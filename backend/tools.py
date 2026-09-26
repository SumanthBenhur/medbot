from typing import Annotated
import httpx
from langchain_core.tools import tool
from langgraph.prebuilt import InjectedState
from rag.vector_store import get_retriever


@tool(return_direct=True)
def book_appointment(booking_time: str, state: Annotated[dict, InjectedState]) -> str:
    """
    Schedules a diagnostic lab appointment for the patient.

    Args:
        booking_time: The desired time for the appointment in 'YYYY-MM-DD HH:MM' format.
    """
    # center_name is provided via human-in-the-loop and injected into the graph state
    center_name = state.get("center_name")

    if not center_name:
        return "Error: 'center_name' was not provided in the runtime configuration."

    try:
        response = httpx.post(
            "http://127.0.0.1:8001/book",
            json={"center_name": center_name, "time": booking_time},
            timeout=10.0,
        )
        # If it's a 4xx or 5xx error, this raises an exception
        response.raise_for_status()

        # Parse the successful response
        data = response.json()

        # Returning this string verbatim. return_direct=True ensures it bypasses the LLM.
        return data["message"]

    except httpx.HTTPStatusError as e:
        try:
            error_detail = e.response.json().get("detail", e.response.text)
        except Exception:
            error_detail = e.response.text
        return f"Booking failed: {error_detail}"
    except Exception as e:
        return f"An error occurred while attempting to book the appointment: {str(e)}"


@tool
def retrieve_medical_guidelines(query: str) -> str:
    """
    Scans and retrieves information across all clinical diagnostic knowledge documents, including:
    1. Test preparation protocols (fasting rules, diet, medication guidelines).
    2. Clinical contraindications and safety precautions (implants, allergies, pregnancy).
    3. Insurance coverage, pre-authorization, and cost policies.
    4. Test durations, check-in instructions, and appointment requirements.
    5. Diagnostic test FAQs and general procedure details.

    Args:
        query: Specific medical query or test topic to retrieve information for.
    """
    retriever = get_retriever(k=1)
    docs = retriever.invoke(query)

    if not docs:
        return "No relevant medical guidelines or protocol documents found."

    results = []
    for doc in docs:
        source = doc.metadata.get("source", "Unknown Document")
        results.append(f"Source ({source}):\n{doc.page_content}")

    return "\n\n---\n\n".join(results)
