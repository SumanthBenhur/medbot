# medbot
AI Assistant for medical appointments and enquiries

## Setting up

1. Clone the repo
```bash
git clone https://github.com/SumanthBenhur/medbot.git
```

2. Get the virtual environment
```bash
uv sync
```

3. Activate the virtual environment
```bash
source .venv/bin/activate
```

4. Install pre-commit hooks
```bash
uvx pre-commit install
```

5. How to add new deps: Always use `uv add` to add new dependencies. Do not use any direct `pip install`. Let uv do the dependency management for us!
