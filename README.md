# standalone-venv

`standalone-venv` is a tool to easily set up a self-contained Python environment with an interpreter and a venv in a `.standalone-venv` directory. It can be used to set up an isolated Python environment for a project, or a global Python environment for a user.

[![asciicast](https://asciinema.org/a/455461.svg)](https://asciinema.org/a/455461)

What does this tool provide compared to other tools?
* **fully self-contained Python environment**. The environment is contained in a single directory, and includes a fully isolated Python interpreter and an associated venv. As the environment has its own full-blown Python interpreter, it is protected against breaking updates by your package manager (brew) or you blowing up your environment in one of your projects. You can get rid of your environment simply by removing the `.standalone-venv` directory.
* **transparent configuration**. No sourcing of tool-specific initialization scripts. Auto-activation of venv can be enabled with a few explicit environment variable exports.
* **easy venv setup**. No long list of steps to follow to set up a virtualenv. Install the dependencies, download the Bash script somewhere on your `$PATH`, then run it and you've got your environment. Doesn't assume the existence of a working Python interpreter.

What are the limitations of this tool?
* supports installing only a single Python interpreter at a time for a project. It does not support installing multiple Python interpreters with different versions for the same project.
  * This can be a problem for you if you are the author of a library that supports multiple versions of Python. If it is the case, it is recommended to use [pyenv](https://github.com/pyenv/pyenv) or [asdf](https://github.com/asdf-vm/asdf).
* supports only Python 3.7+, older versions are not supported.
* consumes more disk space than tools that keep a single version of the Python interpreter in `$HOME` (pyenv, asdf), as the interpreter is copied to every project (300 MB).

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
  * `curl -sL -o ~/.local/bin/standalone-venv https://github.com/pwalch/standalone-venv/releases/download/0.0.3/standalone-venv`
  * `chmod u+x ~/.local/bin/standalone-venv`
* check that the script is accessible by running `standalone-venv --help`

## usage

**help message**

```
Usage: standalone-venv [--cpython-version VERSION]

Creates a standalone Python environment in a new directory named 
'.standalone-venv' inside your working directory. This environment includes
a CPython interpreter built from source and a venv created with that
interpreter.
The source and build files are cached in '/home/pierre/.cache/standalone-venv'.

OPTIONS
  --cpython-version VERSION
       pass a version number to install the CPython interpreter
       version of your choice. By default, the version 3.10.1
       is installed. Versions before Python 3.7 are not supported.
       That is, Python 2.7.X and 3.6.X are not supported.
       You can find the list of all Python releases on this page:
       https://www.python.org/downloads/

DEPENDENCIES
  📝 Make sure you have installed all the dependencies that are necessary
     to compile the CPython interpreter. Check out the docs for more details
     about how to do it for your OS.
```

**example commands**

* `standalone-venv`
  * default interpreter version (see `--help`) + empty venv
* `standalone-venv --version 3.9.9`
  * Python 3.9.9 interpreter + empty venv

**example output**

```
➜ standalone-venv
We are going to install a standalone Python environment in directory
.standalone-venv, which will include the CPython 3.10.1 interpreter
as well as a venv based on this interpreter.

CPYTHON INTERPRETER COMPILATION & INSTALLATION
➖ Looking for a previous build of CPython 3.10.1 interpreter in
the cache at '/home/pierre/.cache/standalone-venv/3.10.1'...
  ℹ️  No previous build of CPython 3.10.1 was found in the cache, so we are going to download its source code from 'python.org' and compile it.
➖ Downloading Python interpreter source code from 'https://www.python.org/ftp/python/3.10.1/Python-3.10.1.tgz'...
  ✅ downloaded Python interpreter to '/home/pierre/.cache/standalone-venv/3.10.1'.
➖ Running './configure' in Python interpreter source code directory '/home/pierre/.cache/standalone-venv/3.10.1'...
  ✅ ran './configure' in 16s, ready to compile interpreter.
➖ Compiling Python interpreter with 'make -j'...
  ✅ compiled Python interpreter in 32s.
➖ Installing Python interpreter to '.standalone-venv/interpreter'...
  ✅ installed Python interpreter in 11s.
➖ Verifying that the interpreter located at '.standalone-venv/interpreter/bin/python3.10' runs and returns the expected version...
  ✅ ran 'python --version' using the interpreter we just compiled. It returned 'Python 3.10.1' as expected.

VENV INSTALLATION
➖ Creating a Python venv at '.standalone-venv/venv' using the interpreter we built...
  ✅ created Python venv
➖ Upgrading Pip and setuptools inside venv using '.standalone-venv/venv/bin/pip'...
  ✅ upgraded Pip inside venv
➖ Installing complimentary Python packages (wheel) inside venv...
  ✅ installed complimentary packages inside venv

SUMMARY
The Python standalone environment has been installed successfully in
'.standalone-venv'! (💽 343M)
You can find the interpreter in '.standalone-venv/interpreter'
and the venv in '.standalone-venv/venv'.

ACTIVATION INSTRUCTIONS
You can activate your environment with the following command:
  source .standalone-venv/venv/bin/activate

💡 Please note that there are solutions in the documentation to automatically
activate the venv.
```

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

This section describes the structure of the standalone environment directory.

This standalone environment includes a Python interpreter built from [source](https://www.python.org/downloads/source/), as well as a [venv](https://docs.python.org/3/library/venv.html). That is, the content of the `.standalone-venv` directory is the following:
* `interpreter` interpreter directory including `bin`, `include`, etc...
* `venv` venv directory including `bin`, `include`, `pyvenv.cfg` etc... It is created by the interpreter above.

Behind the scenes, `standalone-venv` takes advantage of cache directories for the CPython source code and build files, located at `~/.cache/standalone-venv/X.Y.Z/` where `X.Y.Z` is the Python version (e.g. `3.10.1`). These cache directories enable us to skip the compilation step when the CPython code was already compiled in the past for the requested version.
