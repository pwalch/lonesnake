# lonesnake

![main workflow status](https://github.com/pwalch/lonesnake/actions/workflows/main.yml/badge.svg)

`lonesnake` is a zero-config Bash tool that generates self-contained Python environments with a single command. Each environment fits in a single directory, including a CPython interpreter built from source and a venv. When a capricious environment breaks, you can just delete the directory and generate a new one easily.

It enables you to generate isolated environments not only for projects, but also for global environments or Docker images. It integrates seamlessly with IDEs (VS Code, PyCharm) and dependency management tools (Poetry, pip-tools). It does not impose shell init scripts, so you can activate environments with the method of your choice.

[![asciicast](https://asciinema.org/a/479944.svg)](https://asciinema.org/a/479944)

What are the limitations of `lonesnake`?

- accepts only a single interpreter version per project and per global environment
- supports CPython 3.7+ but not older CPython versions nor alternative interpreters like Pypy
- runs on macOS and Linux, but not Windows
- consumes more disk space than tools that store interpreters in a centralized location

I designed `lonesnake` to be much easier to understand for the average developer than the centralized tools out there. I deliberately renounced many features to keep the code structure simple. But if `lonesnake` is too basic for you, feel free to adopt the well-established [pyenv](https://github.com/pyenv/pyenv) or [asdf](https://github.com/asdf-vm/asdf).

## installation

### macOS installation with Brew

```bash
brew tap pwalch/lonesnake
brew install lonesnake
```

### Linux and manual installation

<details>
<summary>install the CPython build dependencies and <code>curl</code>, depending on your OS</summary>

```bash
# The instructions below are taken from the pyenv Wiki and the python.org dev guide.
# Please check them out if you need more details or if you are using a different OS.
# https://github.com/pyenv/pyenv/wiki#suggested-build-environment
# https://devguide.python.org/setup/#install-dependencies

# Ubuntu/Debian/Mint
sudo apt-get update && sudo apt-get install -y \
  make build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev \
  libsqlite3-dev wget curl llvm libncursesw5-dev xz-utils tk-dev \
  libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev

# Fedora
sudo dnf install \
  curl make gcc zlib-devel bzip2 bzip2-devel readline-devel \
  sqlite sqlite-devel openssl-devel tk-devel libffi-devel xz-devel

# Arch Linux
sudo pacman -S --needed curl base-devel openssl zlib xz

# macOS without Brew
brew install curl openssl readline sqlite3 xz zlib
```

</details>

<details>
<summary>download <code>lonesnake</code> to <code>~/.local/bin</code></summary>

```bash
mkdir -p ~/.local/bin && \
  curl -sL -o ~/.local/bin/lonesnake https://github.com/pwalch/lonesnake/releases/download/0.22.0/lonesnake && \
  chmod u+x ~/.local/bin/lonesnake
```

- make sure you have `export PATH="$HOME/.local/bin:$PATH"` in your `.bashrc` (Bash) or `.zshrc` (ZSH), and open a new shell
- check that the script is accessible with `lonesnake --help`

</details>

## usage

**example commands**

- `lonesnake`
  - generates an environment with the latest CPython version, in the `.lonesnake` directory at the root of the current working directory
- `lonesnake --py 3.11`
  - same, but with the latest patch of CPython 3.11
- `lonesnake --py 3.11.0`
  - same, but with exactly CPython 3.11.0

If the `.lonesnake` directory already exists, `lonesnake` asks for confirmation before deleting it.

## automated activation

### project activation with direnv

To activate a lonesnake environment when entering a project directory, you can bring your own shell auto-load tool. If you are undecided, I recommend [direnv](https://direnv.net/docs/installation.html).

<details>
<summary>install <code>direnv</code> and register its hook</summary>

```bash
# macOS
brew install direnv

# Ubuntu/Debian/Mint
sudo apt-get install direnv

# Fedora
sudo dnf install direnv

# Archlinux
sudo pacman -S direnv
```

- Bash: in your `~/.bashrc`, append `eval "$(direnv hook bash)"`
- ZSH: in your `~/.zshrc`, append `eval "$(direnv hook zsh)"`

</details>

<details>
<summary>generate the project lonesnake environment and enable auto-activation</summary>

- start a new shell then `cd YOUR_PROJECT`
- `lonesnake`
- touch `.envrc` then fill it with this code

```bash
# lonesnake auto-activation for the project directory
lonesnake_dir="${PWD}/.lonesnake"
PATH_add "${lonesnake_dir}/venv/bin"
export VIRTUAL_ENV="${lonesnake_dir}/venv"

# Solve errors involving "Python.h not found" when building
# Python extensions with a lonesnake environment.
parent_include_dir="${lonesnake_dir}/interpreter/usr/local/include"
if [[ -d "$parent_include_dir" ]]; then
  include_dir_name=$(find "$parent_include_dir" \
    -mindepth 1 -maxdepth 1 -type d -name "python3.*" \
    -exec basename {} \;)
  path_add CPATH "${parent_include_dir}/${include_dir_name}"
fi
```

- `direnv allow`
- check that `which python` prints your project's `.lonesnake/venv` directory

> ℹ️ In case of trouble, you can get rid of the lonesnake environment by running `rm -rf .lonesnake .envrc` at the root of your project. Make sure to open a new shell for the change to take effect.

</details>

**Tips**

<details>
<summary>If you find yourself pasting into <code>.envrc</code> files often, automate it with this function for your <code>~/.bashrc</code> or <code>~/.zshrc</code>.</summary>

```bash
# Print direnv activation instructions for lonesnake
# Usage: lonesnake-print-activation >> .envrc
function lonesnake-print-activation() {
cat << EOM
# lonesnake auto-activation for the project directory
lonesnake_dir="\${PWD}/.lonesnake"
PATH_add "\${lonesnake_dir}/venv/bin"
export VIRTUAL_ENV="\${lonesnake_dir}/venv"

# Solve errors involving "Python.h not found" when building
# Python extensions with a lonesnake environment.
parent_include_dir="\${lonesnake_dir}/interpreter/usr/local/include"
if [[ -d "\$parent_include_dir" ]]; then
  include_dir_name=\$(find "\$parent_include_dir" \
    -mindepth 1 -maxdepth 1 -type d -name "python3.*" \
    -exec basename {} \;)
  path_add CPATH "\${parent_include_dir}/\${include_dir_name}"
fi
EOM
}
```

</details>

<details>
<summary>To show a prefix in your shell prompt indicating an active lonesnake venv (e.g. <code>🐍venv-3.11.0</code>), take inspiration from this example code for your <code>~/.bashrc</code> or <code>~/.zshrc</code>.</summary>

```bash
show_lonesnake_venv_prefix () {
  local cpython_path="$PWD/.lonesnake/venv/bin/python"
  # If the venv is activated, print the prompt prefix
  if [[ -x "$cpython_path" ]] && \
      [[ "$(which python)" == "$cpython_path" ]]; then
    local cpython_version="$(python --version | grep -Eo '[0-9]+\.[0-9]+\.[0-9]+')"
    echo "🐍venv-${cpython_version} "
  fi
}
PS1='$(show_lonesnake_venv_prefix)'"$PS1"
```

</details>

### project dependency management

Provided you have configured `direnv` as in the previous section, dependency management tools integrate seamlessly into `lonesnake` venvs.

<details>
<summary>pip-tools</summary>

[pip-tools](https://github.com/jazzband/pip-tools)' sync command installs packages in the current venv. Therefore, all packages are installed in the `.lonesnake` venv directory by default:

- `cd YOUR_PROJECT`
- `pip install pip-tools`
- `pip-sync PINNED_COMPILED_REQUIREMENTS`

</details>

<details>
<summary>Poetry</summary>

You can integrate [Poetry](https://github.com/python-poetry/poetry) into the `.lonesnake` directory by specifying the `POETRY_VIRTUALENVS_PATH` environment variable:

- `cd YOUR_PROJECT` (where your `pyproject.toml` is)
- append the following to your `.envrc`:

```bash
export POETRY_VIRTUALENVS_PATH="${PWD}/.lonesnake/poetry_virtualenvs"
```

- `direnv allow`
- `pip install poetry`
- `poetry install`
- check with `poetry debug` that the "Virtualenv Path" is in a child directory of `.lonesnake/poetry_virtualenvs`

**Tips**

> ℹ️ In case of trouble, you can get rid of the Poetry virtualenvs using `rm -rf .lonesnake/poetry_virtualenvs`. Make sure to open a new shell for the change to take effect.

</details>

### project IDE support

<details>
<summary>Visual Studio Code (VS Code)</summary>

- open a project directory that contains a lonesnake environment at its root
- click `File > Preferences > Settings` and then go to `Workspace` and search for `python.defaultInterpreterPath`
- set this path to `${workspaceFolder}/.lonesnake/venv/bin/python`
- press `CMD/CTRL + SHIFT + P` or click `View > Command Palette`, then choose `Python: Select Interpreter`
- choose `` Use Python from `python.defaultInterpreterPath` setting ``
  - note that after the word `setting`, you should see `./.lonesnake/venv/bin/python`
- when you open the integrated terminal, VS Code should now be sourcing `.lonesnake/venv/bin/activate`

</details>

<details>
<summary>PyCharm</summary>

- open a project directory that contains a lonesnake environment at its root
- click `File > Settings > Project: YOUR_PROJECT > Python Interpreter`
- click `Add Interpreter > Add Local Interpreter...`
- in `Virtualenv Environment`
  - set `Environment` to `Existing`
  - as `Interpreter`, pick `.lonesnake/venv/bin/python` from your project
  - click `OK`
- click `OK`, then wait for the environment to be indexed
- when you create a new `Run/Debug` configuration, the `Python interpreter` field should point to the lonesnake environment

</details>

### user-wide global auto-activation

<details>
<summary>To activate a lonesnake environment user-wide when opening a new shell, you can generate one at the root of your <code>HOME</code> and register it in your <code>.bashrc</code> or <code>.zshrc</code>.</summary>

- `cd ~`
- `lonesnake`
- in your `.bashrc` (Bash) or `.zshrc` (ZSH), append the following:

```bash
# global lonesnake auto-activation
export PATH="${HOME}/.lonesnake/venv/bin:${PATH}"
```

- exit your shell and start a new one
- check that `which python` points to your lonesnake environment

**Tips**

> ℹ️ In case of trouble, you can get rid of the lonesnake environment by removing the export statements from your `.bashrc` or `.zshrc` and running `rm -rf ~/.lonesnake`. Make sure to open a new shell for the change to take effect.

</details>

<details>
<summary>pipx support</summary>

After setting up a global lonesnake environment, you should install `pipx` to manage Python command-line tools. In the same spirit as `lonesnake`, `pipx` installs all tools in isolated venvs so they don't break each other or interfere with the global one. To integrate `pipx`:

- append these lines to your `.bashrc` or `.zshrc`:

```bash
# By default, pipx stores its files in "~/.local/pipx" and "~/.local/bin", but we
# configure it to use sub-directories of the lonesnake global environment:
# "~/.lonesnake/pipx_bin" and "~/.lonesnake/pipx_home". Thanks to this,
# we keep everything related to the global environment in the same place.
export PIPX_HOME="${HOME}/.lonesnake/pipx_home"
export PIPX_BIN_DIR="${HOME}/.lonesnake/pipx_bin"
export PATH="${PIPX_BIN_DIR}:${PATH}"
```

- exit your shell and start a new one
- `pip install pipx`
- from now on, use `pipx install` to install Python CLI tools such as `httpie`

**Tips**

> ℹ️ In case of trouble, you can get rid of your pipx installation by running `rm -rf ~/.lonesnake/pipx_*` and `pip uninstall pipx`. Make sure to open a new shell for the change to take effect.

</details>

## lonesnake environment structure

This `.lonesnake` directory includes a Python interpreter built from [source](https://www.python.org/downloads/source/), as well as a [venv](https://docs.python.org/3/library/venv.html):

- `interpreter` directory includes `usr/local/bin`, `usr/local/include`, etc...
- `venv` directory includes `bin`, `include`, `pyvenv.cfg` etc... It is created by the interpreter above.

Behind the scenes, `lonesnake` takes advantage of cache directories for the CPython source code and build files, located at `~/.cache/lonesnake/X.Y.Z/` where `X.Y.Z` is the Python version (e.g. `3.11.0`). Cache directories enable us to skip the compilation step when CPython was already compiled for the requested version.
