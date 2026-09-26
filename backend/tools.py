import httpx
from langchain_core.tools import tool
from langgraph.prebuilt import InjectedState
from typing import Annotated


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


# We can add the retriever tool here later
