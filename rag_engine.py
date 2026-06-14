import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_community.chat_models import ChatOllama
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

load_dotenv()


class StoreCopilotEngine:
    def __init__(self):
        # Load local embedding pipeline
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

        if os.path.exists("faiss_store_index"):
            self.db = FAISS.load_local("faiss_store_index", self.embeddings, allow_dangerous_deserialization=True)
        else:
            self.db = None
            print("Warning: Vector DB folder not found. Please execute build_vector_db.py first.")

        # 1. Instantiate Groq LLM Client
        self.groq_llm = ChatGroq(
            groq_api_key=os.getenv("GROQ_API_KEY", "dummy_key"),
            model_name="llama-3.1-8b-instant",
            temperature=0.2
        )

        # 2. Instantiate Local Ollama Client (Llama 3)
        # Note: Ensure you have run `ollama run llama3` in your terminal beforehand.
        self.ollama_llm = ChatOllama(
            model="llama3.1",
            temperature=0.2
        )

    def get_response(self, user_query, chat_history, provider="Groq"):
        if not self.db:
            return "Error: Database is offline. Please build the local knowledge vector indexes."

        # Fetch relevant chunks
        docs = self.db.similarity_search(user_query, k=5)
        context = "\n".join([doc.page_content for doc in docs])

        # Format historical chat data (History limited to 3 via app.py state)
        history_str = ""
        for chat in chat_history:
            history_str += f"Associate: {chat['query']}\nCopilot: {chat['response']}\n"

        system_prompt = f"""
You are the General Store Associate Copilot. Your role is to provide quick, structured, and factual answers regarding stock lookups, aisle placement, promotions/offers, substitutions, and SOP protocols.

CRITICAL LOGICAL RULE & PRECEDENCE ORDER (AVOID GIVING EMPTY LOCATIONS):
- You MUST verify the "Stock" value of the target product in the context before answering.
- If the item's stock count is explicitly 0 (e.g., "Stock: 0 available" or "qty_on_hand: 0"), then the item is PHYSICALLY OUT OF STOCK.
- **CRITICAL BUG prevention:** When an item is out of stock (Stock: 0), you are FORBIDDEN from telling the associate to go to that item's planogram location (aisle/shelf), as sending them to an empty shelf is an error. Bypassing the shelf location entirely, you must follow the instructions below:

1. SMART CROSS-SELL ENGINE (Only for IN-STOCK items):
   - If the product is IN-STOCK (Stock > 0), provide its exact location (Aisle, Section, Shelf). 
   - You MUST also explicitly suggest an associated complementary item to boost sales (using 'Adjacent' items from the planogram context if available).
   - Example style: "Yes, we have it in stock at [Location]. Suggest recommending the adjacent item [Item Name] to complete their purchase."

2. ACTIONABLE ESCALATION FORMAT (Only for OUT-OF-STOCK items):
   - If the target product has "Stock: 0 available", DO NOT give its aisle/shelf location.
   - Instead, check your context for any valid substitutes (from the substitutions document).
   - If there is a valid substitute mentioned in the context, check its stock status. If the substitute is in stock, recommend it and provide its location.
   - If NO valid, in-stock substitutes or alternatives are mentioned in the context, you MUST immediately output the following 'one-click order form' escalation template:
     ---
     [📦 SYSTEM ESCALATION: ITEM OUT OF STOCK]
     "I can order this item directly from our regional warehouse for you. Would you like it shipped directly to your home address or setup for free in-store collection next Tuesday?"
     ---

CONTEXT FOR CURRENT INQUIRY:
{context}

RECENT CONVERSATION HISTORY:
{history_str}

Associate Question: {user_query}
Answer concisely as an operations-focused store assistant:
"""

        # Execute based on UI switch
        try:
            if provider == "Groq":
                response = self.groq_llm.invoke(system_prompt)
            else:
                response = self.ollama_llm.invoke(system_prompt)
            return response.content

        except Exception as e:
            fallback_msg = f"⚠️ **Connection Error with {provider}:** "
            if provider == "Groq":
                fallback_msg += "Please verify your `GROQ_API_KEY` in the `.env` file."
            else:
                fallback_msg += "Ensure Ollama is running in your background (open terminal and type `ollama run llama3`)."
            fallback_msg += f"\n\n*Technical Details: {str(e)}*"
            return fallback_msg

    def get_sop_guidance(self, sop_title, completed_steps, next_step, provider="Groq"):
        """
        Retrieves database context for a specific store checklist step and generates an
        actionable, RAG-guided micro-instruction with safety, department, and process details.
        """
        if not self.db:
            return "Error: Database is offline."

        # Search database for specific SOP checklists & instructions
        query = f"SOP {sop_title} details: {next_step}"
        docs = self.db.similarity_search(query, k=4)
        context = "\n".join([doc.page_content for doc in docs])

        system_prompt = f"""
You are the General Store Operations Copilot. An associate is actively completing a structured store checklist.

SOP Title: {sop_title}
Completed Steps: {', '.join(completed_steps) if completed_steps else 'None (Starting Checklist)'}
Active Step to Perform Now: {next_step}

RELEVANT DATABASE CONTEXT:
{context}

Based on the Active Step and the Store SOP rules in the context above, generate a highly practical, 2-to-3 sentence instruction detailing exactly HOW to perform this active step safely and efficiently on the store floor. 
- Highlight any relevant safety rules, specific locations (e.g., back office, specific departments), or physical tools required (e.g., keypad, temp probes, cash drawer keys).
- Keep it direct, energetic, and professional.
"""
        try:
            if provider == "Groq":
                response = self.groq_llm.invoke(system_prompt)
            else:
                response = self.ollama_llm.invoke(system_prompt)
            return response.content
        except Exception as e:
            return f"Could not generate next instruction. Please perform step: '{next_step}' as documented in the manual."