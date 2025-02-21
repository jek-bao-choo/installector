# Installector
Installector is AI assistant for installing agent collectors in your terminal.

## Initial setup
```bash
uv init installector
cd installector
```

## Log in
```bash
cd installector
uv tree
uv sync

# optional
source .venv/bin/activate
```

## Run
```bash
# inside /installector directory but outside of /src directory.
# For dev
uv run -m instalar

# for Dev
uv run src/instalar/__main__.py

# Only if it has been published to PyPI
uv tool run -i https://test.pypi.org/simple/ --from instalar instalar-cli 
```

## Build
```bash
# Wheel only
uv build --wheel

# Wheel and tar.gz
uv build
```

## Publish (optional)
```bash
uvx twine upload --repository testpypi dist/* `

# uv publish...
```

## Install
```bash
# Change the version accordingly
# Install Instalar from wheel
uv tool install dist/example_package_jekbao-0.0.1-py3-none-any.whl

# See if Instalar is installed
uv tool list

# Step 3: Use Instalar
instalar-cli
```

## Clean up or log out
```bash
uv tool list

uv tool uninstall instalar

rm -rf dist

deactivate  
```

## Features
- Interactive terminal interface
- AI-powered installation guidance
- Support for multiple observability vendors
- Cross-platform compatibility (Linux, macOS, Windows)
- System environment detection
- Step-by-step verification

## License
This project is licensed under the GNU General Public License v3.0 - see the LICENSE file for details.

---

# Dev
## Reminder
- Do not attempt to automate packaging, build, and deployment i.e. CICD yet. KISS
- POC so keep is simple!

## TODO
- try distributing it with uv such that run.sh but where to put run.sh in this project? KISS
- think about how to use llama.cpp or ollama with this whichever lite KISS
- Add memory. Reference how others do it. KISS
- Add supported version to the prompt and out of support message of we notify.

