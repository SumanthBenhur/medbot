from typing import Any, Callable, Dict, Optional
import uuid
import streamlit as st

DIAGNOSTIC_CENTERS = [
    "Downtown Medical Plaza",
    "Westside Imaging Lab",
    "Metro Central Annex",
]


def render_sidebar() -> None:
    """Renders the Streamlit sidebar containing HIPAA-compliant non-prompt inputs and session controls."""
    with st.sidebar:
        st.title("🏥 Medbot Assistant")
        st.caption("Diagnostic Prep Guidelines & Scheduling")
        st.markdown("---")

        st.subheader("🔒 Privacy & Non-Prompt Inputs")
        st.markdown(
            "<small style='color: gray;'>"
            "Sensitive identifiers are maintained in secure session state and excluded from LLM prompt context to adhere to HIPAA guidelines."
            "</small>",
            unsafe_allow_html=True,
        )

        patient_id = st.text_input(
            "Patient Health ID / Member #",
            value=st.session_state.get("patient_id", ""),
            placeholder="e.g., MED-948201",
            help="Your National Health ID / Insurance Member Number is isolated from LLM prompts.",
            key="input_patient_id",
        )
        st.session_state.patient_id = patient_id

        selected_center = st.selectbox(
            "Preferred Diagnostic Branch",
            options=DIAGNOSTIC_CENTERS,
            index=DIAGNOSTIC_CENTERS.index(
                st.session_state.get("preferred_center", DIAGNOSTIC_CENTERS[0])
            )
            if st.session_state.get("preferred_center") in DIAGNOSTIC_CENTERS
            else 0,
            key="select_preferred_center",
        )
        st.session_state.preferred_center = selected_center

        st.markdown("---")
        st.subheader("⚙️ Session & Backend")

        backend_url = st.text_input(
            "Backend API URL",
            value=st.session_state.get("backend_url", "http://127.0.0.1:8000"),
            key="input_backend_url",
        )
        st.session_state.backend_url = backend_url

        st.text(f"Thread ID: {st.session_state.get('thread_id', '')[:8]}...")

        if st.button("🔄 New Conversation", use_container_width=True):
            st.session_state.thread_id = str(uuid.uuid4())
            st.session_state.messages = []
            st.session_state.awaiting_hitl = False
            st.session_state.hitl_prompt = None
            st.rerun()


def render_thought_block(thought_text: str, is_active: bool = False) -> None:
    """Renders reasoning / thought tokens in an expandable container."""
    if not thought_text:
        return
    label = (
        "💭 Reasoning Process (Generating...)" if is_active else "💭 Reasoning Process"
    )
    with st.expander(label, expanded=is_active):
        st.markdown(
            f"<div style='font-family: monospace; font-size: 0.88rem; color: #4b5563; white-space: pre-wrap;'>"
            f"{thought_text}"
            f"</div>",
            unsafe_allow_html=True,
        )


def render_tool_confirmation(result_text: str) -> None:
    """Renders the verbatim confirmation string from the external booking API."""
    if not result_text:
        return
    st.success(f"📋 **External API Confirmation:**\n\n{result_text}")


def render_message_item(msg: Dict[str, Any]) -> None:
    """Renders a single message item from chat history."""
    role = msg.get("role", "assistant")
    with st.chat_message(role):
        # Render thoughts if present
        if msg.get("thought"):
            render_thought_block(msg["thought"], is_active=False)

        # Render main content
        if msg.get("content"):
            st.markdown(msg["content"])

        # Render direct external tool results if present
        if msg.get("tool_result"):
            render_tool_confirmation(msg["tool_result"])


def render_hitl_form(
    prompt_data: Dict[str, Any],
    on_submit_callback: Callable[[str], None],
    default_center: Optional[str] = None,
) -> None:
    """Renders the Human-in-the-Loop AGUI form for center selection."""
    prompt_message = prompt_data.get(
        "message", "Please select your preferred diagnostic center for the booking."
    )

    with st.container():
        st.info(f"📍 **Action Required:** {prompt_message}")
        with st.form(key="hitl_center_form"):
            initial_index = 0
            if default_center in DIAGNOSTIC_CENTERS:
                initial_index = DIAGNOSTIC_CENTERS.index(default_center)

            chosen_center = st.selectbox(
                "Diagnostic Center / Lab Branch",
                options=DIAGNOSTIC_CENTERS,
                index=initial_index,
            )
            submitted = st.form_submit_button(
                "Confirm & Schedule Appointment",
                type="primary",
                use_container_width=True,
            )
            if submitted:
                on_submit_callback(chosen_center)
