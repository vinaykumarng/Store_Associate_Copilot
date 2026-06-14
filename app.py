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

# Define SOP checklists from sops.json if available, or fall back to high-fidelity defaults
OPENING_STEPS = [
    "Arrive 30 minutes before store opening.",
    "Disable the alarm using the keypad (code in manager's binder).",
    "Turn on all lights aisle by aisle using the panel in the back office.",
    "Check the overnight freight log and sign off.",
    "Walk each aisle for safety hazards (spills, fallen items, blocked exits).",
    "Verify POS terminals boot correctly — reboot any frozen terminals.",
    "Confirm all refrigerated sections are at correct temp (dairy: 35–38°F, frozen: 0°F or below).",
    "Unlock customer-entry doors at opening time.",
    "Announce store opening over intercom: 'Good morning, shoppers. Welcome to our store!'"
]

CLOSING_STEPS = [
    "Announce closing 15 minutes before close: 'Attention shoppers, the store will close in 15 minutes.'",
    "Begin escorting remaining customers to checkout.",
    "Lock all entrance doors once last customer has exited.",
    "Complete end-of-day cash reconciliation at each POS lane.",
    "Process Z-tape from all registers and deposit cash in the safe.",
    "Perform a final walk-through to ensure all zones are clean and clear of hazards.",
    "Turn off all non-essential lights using the back office breaker panel.",
    "Set the security alarm at the exit keypad and secure the final exit doors."
]

# Try to dynamic-load from raw JSON if available to match dataset precisely
try:
    if os.path.exists('sops.json'):
        with open('sops.json', 'r', encoding='utf-8') as f:
            sops_data = json.load(f)
            for sop in sops_data:
                if "Opening" in sop.get("title", ""):
                    OPENING_STEPS = sop.get("steps", OPENING_STEPS)
                elif "Closing" in sop.get("title", ""):
                    CLOSING_STEPS = sop.get("steps", CLOSING_STEPS)
except Exception:
    pass

# --- SESSION STATE INITIALIZATIONS ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "preset_query" not in st.session_state:
    st.session_state.preset_query = None

if "demand_log" not in st.session_state:
    st.session_state.demand_log = []

# SOP Checklist states
if "opening_checklist_progress" not in st.session_state:
    st.session_state.opening_checklist_progress = [False] * len(OPENING_STEPS)

if "closing_checklist_progress" not in st.session_state:
    st.session_state.closing_checklist_progress = [False] * len(CLOSING_STEPS)

if "sop_instruction" not in st.session_state:
    st.session_state.sop_instruction = "Select a checklist tab to begin your guided store operations."

# --- UI LAYOUT & BRANDING ---
st.title("🛒 General Store Associate Copilot")
st.markdown(
    "Your AI assistant for **stock intelligence**, **cross-sell configurations**, and **guided SOP checklists**.")

# 1. Top Trending Offer Display
try:
    if os.path.exists('offers.json'):
        with open('offers.json', 'r', encoding='utf-8') as f:
            offers_data = json.load(f)
            if offers_data:
                top_offer = offers_data[0]
                st.success(
                    f"🔥 **Trending Offer to Pitch:** {top_offer.get('product_name', 'Featured Item')} — {top_offer.get('description', '')} (Price: ${top_offer.get('offer_price', '')})")
except Exception:
    pass

# --- SIDEBAR CONFIGURATION ---
with st.sidebar:
    st.header("⚙️ System Settings")

    # 2. LLM Switcher (Groq vs Ollama)
    llm_provider = st.radio(
        "Select Intelligence Engine:",
        ["Groq API (Cloud - Fast)", "Ollama (Local - Private)"],
        help="Switch between cloud processing and your local offline Llama 3 model."
    )
    provider_key = "Groq" if "Groq" in llm_provider else "Ollama"

    st.divider()
    st.info("💡 **Memory Active:** The system remembers your last 3 chat interactions to provide better context.")

    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()

    st.divider()

    # 3. Manager Demand Dashboard
    st.header("📊 Manager Demand Dashboard")
    st.caption("Tracks out-of-stock items ordered by customers today.")
    if st.session_state.demand_log:
        for item in reversed(st.session_state.demand_log):
            st.warning(f"📦 Demand Logged for query: '{item}'")
    else:
        st.write("No out-of-stock orders yet.")

# --- NAVIGATION TABS ---
tab_chat, tab_opening, tab_closing = st.tabs([
    "💬 AI Copilot Assistant",
    "🌅 Store Opening Checklist",
    "🌃 Store Closing Checklist"
])

