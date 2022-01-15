# lonesnake

`lonesnake` sets up a self-contained Python environment with an interpreter and a venv in single directory. It can be used to create fully isolated Python environments for projects, as well as setting up a global Python environment.

It can be seen as a simpler variant of [pyenv](https://github.com/pyenv/pyenv) for people who do not need to develop against multiple versions of Python simultaneously for the same project.

[![asciicast](https://asciinema.org/a/JaCIWWQaQ3TnZLfRqUB55S2Dl.svg)](https://asciinema.org/a/JaCIWWQaQ3TnZLfRqUB55S2Dl)

What does this tool provide compared to other tools?
* **fully self-contained Python environment**. The environment is contained in a single directory, and includes a fully isolated Python interpreter as well as a venv. It is protected against breaking updates by your package manager or you blowing up your environment in one of your projects.
* **transparent configuration and structure**. No sourcing of slow tool-specific initialization scripts. Auto-activation of venv is enabled with explicit exports.
* **easy venv setup**. No need to learn many new commands to set up a Python virtual environment. Just install `lonesnake` and run it, and you've got your environment. No previous Python interpreter is needed.

What are the limitations of this tool?
* supports installing only a single Python interpreter version at a time for a specific project
  * if you need to support multiple versions simultaneously with a fallback order, use [pyenv](https://github.com/pyenv/pyenv) or [asdf](https://github.com/asdf-vm/asdf).
* supports only CPython 3.7+, older CPython versions and other Python interpreters (e.g. PyPy) are not supported
* supports only macOS and Linux
* consumes more disk space than tools that keep a single version of the Python interpreter in `$HOME` (pyenv, asdf), as the interpreter is copied to every project

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

# macOS
brew install curl openssl readline sqlite3 xz zlib

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
```

</details>


<details>
<summary>download <code>lonesnake</code> to <code>~/.local/bin</code> or some other directory in your <code>PATH</code></summary>

```bash
mkdir -p ~/.local/bin && \
  curl -sL -o ~/.local/bin/lonesnake https://github.com/pwalch/lonesnake/releases/download/0.5.1/lonesnake && \
  chmod u+x ~/.local/bin/lonesnake
```

* make sure you have `export PATH="$HOME/.local/bin:$PATH"` in your `.bashrc` (Bash) or `.zshrc` (ZSH)
* check that the script is accessible with `lonesnake --help`

</details>

## usage

**example commands**

* `lonesnake`
  * creates an environment with the most recent CPython version
* `lonesnake --version 3.10`
  * creates an environment with the latest patch of CPython 3.10
* `lonesnake --version 3.9.9`
  * creates an environment with CPython 3.9.9

## automated activation

In most cases, you don't want to activate your Python environment with `source` every time you enter your project directory or use a Python command-line tool. Instead, you want it to auto-activate.

### local environment auto-activation with direnv

If you want to activate the environment automatically when you enter a project directory, you can use [direnv](https://direnv.net/docs/installation.html):

<details>
<summary>install <code>direnv</code> with your package manager</summary>

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

</details>

<details>
<summary>register the direnv hook in your shell</summary>

* Bash: in your `~/.bashrc`, append `eval "$(direnv hook bash)"` 
* ZSH: in your `~/.zshrc`, append `eval "$(direnv hook zsh)"`

</details>

Once direnv is set up, install a standalone environment in your project and have it auto-activate:

* start a new shell
* `cd YOUR_PROJECT`
* `lonesnake` (pass a `--version` if needed, see `--help`)
* `touch .envrc` and fill it with this:

```bash
# lonesnake auto-activation for the project directory
export PATH="${PWD}/.lonesnake/venv/bin:${PATH}"
```

* `direnv allow`
* check that `which python` points to your project's standalone environment
  * if yes, auto-activation is properly enabled!

> ℹ️ In case of trouble, you can get rid of the environment by running `rm -rf .lonesnake .envrc` at the root of your project.

**Poetry support**

To manage your project dependencies, you might be using [Poetry](https://github.com/python-poetry/poetry). Poetry can be integrated into the `lonesnake` directory as follows:
* `cd YOUR_PROJECT`
* append the following to `.envrc`:

```bash
export POETRY_VIRTUALENVS_PATH="${PWD}/.lonesnake/poetry_virtualenvs"
```

* `direnv allow`
* `pip install poetry`
* check with `poetry debug` that the "Virtualenv Path" of Poetry is located in a child directory of `.lonesnake/poetry_virtualenvs`
  * if yes, Poetry is properly configured to use the `lonesnake` environment.

> ℹ️ In case of trouble, you can get rid of the Poetry virtualenvs using `rm -rf .lonesnake/poetry_virtualenvs`.

### global environment auto-activation for a user

If you intended to use your standalone environment as a global Python environment for your user, you want it to activate automatically when you start a new shell:

* `cd ~`
* `lonesnake`
* in your `.bashrc` (Bash) or `.zshrc` (ZSH), append the following:

```bash
# global lonesnake auto-activation
export PATH="${HOME}/.lonesnake/venv/bin:${PATH}"
```

* exit your shell and start a new one
* check that `which python` points to your standalone environment
  * if yes, auto-activation is properly enabled!

> ℹ️ In case of trouble, you can get rid of the environment by removing the export statements from your `.bashrc` or `.zshrc` and running `rm -rf ~/.lonesnake`.

**pipx support**

After setting up a global standalone environment, it is recommended to install `pipx` to manage Python command-line tools. Indeed, `pipx` installs all tools in isolated venvs so they don't break each other or interfere with the global environment. To install `pipx`, do the following:

* append these lines to your `.bashrc` or `.zshrc`:

```bash
# By default, pipx stores its files in "~/.local/pipx" and "~/.local/bin", but we
# configure it to use sub-directories of the standalone environment:
# "~/.lonesnake/pipx_bin" and "~/.lonesnake/pipx_home". Thanks to this,
# we keep everything related to the global environment in the same place.
export PIPX_HOME="${HOME}/.lonesnake/pipx_home"
export PIPX_BIN_DIR="${HOME}/.lonesnake/pipx_bin"
export PATH="${PIPX_BIN_DIR}:$PATH"
```

* exit your shell and start a new one
* `pip install pipx`
* from now on, use `pipx install` to install Python CLI tools such as `httpie`

> ℹ️ In case of trouble, you can get rid of your pipx installation by running `rm -rf ~/.lonesnake/pipx_*` and `pip uninstall pipx`.

## standalone environment structure

This standalone environment directory includes a Python interpreter built from [source](https://www.python.org/downloads/source/), as well as a [venv](https://docs.python.org/3/library/venv.html). That is, the content of the `.lonesnake` directory is the following:
* `interpreter` interpreter directory includes `bin`, `include`, etc...
* `venv` venv directory includes `bin`, `include`, `pyvenv.cfg` etc... It is created by the interpreter above.

Behind the scenes, `lonesnake` takes advantage of cache directories for the CPython source code and build files, located at `~/.cache/lonesnake/X.Y.Z/` where `X.Y.Z` is the Python version (e.g. `3.10.1`). These cache directories enable us to skip the compilation step when the CPython code was already compiled in the past for the requested version.
