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
source .venv/bin/activate

# inside /installector directory but outside of /server directory.
python -m server
python -m client.console
```

## Log out
```bash
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

