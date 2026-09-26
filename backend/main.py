from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
from langchain_core.messages import HumanMessage
from langgraph.types import Command

from backend.graph import graph
from backend.agui import format_sse, ChatTokenEvent, ToolCallEvent, ToolResultEvent

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

                    # If the model emits thought/reasoning tokens, they'd be handled here.
                    # For standard text:
                    content = chunk.content
                    if isinstance(content, list):
                        content = "".join(
                            c.get("text", "")
                            for c in content
                            if isinstance(c, dict) and "text" in c
                        )

                    if content:
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
