# standalone-venv

`standalone-venv` is a tool to easily set up a self-contained Python environment with an interpreter and a venv in a `.standalone-venv` directory. It can be used to set up isolated Python environments for projects, as well as a global Python environment.

[![asciicast](https://asciinema.org/a/455461.svg)](https://asciinema.org/a/455461)

What does this tool provide compared to other tools?
* **fully self-contained Python environment**. The environment is contained in a single directory, and includes a fully isolated Python interpreter and an associated venv. As the environment has its own full-blown Python interpreter, it is protected against breaking updates by your package manager (brew) or you blowing up your environment in one of your projects.
* **transparent configuration and structure**. No sourcing of tool-specific initialization scripts. Auto-activation of venv can be enabled with a few explicit environment variable exports. You can get rid of your environment simply by removing the `.standalone-venv` directory.
* **easy venv setup**. No need to learn many new commands to set up a Python virtual environment. Just install `standalone-venv` and run it, and you've got your environment. No previous Python interpreter is needed.

What are the limitations of this tool?
* supports installing only a single Python interpreter at a time for a project. It does not support installing multiple Python interpreters with different versions for the same project.
  * This can be a problem for you if you are the author of a library that supports multiple versions of Python. If it is the case, it is recommended to use [pyenv](https://github.com/pyenv/pyenv) or [asdf](https://github.com/asdf-vm/asdf).
* supports only CPython 3.7+, other interpreters and older versions are not supported.
* consumes more disk space than tools that keep a single version of the Python interpreter in `$HOME` (pyenv, asdf), as the interpreter is copied to every project (100s of MBs).

## installation

### macOS installation with Brew

* `brew tap pwalch/standalone-venv`
* `brew install standalone-venv`

### Manual installation

* install the CPython build dependencies and `curl` depending on your OS. The instructions below are taken from the [pyenv Wiki](https://github.com/pyenv/pyenv/wiki#suggested-build-environment) and the [python.org dev guide](https://devguide.python.org/setup/#install-dependencies):
  * macOS
    ```bash
    brew install curl openssl readline sqlite3 xz zlib
    ```
  * Ubuntu/Debian/Mint
    ```bash
    sudo apt-get update && sudo apt-get install -y \
      curl make build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev \
      libsqlite3-dev wget curl llvm libncursesw5-dev xz-utils tk-dev \
      libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev
    ```
  * Fedora
    ```bash
    sudo dnf install curl make gcc zlib-devel bzip2 bzip2-devel readline-devel \
      sqlite sqlite-devel openssl-devel tk-devel libffi-devel xz-devel
    ```
  * Arch Linux
    ```bash
    sudo pacman -S --needed curl base-devel openssl zlib xz
    ```
* download the `standalone-venv` Bash script to a directory in your `$PATH`. You can put it anywhere, but here are some instructions to download it to `~/.local/bin`:
  * `mkdir -p ~/.local/bin`
  * make sure you have `export PATH="$HOME/.local/bin:$PATH"` in your interactive shell start-up script (e.g. `.bashrc` or `.zshrc`)
  * `curl -sL -o ~/.local/bin/standalone-venv https://github.com/pwalch/standalone-venv/releases/download/0.3.0/standalone-venv`
  * `chmod u+x ~/.local/bin/standalone-venv`
* check that the script is accessible by running `standalone-venv --help`

## usage

**example commands**

* `standalone-venv`
  * default interpreter version (see `--help`) + empty venv
* `standalone-venv --version 3.9.9`
  * Python 3.9.9 interpreter + empty venv

## automated activation

In most cases, you don't want to activate your Python environment manually every time you enter your project directory or use a Python command-line tool. Instead, you want to rely on your computer to do it for you.

There are two main auto-activation use cases for which we provide recommendations:
* local environment for a project, where the environment activates when entering the project directory
* global environment for a user, where the environment activates when you opening the shell

### local environment auto-activation with direnv

If you want to activate the environment automatically when you enter your project directory, this section is for you.

* install `direnv` by following its installation [instructions](https://direnv.net/docs/installation.html)
  * includes installing a package and adding a hook in your `.bashrc` or `.zshrc`
* create an `.envrc` file at the root of your project directory with this content:

```bash
# direnv doesn't support updating the prompt, so we disable the venv prompt
export VIRTUAL_ENV_DISABLE_PROMPT=1
export PATH="$PWD/${VENV_REL_DIR}/bin:$PATH"
export VIRTUAL_ENV="$PWD/${VENV_REL_DIR}"
```

* allow direnv to load your `.envrc` using `direnv allow .`

After this, direnv will automatically activate the venv whenever you enter your project directory, and deactivate it when you leave it.

### global environment auto-activation for a user

If you intended to use your standalone environment as a global Python environment for your user, this section is for you. We will explain how to create such an environment and how to make sure it is activated automatically when you start a new shell.

* enter your home directory
  * `cd ~`
* create a standalone venv
  * `standalone-venv`
* append the following lines to your interactive shell start-up script (`.bashrc` or `.zshrc`):

```bash
# the venv prompt would always be visible for global environments, so we disable it 
export VIRTUAL_ENV_DISABLE_PROMPT=1
export PATH="$HOME/.standalone-venv/venv/bin:$PATH"
export VIRTUAL_ENV="$HOME/.standalone-venv/venv"
```

* exit your shell and start a new one
* check that `which python` points to your standalone environment

Your global environment is now set up. If you run into any issue, you can get rid of the environment by removing the export statements from your interactive shell start-up script and removing `$HOME/.standalone-venv`.

**pipx support**

When using a global environment, it is recommended to install `pipx` to manage Python command-line tools. Indeed, it installs all tools in isolated venvs so they don't break each other or the global environment. By default, pipx stores its files in `~/.local/pipx` and `~/.local/bin`, but we can configure it to use sub-directories of the standalone environment to keep everything related to the global environment in the same place.

* append the following lines to your interactive shell start-up script (`.bashrc` or `.zshrc`):

```bash
export PIPX_HOME="$HOME/.standalone-venv/pipx_home"
export PIPX_BIN_DIR="$HOME/.standalone-venv/pipx_bin"
export PATH="$PIPX_BIN_DIR:$PATH"
```

* exit your shell and start a new one
* `pip install pipx`

Thanks to the environment variables set above, pipx will install all the tools in your standalone environment directory, in `~/.standalone-venv/pipx_bin` and `~/.standalone-venv/pipx_home`. In case you run into any issue, you can get rid of your pipx installation by removing the export statements from your shell start-up script and removing these two pipx-related directories.

## standalone environment structure

This standalone environment directory includes a Python interpreter built from [source](https://www.python.org/downloads/source/), as well as a [venv](https://docs.python.org/3/library/venv.html). That is, the content of the `.standalone-venv` directory is the following:
* `interpreter` interpreter directory including `bin`, `include`, etc...
* `venv` venv directory including `bin`, `include`, `pyvenv.cfg` etc... It is created by the interpreter above.

Behind the scenes, `standalone-venv` takes advantage of cache directories for the CPython source code and build files, located at `~/.cache/standalone-venv/X.Y.Z/` where `X.Y.Z` is the Python version (e.g. `3.10.1`). These cache directories enable us to skip the compilation step when the CPython code was already compiled in the past for the requested version.
