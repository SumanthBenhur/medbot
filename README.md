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

6. Ingest the Knowledge Base
Run the ingestion script as a module so that all relative imports work correctly:
```bash
uv run python -m rag.ingest
```

## Testing the Application

To test the end-to-end backend flow (including the LangGraph interruption for the human-in-the-loop diagnostic center selection), you must run both servers and the `test.py` script.

1. Ensure your `.env` file is set up with `GOOGLE_API_KEY`.
2. Start the Mock Third-Party Booking API (in a new terminal):
   ```bash
   uv run uvicorn third_party.main:app --reload --port 8001
   ```
3. Start the LangGraph Backend Server (in a new terminal):
   ```bash
   uv run uvicorn backend.main:app --reload --port 8000
   ```
4. Run the test script (in a new terminal):
   ```bash
   uv run python test.py
   ```
   You will see the Server-Sent Events stream to the console, demonstrating the agent pausing for human input and then resuming.
