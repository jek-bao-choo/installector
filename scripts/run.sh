#!/usr/bin/env bash
set -e

# Logging helper functions
info() {
    echo "[INFO] $1"
}

error() {
    echo "[ERROR] $1" >&2
}

# Determine the operating system (Linux or Darwin/macOS)
OS=$(uname -s | tr '[:upper:]' '[:lower:]')
info "Detected OS: ${OS}"

# Define the uv executable download URL (update with your actual repository info)
UV_URL="https://github.com/AstralProject/uv/releases/latest/download/uv-${OS}-amd64"
UV_BIN="./uv"

# Download uv if not already available
if [ ! -x "${UV_BIN}" ]; then
    info "Downloading uv from ${UV_URL}..."
    curl -L -o "${UV_BIN}" "${UV_URL}"
#    chmod +x "${UV_BIN}"
    info "uv downloaded and made executable."
else
    info "uv is already available."
fi

# Define your package name (as it appears on PyPI)
PACKAGE_NAME="instalar"

# Attempt to install the package from PyPI using uv
info "Attempting to install ${PACKAGE_NAME} from PyPI Test using uv..."
if "${UV_BIN}" install "${PACKAGE_NAME}"; then
    info "${PACKAGE_NAME} installed from PyPI successfully."
else
    info "Installation from PyPI failed. Falling back to GitHub Releases..."

    # Use GitHub API to get the latest release wheel URL
    RELEASE_URL=$(curl -s https://api.github.com/repos/YourUsername/my_cli_tool/releases/latest \
        | grep "browser_download_url.*\.whl" \
        | cut -d '"' -f 4)

    if [ -z "${RELEASE_URL}" ]; then
        error "Could not locate the wheel file in GitHub releases."
        exit 1
    fi

    info "Downloading wheel file from GitHub release: ${RELEASE_URL}"
    curl -L -o "latest.whl" "${RELEASE_URL}"

    info "Installing ${PACKAGE_NAME} from downloaded wheel using uv..."
    "${UV_BIN}" install "latest.whl"
fi

# Start the CLI tool (assumes it is now available in PATH)
info "Starting ${PACKAGE_NAME}..."
exec my_cli_tool "$@"
