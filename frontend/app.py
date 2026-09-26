import os
import sys
import uuid
from dotenv import load_dotenv
import streamlit as st

# Ensure project root is in sys.path when running directly via Streamlit
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

try:
    from frontend.client import stream_chat
    from frontend.components import (
        DIAGNOSTIC_CENTERS,
        render_hitl_form,
        render_message_item,
        render_sidebar,
        render_thought_block,
        render_tool_confirmation,
    )
except ModuleNotFoundError:
    from client import stream_chat  # type: ignore
    from components import (  # type: ignore
        DIAGNOSTIC_CENTERS,
        render_hitl_form,
        render_message_item,
        render_sidebar,
        render_thought_block,
        render_tool_confirmation,
    )

load_dotenv()

st.set_page_config(
    page_title="Medbot - Medical Prep & Booking Assistant",
    page_icon="🏥",
    layout="wide",
)


def init_session_state() -> None:
    """Initializes all necessary session state variables."""
    if "thread_id" not in st.session_state:
        st.session_state.thread_id = str(uuid.uuid4())
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "awaiting_hitl" not in st.session_state:
        st.session_state.awaiting_hitl = False
    if "hitl_prompt" not in st.session_state:
        st.session_state.hitl_prompt = None
    if "patient_id" not in st.session_state:
        st.session_state.patient_id = ""
    if "preferred_center" not in st.session_state:
        st.session_state.preferred_center = DIAGNOSTIC_CENTERS[0]
    if "backend_url" not in st.session_state:
        st.session_state.backend_url = "http://127.0.0.1:8000"


def execute_stream(payload: dict) -> None:
    """Streams responses from the backend, updates UI elements in real-time, and saves completed turn to history."""
    backend_url = st.session_state.get("backend_url", "http://127.0.0.1:8000")

    with st.chat_message("assistant"):
        thought_placeholder = st.empty()
        text_placeholder = st.empty()
        tool_status_placeholder = st.empty()
        confirmation_placeholder = st.empty()

        accumulated_text = ""
        accumulated_thought = ""
        tool_result = ""
        hitl_received = None

        for event_type, data in stream_chat(backend_url, payload):
            if event_type == "thought":
                # Extract thought text
                thought_chunk = (
                    data.get("thought", "") if isinstance(data, dict) else str(data)
                )
                accumulated_thought += thought_chunk
                with thought_placeholder.container():
                    render_thought_block(accumulated_thought, is_active=True)

            elif event_type == "text":
                text_chunk = (
                    data.get("text", "") if isinstance(data, dict) else str(data)
                )
                accumulated_text += text_chunk
                text_placeholder.markdown(accumulated_text)

            elif event_type == "tool_call":
                tool_name = (
                    data.get("name", "tool") if isinstance(data, dict) else "tool"
                )
                tool_status_placeholder.info(
                    f"⚙️ Calling external service: `{tool_name}`..."
                )

            elif event_type == "tool_result":
                tool_status_placeholder.empty()
                result_str = (
                    data.get("result", "") if isinstance(data, dict) else str(data)
                )
                tool_result = result_str
                with confirmation_placeholder.container():
                    render_tool_confirmation(tool_result)

            elif event_type == "human_prompt":
                hitl_received = data

            elif event_type == "error":
                detail = (
                    data.get("detail", "Unknown error")
                    if isinstance(data, dict)
                    else str(data)
                )
                st.error(f"❌ {detail}")

        # Final cleanup on stream end
        tool_status_placeholder.empty()
        if accumulated_thought:
            with thought_placeholder.container():
                render_thought_block(accumulated_thought, is_active=False)

        # Save assistant message to session history
        if accumulated_text or tool_result or accumulated_thought:
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": accumulated_text,
                    "thought": accumulated_thought,
                    "tool_result": tool_result,
                }
            )

        if hitl_received:
            st.session_state.awaiting_hitl = True
            st.session_state.hitl_prompt = hitl_received
            st.rerun()


def handle_hitl_submission(selected_center: str) -> None:
    """Resumes the LangGraph workflow when a diagnostic center is chosen."""
    st.session_state.awaiting_hitl = False
    st.session_state.hitl_prompt = None

    # Record user's selection in message history
    st.session_state.messages.append(
        {"role": "user", "content": f"Selected Center: **{selected_center}**"}
    )

    resume_payload = {
        "thread_id": st.session_state.thread_id,
        "center_name": selected_center,
    }
    execute_stream(resume_payload)


def main() -> None:
    init_session_state()
    render_sidebar()

    st.header("🏥 Medbot — Diagnostic Assistant")
    st.markdown(
        "Ask questions regarding diagnostic test prep protocols, fasting guidelines, or schedule your lab appointment."
    )

    # Render previous conversation history
    for msg in st.session_state.messages:
        render_message_item(msg)

    # If the workflow is currently interrupted waiting for user center selection
    if st.session_state.awaiting_hitl and st.session_state.hitl_prompt:
        render_hitl_form(
            prompt_data=st.session_state.hitl_prompt,
            on_submit_callback=handle_hitl_submission,
            default_center=st.session_state.get("preferred_center"),
        )

    # User Chat Input
    prompt = st.chat_input(
        "Type your message here...", disabled=st.session_state.awaiting_hitl
    )
    if prompt:
        # Add user message to history
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Re-render user message immediately
        with st.chat_message("user"):
            st.markdown(prompt)

        # Build backend chat payload
        payload = {
            "thread_id": st.session_state.thread_id,
            "message": prompt,
        }
        if st.session_state.get("patient_id"):
            payload["patient_id"] = st.session_state.patient_id

        execute_stream(payload)


if __name__ == "__main__":
    main()
