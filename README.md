# Installector
Installector is AI assistant for installing agent collectors in your terminal.

## Project Structure
```
installector/
├── .github/                    # GitHub Actions workflows, issue templates, etc.
├── src/
│   └── instalar/             # Your Python package code
│       ├── client/
│       ├── server/
│       ├── __init__.py
│       └── main.py
├── tests/                      # Your test suite
│   └── test_main.py
├── scripts/                    # Distribution helper scripts (e.g. run.sh)
│   └── run.sh                 # Script that installs the wheel using uv for MacOS and Linux. Verify that the uv executable (from your /bin folder) is available, install the wheel using the uv executable.
│   └── run.ps1                 # Script that installs the wheel using uv for Windows
├── bin/                        # Additional executables you want to distribute. Excluded from committing to git.
│   └── uv                     # The uv executable (from Astral). Although the uv executable and run.sh are not part of the Python package per se, they are essential for your distribution. Keep these files in your repository but do not include them in the wheel. Instead, they will be distributed as release assets alongside the wheel.
│   └── ollama-darwin-v0.5.12/  # The ollama for macOS manually downloaded (ollama-darwin.tgz) from https://github.com/ollama/ollama/releases and suffix with version tag
│       ├── ...
│       └── ollama              # Ollama executable
├── pyproject.toml              # Modern build configuration. Create a Git tag for your release. This tag should correspond to your version in pyproject.toml.
├── README.md
├── .gitignore                  # Make sure /dist is ignored in version control
└── dist/                      # Build artifacts (wheel file, etc.)
```

## Initial Llama.cpp setup

* Download the model from HuggingFace in GGUF format. For example, I like Unsloth's https://huggingface.co/collections/unsloth/deepseek-r1-all-versions-678e1c48f5d2fce87892ace5
  * Put the downloaded model into folder /models
  * optional: Read about GGUF part 1 https://huggingface.co/docs/hub/en/gguf 
  * optional: Read about GGUF part 2https://github.com/ggml-org/ggml/blob/master/docs/gguf.md
  * 
* Download llama.cpp pre-built binaries from Github release https://github.com/ggml-org/llama.cpp/releases
  * Read about llama.cpp's llama-server from https://github.com/ggml-org/llama.cpp/tree/master/examples/server
  * Unzip the content and execute it

```bash
# First terminal - start the llama-server
./llama-server -m models/7B/ggml-model.gguf -c 2048

# Second terminal - test the llama-server
curl --request POST \     
    --url http://localhost:8080/completion \
    --header "Content-Type: application/json" \
    --data '{"prompt": "Why is the sky blue?","n_predict": 128}'
```

## Initial project setup
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

# Only if it has been published to PyPI Test
uv tool run -i https://test.pypi.org/simple/ --from instalar instalar-cli 
```

## Lint
```bash
uvx ruff check   # Lint all files in the current directory.
uvx ruff format  # Format all files in the current directory.
```

## Build
```bash
# uv remove actually cleans up your repo correctly.

# Clear cache to optimise storage
uv cache clean

rm -rf dist

# uv build create a .whl package out of your project, but uv doesn't require your project to be able to be built.
# Wheel only
uv build --wheel

# Wheel and tar.gz
uv build
```

## Publish (optional)
```bash
uvx twine upload --repository testpypi dist/*

# uv publish...
```

## Install
```bash
# Change the version accordingly
# Install Instalar from wheel
uv tool install dist/instalar-0.0.1-py3-none-any.whl

# See if Instalar is installed
uv tool list

# Step 3: Use Instalar
instalar-cli
```

## Test run.sh
```
......scripts/run.sh | sh
```

## Upgrade
```bash
# uv lock --upgrade-package <package>==<version> let you upgrade carefully your packages one version at a time.
```

## Build automation
```bash
# Use GitHub Actions to trigger a workflow on tag creation.
# The workflow should build your package (generating the wheel file in /dist), and then collect the artifacts (wheel file, run.sh, and uv executable) as assets.
# Do not commit build artifacts (like the wheel) to your repository. Instead, attach them as assets to your GitHub release.
# Ensure your release notes describe how to use the run.sh script to perform the installation and mention any prerequisites (e.g., needing execution permissions for uv).
# attach the wheel file, run.sh, and the uv executable as release assets.
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

## Decision

### llama-cpp-python vs. llama.cpp's llama-server vs. ollama
- Though llama-cpp-python is not actively maintained, it is a straightforward to POC this app.
- llama.cpp's llama-server is my preferred approach but it takes a bit more time to POC this app.
- ollama has huge download size.
For now, I am using llama-cpp-python to move fast. 

## TODO
- Add llama-cpp-python to llm.py.
- Add memory. Reference how others do it. KISS. Mem0?
- Understand how to resolve the dependencies issue of PyPI when missing. Or can we build the dependencies on build to have certainty?
- Add supported version to the prompt and out of support message of we notify.
- Think about repomix and docling for RAG. KISS.


