import streamlit as st
from rag_engine import StoreCopilotEngine

st.set_page_config(page_title="General Store Copilot", page_icon="🛒", layout="wide")


# Initialize back-end engine
@st.cache_resource
def init_engine():
    return StoreCopilotEngine()


try:
    engine = init_engine()
except Exception as e:
    st.error(f"Failed to boot RAG Engine. Check your Groq Key setup. Error: {e}")
    engine = None

st.title("🛒 General Store Associate Copilot")
st.caption("On-demand stock intelligence, cross-sell configurations, planogram lookups, and SOP guidance.")

# Setup Session State for limiting conversation tracking history logs to maximum 3
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Sidebar info
with st.sidebar:
    st.header("System Settings")
    st.success("Connected to: Local Embeddings Engine")
    st.info("Core LLM Architecture: Llama-3-8B (Groq)")

    if st.button("Reset Chat Logs"):
        st.session_state.chat_history = []
        st.rerun()

# Display Chat logs
for interaction in st.session_state.chat_history:
    with st.chat_message("user"):
        st.markdown(interaction["query"])
    with st.chat_message("assistant"):
        st.markdown(interaction["response"])

# Accept Input Queries
if user_input := st.chat_input("Ask about stock levels, aisle numbers, offers, planogram adjacencies, or SOP rules..."):

    with st.chat_message("user"):
        st.markdown(user_input)

    if engine:
        with st.chat_message("assistant"):
            with st.spinner("Analyzing store database..."):
                bot_reply = engine.get_response(user_input, st.session_state.chat_history)
                st.markdown(bot_reply)

        # Append to operational storage stack
        st.session_state.chat_history.append({"query": user_input, "response": bot_reply})

        # Enforce strict sliding window threshold constraint to keep last 2-3 conversations maximum
        if len(st.session_state.chat_history) > 3:
            st.session_state.chat_history.pop(0)
    else:
        st.error("Engine execution blocked. Please ensure Vector store databases are successfully initialized.")