# ==================== TAB 1: AI COPILOT CHAT ====================
with tab_chat:
    st.write("### ⚡ Quick Lookups")
    q_cols = st.columns(3)
    if q_cols[0].button("📦 Check Apple Stock", use_container_width=True):
        st.session_state.preset_query = "What is the stock and location of Organic Fuji Apples?"
        st.rerun()
    if q_cols[1].button("💥 More about Trending offer ", use_container_width=True):
        st.session_state.preset_query = f"Say more about the 🔥 **Trending Offer to Pitch:** {top_offer.get('product_name', 'Featured Item')} — {top_offer.get('description', '')} (Price: ${top_offer.get('offer_price', '')})"
        st.rerun()
    if q_cols[2].button("🏷️ Check Drink Offers", use_container_width=True):
        st.session_state.preset_query = "Are there any active offers on Energy Drinks?"
        st.rerun()

    st.divider()

    # Display historical chat logs
    for i, interaction in enumerate(st.session_state.chat_history):
        with st.chat_message("user"):
            st.markdown(interaction["query"])
        with st.chat_message("assistant"):
            st.markdown(interaction["response"])

            # Interactive Escalation Button
            if "[📦 SYSTEM ESCALATION: ITEM OUT OF STOCK]" in interaction["response"]:
                if st.button("🛒 Place Order (Log Demand to Manager)", key=f"order_btn_{i}"):
                    if interaction["query"] not in st.session_state.demand_log:
                        st.session_state.demand_log.append(interaction["query"])
                    st.success("✅ Order placed successfully! The demand has been logged for management review.")
                    time.sleep(1.2)
                    st.rerun()

    # Accept Input Queries
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

            st.session_state.chat_history.append({"query": user_input, "response": bot_reply})
            if len(st.session_state.chat_history) > 3:
                st.session_state.chat_history.pop(0)

            st.rerun()
        else:
            st.error("Engine execution blocked. Please build the FAISS index first.")

# ==================== TAB 2: STORE OPENING CHECKLIST ====================
with tab_opening:
    st.subheader("🌅 Store Opening SOP Checklist")
    st.markdown(
        "Mark off tasks as you perform them. The RAG engine will instantly analyze your progress and generate guidance for your next step.")

    col1, col2 = st.columns([1.2, 1])

    with col1:
        st.write("#### 📋 Operational Tasks")
        completed_list = []
        next_step_to_do = None

        # Build dynamic checkboxes
        for idx, step in enumerate(OPENING_STEPS):
            is_checked = st.checkbox(
                step,
                value=st.session_state.opening_checklist_progress[idx],
                key=f"open_step_{idx}"
            )
            st.session_state.opening_checklist_progress[idx] = is_checked

            if is_checked:
                completed_list.append(step)
            elif next_step_to_do is None:
                next_step_to_do = step

        # Calculate progress stats
        total_steps = len(OPENING_STEPS)
        completed_count = len(completed_list)
        progress_percentage = completed_count / total_steps
        st.progress(progress_percentage)
        st.caption(f"Progress: {completed_count}/{total_steps} steps complete ({int(progress_percentage * 100)}%)")

    with col2:
        st.info("💡 **RAG Assistant Next-Step Guidance**")

        if completed_count == total_steps:
            st.success(
                "🎉 **Checklist Complete!** All opening protocols have been logged. The store is officially ready for customers.")
        elif next_step_to_do:
            st.write(f"**Target Task:** *{next_step_to_do}*")

            # Button to fetch dynamic details from local knowledgebase
            if st.button("🚀 Click here for More Information", key="get_open_instruction_btn"):
                with st.spinner("Consulting store standard procedures database..."):
                    guidance = engine.get_sop_guidance(
                        sop_title="Opening Store Checklist",
                        completed_steps=completed_list,
                        next_step=next_step_to_do,
                        provider=provider_key
                    )
                    st.session_state.sop_instruction = guidance

            st.markdown(f"> {st.session_state.sop_instruction}")
            st.caption(
                "*This helper pulls active store safety rules, breaker panel details, and manager binder positions directly from local SOP documentation.*")

# ==================== TAB 3: STORE CLOSING CHECKLIST ====================
with tab_closing:
    st.subheader("🌃 Store Closing SOP Checklist")
    st.markdown(
        "Ensure security, accounting balance, and store cleanliness. Progress to retrieve real-time instructions for subsequent stages.")

    col1_c, col2_c = st.columns([1.2, 1])

    with col1_c:
        st.write("#### 📋 Operational Tasks")
        completed_list_c = []
        next_step_to_do_c = None

        for idx, step in enumerate(CLOSING_STEPS):
            is_checked = st.checkbox(
                step,
                value=st.session_state.closing_checklist_progress[idx],
                key=f"close_step_{idx}"
            )
            st.session_state.closing_checklist_progress[idx] = is_checked

            if is_checked:
                completed_list_c.append(step)
            elif next_step_to_do_c is None:
                next_step_to_do_c = step

        # Closing progress bar
        total_steps_c = len(CLOSING_STEPS)
        completed_count_c = len(completed_list_c)
        progress_percentage_c = completed_count_c / total_steps_c
        st.progress(progress_percentage_c)
        st.caption(
            f"Progress: {completed_count_c}/{total_steps_c} steps complete ({int(progress_percentage_c * 100)}%)")

    with col2_c:
        st.info("💡 **RAG Assistant Next-Step Guidance**")

        if completed_count_c == total_steps_c:
            st.success(
                "🔒 **Checklist Complete!** Cash drawers are secure, hazards cleared, alarms set, and doors locked. Safe travels!")
        elif next_step_to_do_c:
            st.write(f"**Target Task:** *{next_step_to_do_c}*")

            if st.button("🚀 Retrieve Operational Instructions", key="get_close_instruction_btn"):
                with st.spinner("Analyzing cash safety, lighting schedules, and locking mechanisms..."):
                    guidance_c = engine.get_sop_guidance(
                        sop_title="Closing Store Checklist",
                        completed_steps=completed_list_c,
                        next_step=next_step_to_do_c,
                        provider=provider_key
                    )
                    st.session_state.sop_instruction = guidance_c

            st.markdown(f"> {st.session_state.sop_instruction}")
            st.caption(
                "*This helper references cash room safe limits, register audit sheets, and exit code placements to keep operations fully compliant.*")