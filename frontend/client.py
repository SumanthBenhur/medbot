import json
from typing import Any, Dict, Generator, Tuple
import httpx


def stream_chat(
    api_url: str, payload: Dict[str, Any], timeout: float = 60.0
) -> Generator[Tuple[str, Any], None, None]:
    """Streams Server-Sent Events (SSE) from the FastAPI backend.

    Yields tuples of (event_type, parsed_data).
    """
    endpoint = f"{api_url.rstrip('/')}/chat"
    current_event = "message"

    try:
        with httpx.stream("POST", endpoint, json=payload, timeout=timeout) as response:
            if response.status_code != 200:
                error_body = response.read().decode("utf-8")
                yield (
                    "error",
                    {
                        "detail": f"Server returned error {response.status_code}: {error_body}"
                    },
                )
                return

            for line in response.iter_lines():
                if not line:
                    current_event = "message"
                    continue

                if line.startswith("event: "):
                    current_event = line[7:].strip()
                elif line.startswith("data: "):
                    data_str = line[6:].strip()
                    try:
                        data = json.loads(data_str)
                    except json.JSONDecodeError:
                        data = data_str

                    yield (current_event, data)

    except httpx.ConnectError:
        yield (
            "error",
            {
                "detail": f"Could not connect to backend server at {api_url}. Is FastAPI running on port 8000?"
            },
        )
    except httpx.TimeoutException:
        yield (
            "error",
            {"detail": "Request timed out while waiting for backend response."},
        )
    except Exception as e:
        yield ("error", {"detail": f"Streaming error: {str(e)}"})
