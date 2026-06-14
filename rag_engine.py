import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
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

        # Instantiate fast Groq LLM Client
        self.llm = ChatGroq(
            groq_api_key=os.getenv("GROQ_API_KEY"),
            model_name="llama-3.1-8b-instant",
            temperature=0.2
        )

    def get_response(self, user_query, chat_history):
        if not self.db:
            return "Error: Database is offline. Please build the local knowledge vector indexes."

        # Fetch relevant chunks
        docs = self.db.similarity_search(user_query, k=5)
        context = "\n".join([doc.page_content for doc in docs])

        # Format historical chat data
        history_str = ""
        for chat in chat_history:
            history_str += f"Associate: {chat['query']}\nCopilot: {chat['response']}\n"

        # Adapted for the General Store context instead of Decathlon
        system_prompt = f"""
You are the General Store Associate Copilot. Your role is to provide quick, structured, and factual answers regarding stock lookups, aisle placement, promotions/offers, substitutions, and SOP protocols.

CRITICAL INSTRUCTIONS FOR UNIQUE ENGINE RULES:
1. SMART CROSS-SELL ENGINE:
   - If an associate inquires about any physical product or its category and it IS in stock (Stock > 0), you MUST explicitly suggest an associated complementary item to boost sales. You can use the 'Adjacent' items from the planogram context if available.
   - Example style: "Yes, we have it in Aisle A. Suggest recommending the adjacent item [Item Name] to complete their purchase."

2. ACTIONABLE ESCALATION FORMAT:
   - If a product lookup explicitly states 'Stock: 0 available', check your context for any valid substitutes from the substitution document.
   - If NO direct substitutions or alternatives are mentioned in the immediate file context, you MUST immediately output a 'one-click order form' summary for the customer.
   - Exact template format to print:
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

        response = self.llm.invoke(system_prompt)
        return response.content