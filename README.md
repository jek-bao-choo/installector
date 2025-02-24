# Installector
Installector is AI assistant for installing agent collectors in your terminal.

## Initial setup
```bash
# uv init not only create a ".venv", but also a pyproject.toml, a git repo (with Python-specific .gitignore), a README.md and a hello.py by default. 
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

## Add dependencies
```
# You can declare your root dependencies in pyproject.toml or add them with uv add.
```

## Run
```bash
# uv run will run any command in the venv, even if it's not activated. You don't even need to know there is a venv, or what activation means.
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
# uv remove actually cleans up your repo correctly.
uv remove

uv cache clean

# uv build create a .whl package out of your project, but uv doesn't require your project to be able to be built.
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

## Upgrade
```bash
# uv lock --upgrade-package <package>==<version> let you upgrade carefully your packages one version at a time.
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

## Consideration
- Usage in air gapped environment

## TODO
- try distributing it with uv such that run.sh but where to put run.sh in this project? KISS
- think about how to use llama.cpp or ollama with this whichever lite KISS
- Add memory. Reference how others do it. KISS
- Add supported version to the prompt and out of support message of we notify.


