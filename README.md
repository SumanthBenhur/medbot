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

## Running the Full Application

To run the complete system (Mock Booking API, FastAPI backend, and Streamlit frontend):

1. **Ensure your `.env` file is configured** with your `GOOGLE_API_KEY`.
2. **Ingest the Knowledge Base** (one-time setup):
   ```bash
   uv run python -m rag.ingest
   ```
3. **Start the Mock Third-Party Booking API** (Terminal 1):
   ```bash
   uv run uvicorn third_party.main:app --reload --port 8001
   ```
4. **Start the LangGraph FastAPI Backend** (Terminal 2):
   ```bash
   uv run uvicorn backend.main:app --reload --port 8000
   ```
5. **Start the Streamlit Frontend UI** (Terminal 3):
   ```bash
   uv run streamlit run frontend/app.py
   ```

Open your browser to `http://localhost:8501` to interact with Medbot.

## Testing via CLI

You can also run the automated end-to-end CLI test script:
```bash
uv run python test.py
```
This tests the full Server-Sent Events (SSE) streaming flow, LangGraph interruption, and graph resumption with center selection.
