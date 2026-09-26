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

4. Configure Environment Variables
Create your local `.env` file from `.env.example`:
```bash
cp .env.example .env
```
Open `.env` and set your `GOOGLE_API_KEY` (you can generate an API key at [Google AI Studio](https://aistudio.google.com/)):
```env
GOOGLE_API_KEY=your_google_api_key_here
```
> **Note**: `GOOGLE_API_KEY` is required by the FastAPI backend and LangGraph agent to generate reasoning tokens, answer test preparation questions, and execute tool calls.

5. Install pre-commit hooks
```bash
uvx pre-commit install
```

6. How to add new deps: Always use `uv add` to add new dependencies. Do not use any direct `pip install`. Let uv do the dependency management for us!

7. Ingest the Knowledge Base
Run the ingestion script as a module so that all relative imports work correctly:
```bash
uv run python -m rag.ingest
```

## Running the Application

Ensure your `.env` file is configured with your `GOOGLE_API_KEY` and the knowledge base has been ingested.

---

### Option 1: Run Everything Together (Recommended)

You can start all three services (Mock Booking API, FastAPI Backend, and Streamlit Frontend) simultaneously using the provided startup script:

```bash
./run.sh
```
*(or `bash run.sh`)*

Pressing `Ctrl+C` will cleanly terminate all running background processes.

---

### Option 2: Run Services Individually (Separate Terminals)

If you prefer running services in separate terminal windows/tabs for independent logging and debugging:

1. **Terminal 1: Mock Third-Party Booking API** (Port 8001)
   ```bash
   uv run uvicorn third_party.main:app --reload --port 8001
   ```

2. **Terminal 2: LangGraph FastAPI Backend** (Port 8000)
   ```bash
   uv run uvicorn backend.main:app --reload --port 8000
   ```

3. **Terminal 3: Streamlit Frontend UI** (Port 8501)
   ```bash
   uv run streamlit run frontend/app.py
   ```

---

## Service Endpoints & URLs

| Service | Port | URL | Description |
| :--- | :--- | :--- | :--- |
| **Streamlit UI** | `8501` | [http://localhost:8501](http://localhost:8501) | Main chat user interface |
| **FastAPI Backend** | `8000` | [http://localhost:8000](http://localhost:8000) | LangGraph agent & SSE `/chat` endpoint ([API Docs](http://localhost:8000/docs)) |
| **Mock Booking API** | `8001` | [http://localhost:8001](http://localhost:8001) | External scheduling service ([API Docs](http://localhost:8001/docs)) |

---

## Testing via CLI

You can also run the automated end-to-end CLI test script:
```bash
uv run python test.py
```
This tests the full Server-Sent Events (SSE) streaming flow, LangGraph interruption, and graph resumption with center selection.
