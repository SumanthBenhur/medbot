from pydantic import BaseModel
from typing import Any, Dict, Literal


# Base model for all SSE events
class AGUIEvent(BaseModel):
    type: Literal[
        "text", "thought", "tool_call", "tool_result", "human_prompt", "error", "done"
    ]
    data: Any


class ChatTokenEvent(BaseModel):
    text: str


class ThoughtEvent(BaseModel):
    thought: str


class ToolCallEvent(BaseModel):
    name: str
    input_args: Dict[str, Any]


class ToolResultEvent(BaseModel):
    name: str
    result: str


class HumanPromptEvent(BaseModel):
    prompt_type: Literal["center_name", "patient_id"]
    message: str


def format_sse(event_type: str, data: Any) -> str:
    """Formats a message for Server-Sent Events."""
    import json

    return f"event: {event_type}\ndata: {json.dumps(data)}\n\n"
