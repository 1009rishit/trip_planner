import streamlit as st
from orchestration import ConversationalOrchestrator

st.set_page_config(page_title="Trip Planner AI", layout="wide")
st.title("🗺️ Conversational Trip Planner")

# -----------------------------
# Initialize orchestrator
# -----------------------------
if "orchestrator" not in st.session_state:
    st.session_state.orchestrator = ConversationalOrchestrator()

orchestrator = st.session_state.orchestrator

# -----------------------------
# User input
# -----------------------------
user_input = st.text_input("Ask me about your trip:")

if user_input:
    # Process user input through orchestrator
    result = orchestrator.process_user_input(user_input)

    response_data = result.get("response")
    response_text = (
        response_data.get("raw") if isinstance(response_data, dict) else str(response_data)
    )

    # Show assistant response
    st.markdown(f"**Assistant:** {response_text}")

    # Show current trip context
    st.markdown("### 📌 Current Trip Context")
    st.markdown(orchestrator.get_context_summary())

    # Show conversation history (optional)
    st.markdown("### 💬 Conversation History")
    for turn in orchestrator.conversation_history:
        st.markdown(f"**User:** {turn['user']}")
        st.markdown(f"**Assistant:** {turn['assistant']}")
