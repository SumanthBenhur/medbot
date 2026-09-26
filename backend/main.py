from typing import Optional
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from langchain_core.messages import HumanMessage
from langgraph.types import Command
from pydantic import BaseModel

from backend.agui import (
    ChatTokenEvent,
    ThoughtEvent,
    ToolCallEvent,
    ToolResultEvent,
    format_sse,
)
from backend.graph import graph

load_dotenv()

app = FastAPI(title="Medbot LangGraph Backend")


class ChatRequest(BaseModel):
    message: Optional[str] = None
    thread_id: str
    patient_id: Optional[str] = None
    center_name: Optional[str] = None


@app.post("/chat")
async def chat_endpoint(req: ChatRequest):
    # LangGraph uses thread_id in the config to maintain memory
    config = {"configurable": {"thread_id": req.thread_id}}

    async def event_generator():
        try:
            # If the user provided a center_name, we are resuming from a human-in-the-loop interrupt
            if req.center_name:
                input_data = Command(resume=req.center_name)
            elif req.message:
                # Normal initial message
                input_data = {"messages": [HumanMessage(content=req.message)]}
                if req.patient_id:
                    input_data["patient_id"] = req.patient_id
            else:
                yield format_sse(
                    "error", {"detail": "No message or center_name provided."}
                )
                return

            # Stream events using LangChain's astream_events v2
            async for event in graph.astream_events(input_data, config, version="v2"):
                kind = event["event"]

                # Handle streaming tokens
                if kind == "on_chat_model_stream":
                    chunk = event["data"]["chunk"]

                    # Check for thought/reasoning in chunk
                    thought = None
                    if (
                        hasattr(chunk, "additional_kwargs")
                        and "thought" in chunk.additional_kwargs
                    ):
                        thought = chunk.additional_kwargs["thought"]
                    elif (
                        hasattr(chunk, "response_metadata")
                        and "thought" in chunk.response_metadata
                    ):
                        thought = chunk.response_metadata["thought"]

                    if thought:
                        yield format_sse(
                            "thought", ThoughtEvent(thought=str(thought)).model_dump()
                        )

                    content = chunk.content
                    if isinstance(content, list):
                        for c in content:
                            if isinstance(c, dict):
                                if c.get("type") == "thought" or "thought" in c:
                                    t_text = c.get("thought") or c.get("text", "")
                                    if t_text:
                                        yield format_sse(
                                            "thought",
                                            ThoughtEvent(
                                                thought=str(t_text)
                                            ).model_dump(),
                                        )
                                elif "text" in c and c["text"]:
                                    yield format_sse(
                                        "text",
                                        ChatTokenEvent(text=c["text"]).model_dump(),
                                    )
                    elif isinstance(content, str) and content:
                        yield format_sse(
                            "text", ChatTokenEvent(text=content).model_dump()
                        )

                # Handle tool calls starting
                elif kind == "on_tool_start":
                    # Filter out tools that aren't ours (LangChain sometimes emits internal events)
                    if event["name"] in ["book_appointment"]:
                        inputs = event["data"].get("input", {})
                        yield format_sse(
                            "tool_call",
                            ToolCallEvent(
                                name=event["name"], input_args=inputs
                            ).model_dump(),
                        )

                # Handle tool calls finishing
                elif kind == "on_tool_end":
                    if event["name"] in ["book_appointment"]:
                        result = event["data"].get("output", "")
                        yield format_sse(
                            "tool_result",
                            ToolResultEvent(
                                name=event["name"], result=str(result)
                            ).model_dump(),
                        )

            # After the stream finishes, check if the graph paused due to an interrupt()
            state = graph.get_state(config)
            for task in state.tasks:
                if task.interrupts:
                    for intr in task.interrupts:
                        val = intr.value
                        if isinstance(val, dict) and val.get("type") == "human_prompt":
                            # Stream the human prompt request to the frontend
                            yield format_sse("human_prompt", val)

            # Signal the end of the stream
            yield format_sse("done", {"status": "success"})

        except Exception as e:
            yield format_sse("error", {"detail": str(e)})

    return StreamingResponse(event_generator(), media_type="text/event-stream")
