# Retrieval Tool Implementation Plan

## 1. Overview & Objective
The goal is to implement the **Retriever Tool** in [backend/tools.py](file:///c:/Users/abelp/medbot/backend/tools.py) and integrate it with the LangGraph agent workflow in [backend/graph.py](file:///c:/Users/abelp/medbot/backend/graph.py), adhering to guidelines in [AGENTS.md](file:///c:/Users/abelp/medbot/AGENTS.md).

The tool enables the assistant to scan and retrieve relevant knowledge chunks concerning:
- **Test preparation protocols** (e.g., fasting rules, dietary constraints)
- **Clinical contraindications** (e.g., pacemakers, pregnancy, metal implants)
- **Insurance coverage & pre-authorization requirements**
- **Test durations & general lab FAQs**

---

## 2. Architecture & Data Flow

```mermaid
flowchart TD
    UserQuery["User Asks Medical/Prep Question"] --> LLM["Assistant Node (Gemini)"]
    LLM -->|Tool Call: retrieve_medical_guidelines| RetrieverTool["Retriever Tool (backend/tools.py)"]
    RetrieverTool -->|get_retriever(k=3).invoke()| VectorStore["Chroma Vector Store (rag/vector_store.py)"]
    VectorStore -->|Doc Chunks & Metadata| RetrieverTool
    RetrieverTool -->|Formatted Context| ToolsNode["Tools Node"]
    ToolsNode -->|route_after_tools: assistant| LLM
    LLM -->|Synthesized Clinical Response| Patient["Patient Streamed Response"]
```

---

## 3. Implementation Steps

### Step 1: Implement `retrieve_medical_guidelines` in `backend/tools.py`
1. **Import dependencies**:
   - `get_retriever` from `rag.vector_store`
   - `@tool` decorator from `langchain_core.tools`
2. **Tool Definition**:
   - **Name**: `retrieve_medical_guidelines`
   - **Signature**: `def retrieve_medical_guidelines(query: str) -> str`
   - **Docstring**: Clear instructions describing when the tool should be invoked (medical test preparation, contraindications, insurance policies, and test requirements).
   - **Logic**:
     - Retrieve relevant document chunks using `get_retriever(k=3).invoke(query)`.
     - Format chunks into a clean, readable context string including source document metadata.
     - Return the formatted string back to the agent.

```python
# Reference snippet for backend/tools.py
from langchain_core.tools import tool
from rag.vector_store import get_retriever

@tool
def retrieve_medical_guidelines(query: str) -> str:
    """
    Scans and retrieves medical preparation guidelines, clinical contraindications,
    and insurance coverage policies for diagnostic tests.

    Args:
        query: Specific medical query or test topic to retrieve information for.
    """
    retriever = get_retriever(k=3)
    docs = retriever.invoke(query)
    
    if not docs:
        return "No relevant medical guidelines or protocol documents found."

    results = []
    for doc in docs:
        source = doc.metadata.get("source", "Unknown Document")
        results.append(f"Source ({source}):\n{doc.page_content}")

    return "\n\n---\n\n".join(results)
```

---

### Step 2: Register the Tool in `backend/graph.py`
1. **Update Tool List**:
   - Import `retrieve_medical_guidelines` from `backend.tools`.
   - Update `tools = [book_appointment, retrieve_medical_guidelines]`.
2. **Verify Workflow Routing**:
   - Verify `assistant_node` binds both tools.
   - In `route_after_tools(state: AgentState)`:
     - `book_appointment` ends the graph (`return END`) because it returns verbatim confirmation to the user.
     - `retrieve_medical_guidelines` routes back to `assistant` (`return "assistant"`), allowing the LLM to synthesize the final answer.

---

## 4. Verification & Testing Plan

1. **Ingest Knowledge Base**:
   - Verify that [rag/ingest.py](file:///c:/Users/abelp/medbot/rag/ingest.py) has run and indexed markdown files from [rag/docs/](file:///c:/Users/abelp/medbot/rag/docs/) into `rag/chroma_db`.
   
2. **Unit Test / Direct Invocation**:
   - Call `retrieve_medical_guidelines.invoke("What are the fasting rules for an abdominal ultrasound?")` directly to verify formatted output and correct source attribution.

3. **LangGraph Agent Workflow Test**:
   - Query the agent with a sample clinical question: *"Can I have breakfast before a lipid panel test?"*
   - Verify that the tool execution is logged, documents are retrieved, and the assistant streams back an accurate synthesized response.
