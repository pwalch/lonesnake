#!/usr/bin/env bash

# Copyright (C) 2021-2023 Pierre Walch
# This code is licensed under the GNU GPL, see the LICENSE file.
# https://github.com/pwalch/lonesnake/

set -euo pipefail

PROG_NAME="$(basename "$0")"
readonly PROG_VERSION="0.27.0"

readonly LOCAL_BIN_DIR="${HOME}/.local/bin"

# Color markers
readonly CLR_BOLD="\033[1m"  # bold
readonly CLR_UDL="\033[4m"  # underline
readonly CLR_RED="\033[31m"  # red
readonly CLR_BGR="\033[2m"  # background
readonly CLR_ITL="\033[3m"  # italic
readonly CLR_END="\033[0m"  # end-marker

function error_out() {
    echo -e "${CLR_RED}[ERROR] $*${CLR_END}" >&2
    exit 1
}

function usage() {
echo -e "${CLR_BOLD}${PROG_NAME}${CLR_END}
  Usage: ${CLR_BOLD}${PROG_NAME}${CLR_END} ${CLR_BOLD}[--help]${CLR_END}

  Installs the dependencies of lonesnake depending on OS,
  then installs lonesnake in '${LOCAL_BIN_DIR}'.
  If '${LOCAL_BIN_DIR}' is not in PATH, the
  installation is aborted."
}

if [[ "$#" -eq 1 ]]; then
    if [[ "$1" == "-h" ]] || [[ "$1" == "--help" ]]; then
        usage
        exit 1
    fi
fi

if [ "$(id -u)" -eq 0 ]; then
    error_out "You are root, please re-run as a regular user."
fi

if [[ ":$PATH:" != *":${LOCAL_BIN_DIR}:"* ]]; then
    error_out "Directory '${LOCAL_BIN_DIR}' where lonesnake will be installed is not" \
        "in PATH, please add it and re-try."
fi

if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "➖ Installing dependencies of lonesnake..."
    if command -v apt-get &> /dev/null; then
        echo "Detected Debian. You might be prompted for your password..."
        if ! sudo apt-get update && ! \
            sudo DEBIAN_FRONTEND=noninteractive apt-get install -y \
            make build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev \
            libsqlite3-dev wget curl llvm libncursesw5-dev xz-utils tk-dev \
            libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev; then
            error_out "Could not install dependencies for Debian"
        fi
    elif command -v dnf &> /dev/null; then
        echo "Detected Fedora. You might be prompted for your password..."
        if ! sudo dnf install \
            curl make gcc zlib-devel bzip2 bzip2-devel readline-devel \
            sqlite sqlite-devel openssl-devel tk-devel libffi-devel xz-devel; then
            error_out "Could not install dependencies for Fedora"
        fi
    elif command -v pacman &> /dev/null; then
        echo "Detected Arch. You might be prompted for your password..."
        if ! sudo pacman -S --needed curl base-devel openssl zlib xz; then
            error_out "Could not install dependencies for Arch"
        fi
    else
        error_out "Unsupported Linux distribution: ${OSTYPE}"
    fi
    echo "  ✅ installed dependencies"

    echo "➖ Installing lonesnake in '${LOCAL_BIN_DIR}'..."
    mkdir -p ~/.local/bin && \
        curl -sL -o ~/.local/bin/lonesnake https://github.com/pwalch/lonesnake/releases/download/${PROG_VERSION}/lonesnake && \
        chmod u+x ~/.local/bin/lonesnake
    echo "  ✅ installed lonesnake"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    echo "Detected macOS."
    echo "➖ Configuring Brew tap..."
    brew tap pwalch/lonesnake
    echo "  ✅ configured Brew tap"
    echo "➖ Installing lonesnake..."
    brew install lonesnake
    echo "  ✅ installed lonesnake"
else
    error_out "Unsupported operating system: $OSTYPE"
    exit 1
fi
