from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.prebuilt import ToolNode
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import ToolMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt
from typing import Optional

from backend.tools import book_appointment, retrieve_medical_guidelines


class AgentState(MessagesState):
    patient_id: Optional[str]
    center_name: Optional[str]


tools = [book_appointment, retrieve_medical_guidelines]

# Using gemini-3.7-flash as the standard model for fast, reliable tool calling
llm = ChatGoogleGenerativeAI(
    model="gemini-3.7-flash", temperature=0, streaming=True, max_retries=2
).bind_tools(tools)

# The pre-built tool node will execute the tools
tool_node = ToolNode(tools)


async def assistant_node(state: AgentState):
    """The main LLM node."""
    # We pass the messages to the model
    # We could also inject a system prompt here if needed
    response = await llm.ainvoke(state["messages"])
    return {"messages": [response]}


async def human_in_the_loop_node(state: AgentState):
    """
    Checks if a tool requires a human input (like center_name).
    If so, interrupts the graph to ask the user.
    """
    last_message = state["messages"][-1]

    if last_message.tool_calls:
        for tool_call in last_message.tool_calls:
            if tool_call["name"] == "book_appointment":
                # Check if we already have the center_name in the state
                if not state.get("center_name"):
                    # Interrupt execution and send a payload to the client
                    # The frontend should capture this and prompt the user.
                    center_name = interrupt(
                        {
                            "type": "human_prompt",
                            "prompt_type": "center_name",
                            "message": "Please select your preferred diagnostic center for the booking.",
                        }
                    )
                    # When resumed, the graph will inject the user's response here.
                    return {"center_name": center_name}
    return {}


def should_continue(state: AgentState):
    """Router: if a tool is called, go to hitl -> tools. Else end."""
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "human_in_the_loop"
    return END


def route_after_tools(state: AgentState):
    """
    Router: if the booking tool was called, we return verbatim,
    so we can just end the graph.
    """
    last_message = state["messages"][-1]
    if (
        isinstance(last_message, ToolMessage)
        and last_message.name == "book_appointment"
    ):
        return END

    return "assistant"


# Build the workflow
workflow = StateGraph(AgentState)
workflow.add_node("assistant", assistant_node)
workflow.add_node("human_in_the_loop", human_in_the_loop_node)
workflow.add_node("tools", tool_node)

workflow.add_edge(START, "assistant")
workflow.add_conditional_edges("assistant", should_continue, ["human_in_the_loop", END])
workflow.add_edge("human_in_the_loop", "tools")
workflow.add_conditional_edges("tools", route_after_tools, ["assistant", END])

# Compile with a checkpointer so we can pause and resume
memory = MemorySaver()
graph = workflow.compile(checkpointer=memory)
