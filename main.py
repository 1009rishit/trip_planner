# main.py
import streamlit as st
from orchestration import ConversationalOrchestrator
from db.embedding import MiniLMEmbedder
from db.memory_store import add_memory, query_memory

st.set_page_config(page_title="Trip Planner AI", layout="wide")
st.title("🗺️ Conversational Trip Planner")

# -----------------------------
# Initialize orchestrator
# -----------------------------
if "orchestrator" not in st.session_state:
    st.session_state.orchestrator = ConversationalOrchestrator()

orchestrator = st.session_state.orchestrator
embedder = MiniLMEmbedder()


user_input = st.text_input("Ask me about your trip:")

if user_input:

    result = orchestrator.process_user_input(user_input)
    response_data = result.get("response")
    response_text = (
        response_data.get("raw") if isinstance(response_data, dict) else str(response_data)
    )
    st.markdown(f"**Assistant:** {response_text}")

    memory_text = f"User: {user_input}\nAssistant: {response_text}"
    add_memory(
        doc_id=str(len(orchestrator.conversation_history)),
        text=memory_text,
        metadata={"intent": result.get("intent", "general")}
    )

    # -----------------------------
    # 3. Update local conversation history
    # -----------------------------
    orchestrator.conversation_history.append({"user": user_input, "assistant": response_text})

    # -----------------------------
    # 4. Show current trip context summary
    # -----------------------------
    st.markdown(f"**Current Trip Context:**\n{orchestrator.get_context_summary()}")
