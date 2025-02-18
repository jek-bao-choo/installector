# Installector
Installector is AI assistant for installing agent collectors in your terminal.

# Initial setup
```bash
uv init installector

cd installector
```

# Log in
```bash
cd installector

uv tree

uv sync

source .venv/bin/activate

# inside /installector directory but outside of /server directory.
python -m server

python -m client.console
```

# Log out
```bash
deactivate  
```

todo:


3. think about distributing it using uv.
3. It needs memory for the simple workflow. reference how aider manages memory.
4. think about how to use llama.cpp or ollama with this

