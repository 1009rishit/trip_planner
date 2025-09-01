# frontend/streamlit_app.py
import streamlit as st
from orchestration import ConversationalOrchestrator

st.set_page_config(page_title="Trip Planner", layout="wide")

st.title("🧳 AI Trip Planner")
st.write("Plan your trips with conversational AI powered by ChromaDB memory.")

if "orchestrator" not in st.session_state:
    st.session_state.orchestrator = ConversationalOrchestrator()

user_input = st.text_input("Ask me about your trip:")

if user_input:
    result = st.session_state.orchestrator.process_user_input(user_input)
    st.markdown(f"**Intent:** {result['intent']}")
    st.markdown(f"**Response:** {result['response']['raw']}")
    st.markdown("**Current Context:**")
    st.markdown(result['orchestrator'].get_context_summary())
