# Medbot Project Guidelines

## Project Overview
Medbot answers patient questions about test preparation guidelines (e.g., fasting rules, test duration) and schedules specialized diagnostic tests.

## Tech Stack
- **Backend**: FastAPI
- **Agent Orchestration**: LangGraph, LangChain
- **Frontend**: Streamlit
- **UI Protocol**: AGUI protocol

## Core Agent Tools
1. **Retriever Tool**: Scans test preparation protocols, clinical contraindications, and insurance coverage requirements.
2. **External API Tool**: Lab appointment scheduling API.
   - **Behavior**: Requires the user's preferred diagnosis center and desired booking time.
   - **Output Handling**: Upon gathering these, the tool returns a confirmation string verbatim to the user: *"Booking confirmed at `<center_name>` at `<time>`"*. This tool output MUST bypass the main assistant and be streamed/displayed directly to the user.
   - **Assistant Role**: The main assistant should merely state, *"Bookings are handled by an external API, redirecting you now..."*, and then let the tool output the final confirmation.

## Chatbot & UI Behavior
- **Streaming**: Responses from the chatbot must be streamed in real-time to the frontend.
- **Reasoning Tokens**: The UI must be capable of displaying the LLM's reasoning (thought) tokens to the user as they are generated.

## Non-Prompt Inputs (Privacy & Preferences)
To respect data privacy and UI boundaries, the following inputs are handled outside the main LLM prompt context:
1. **Dropdown Box**: Preferred Physical Diagnostic Center / Branch Location (`["Downtown Medical Plaza", "Westside Imaging Lab", "Metro Central Annex"]`).
2. **Text Box**: Patient National Health ID / Insurance Member Number (Kept out of LLM context to respect HIPAA and data privacy boundaries).

## Target Directory Structure
Agents contributing to this repository should adhere to the following directory structure:

```
medbot/
│
├── README.md
├── pyproject.toml
├── .env.example
│
├── backend/                             # FastAPI application & LangGraph Agent
│   ├── main.py                          # FastAPI entrypoint & routes
│   ├── graph.py                         # LangGraph state & workflow definition
│   ├── tools.py                         # Retriever and booking tools
│   └── agui.py                          # AGUI protocol event models & streaming
│
├── rag/                                 # Knowledge base & retrieval indexing
│   ├── docs/                            # Source documents (markdown files)
│   ├── ingest.py                        # Document chunking & embedding script
│   └── vector_store.py                  # Vector store access logic
│
├── frontend/                            # Streamlit user interface
│   ├── app.py                           # Main Streamlit layout and session manager
│   ├── client.py                        # API client handling SSE streams from FastAPI
│   └── components.py                    # Renders chat and AGUI forms
│
└── tests/
    └── test_app.py                      # Basic tests for routes and graph
```

## Developer Notes
- **Dependencies**: The project uses `uv` for dependency management. All dependency additions must be done via `uv add <package>` instead of standard pip.
- **Pre-commit**: Ruff is used for linting and formatting via pre-commit hooks.
- **Docker**: This is a toy project meant to be run directly on the host using the `uv` virtual environment. Docker is **not** required.
