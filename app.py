import streamlit as st
import json
import os
import time
from rag_engine import StoreCopilotEngine

st.set_page_config(page_title="General Store Copilot", page_icon="🛒", layout="wide")


# Initialize back-end engine
@st.cache_resource
def init_engine():
    return StoreCopilotEngine()


engine = init_engine()

# --- UI LAYOUT & BRANDING ---
st.title("🛒 General Store Associate Copilot")
st.markdown("Your AI assistant for **stock intelligence**, **cross-sell configurations**, and **SOP guidance**.")

# 1. Top Trending Offer Display
try:
    if os.path.exists('offers.json'):
        with open('offers.json', 'r', encoding='utf-8') as f:
            offers_data = json.load(f)
            if offers_data:
                # Pick the first offer as the current trending deal
                top_offer = offers_data[0]
                st.success(
                    f"🔥 **Trending Offer to Pitch:** {top_offer.get('product_name', 'Featured Item')} — {top_offer.get('description', '')} (Price: ${top_offer.get('offer_price', '')})")
except Exception:
    pass  # Silently fail if offers.json is not ready

# Setup Session State for Chat History (Maintains a strict limit of 3 turns)
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Setup Session State for Preset Buttons
if "preset_query" not in st.session_state:
    st.session_state.preset_query = None

# --- SIDEBAR CONFIGURATION ---
with st.sidebar:
    st.header("⚙️ System Settings")

    # 2. LLM Switcher (Groq vs Ollama)
    llm_provider = st.radio(
        "Select Intelligence Engine:",
        ["Groq API (Cloud - Fast)", "Ollama (Local - Private)"],
        help="Switch between cloud processing and your local offline Llama 3 model."
    )
    # Extract just the keyword for the backend
    provider_key = "Groq" if "Groq" in llm_provider else "Ollama"

    st.divider()
    st.info("💡 **Memory Active:** The system remembers your last 3 interactions to provide better context.")

    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()

# --- PREDEFINED QUICK QUERIES ---
st.write("### ⚡ Quick Lookups")
q_cols = st.columns(3)
if q_cols[0].button("📦 Check Apple Stock", use_container_width=True):
    st.session_state.preset_query = "What is the stock and location of Organic Fuji Apples?"
if q_cols[1].button("📋 Opening SOP", use_container_width=True):
    st.session_state.preset_query = "What is the SOP for opening the store?"
if q_cols[2].button("🏷️ Check Drink Offers", use_container_width=True):
    st.session_state.preset_query = "Are there any active offers on Energy Drinks?"

st.divider()

# --- CHAT INTERFACE ---
# Display historical chat logs
for interaction in st.session_state.chat_history:
    with st.chat_message("user"):
        st.markdown(interaction["query"])
    with st.chat_message("assistant"):
        st.markdown(interaction["response"])

# Accept Input Queries (either from the text box or a preset button)
user_input = st.chat_input("Ask about stock levels, aisle numbers, offers, planogram adjacencies, or SOP rules...")
if st.session_state.preset_query:
    user_input = st.session_state.preset_query
    st.session_state.preset_query = None

if user_input:
    with st.chat_message("user"):
        st.markdown(user_input)

    if engine and engine.db:
        with st.chat_message("assistant"):
            with st.spinner(f"Analyzing store database using {provider_key}..."):
                start_time = time.time()
                bot_reply = engine.get_response(user_input, st.session_state.chat_history, provider=provider_key)
                elapsed_time = time.time() - start_time

                st.markdown(bot_reply)
                st.caption(f"⏱️ Response generated in {elapsed_time:.2f} seconds using {provider_key}.")

        # Append to operational storage stack
        st.session_state.chat_history.append({"query": user_input, "response": bot_reply})

        # Enforce strict sliding window threshold constraint to keep last 3 conversations
        if len(st.session_state.chat_history) > 3:
            st.session_state.chat_history.pop(0)
    else:
        st.error(
            "Engine execution blocked. Please ensure Vector store databases are successfully initialized (Run build_vector_db.py first).")