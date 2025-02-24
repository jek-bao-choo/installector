#!/usr/bin/env bash
set -e

# Logging helper functions
info() {
    echo "[INFO] $1"
}

error() {
    echo "[ERROR] $1" >&2
}

# Detect system information
OS=$(uname -s | tr '[:upper:]' '[:lower:]')
ARCH=$(uname -m)
PLATFORM="${OS}-${ARCH}"

info "System Detection:"
info "Operating System: ${OS}"
info "Architecture: ${ARCH}"
info "Platform: ${PLATFORM}"

# Check if we're on a supported platform
if [ "${OS}" != "darwin" ] && [ "${OS}" != "linux" ]; then
    error "Unsupported operating system: ${OS}"
    exit 1
fi

# Check if uv is already installed
if command -v uv >/dev/null 2>&1; then
    info "uv is already installed, checking for updates..."
    if uv self update; then
        info "uv has been updated to the latest version"
    else
        info "uv is already at the latest version"
    fi
else
    info "Installing uv..."
    if curl -LsSf https://astral.sh/uv/install.sh | sh; then
        info "uv installed successfully"
    else
        error "Failed to install uv"
        exit 1
    fi
fi

# Verify uv installation
if ! command -v uv >/dev/null 2>&1; then
    error "uv installation verification failed"
    exit 1
fi

UV_VERSION=$(uv --version)
info "uv version ${UV_VERSION} is ready"

# Check if instalar is installed
info "Checking if instalar is installed..."
if uv tool list | grep -q "instalar"; then
    info "instalar is already installed, checking for updates..."
    if uv tool upgrade -i https://test.pypi.org/simple/ instalar; then
        info "instalar has been upgraded successfully"
    else
        info "instalar is already at the latest version"
    fi
else
    info "Installing instalar..."
    if uv tool install -i https://test.pypi.org/simple/ instalar; then
        info "instalar installed successfully"
    else
        error "Failed to install instalar"
        exit 1
    fi
fi

# Verify instalar installation
if ! uv tool list | grep -q "instalar"; then
    error "instalar installation verification failed"
    exit 1
fi

INSTALAR_VERSION=$(uv tool list | grep "instalar" | awk '{print $2}')
info "instalar version ${INSTALAR_VERSION} is ready"

# Start instalar-cli
info "Starting instalar-cli..."
if ! instalar-cli; then
    error "Failed to start instalar-cli"
    exit 1
fi

