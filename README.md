# 🛒 General Store Associate Copilot

An AI-powered **Retrieval-Augmented Generation (RAG)** assistant designed for retail store associates. The application provides instant answers regarding stock availability, item locations, active promotions, standard operating procedures (SOPs), and product substitutions.

The copilot combines semantic search, vector databases, and large language models to help associates make faster and more informed decisions during store operations.

---

## ✨ Features

### 🤖 Hybrid LLM Engine

* Supports both **cloud-based inference** using the Groq API and **offline local inference** using Ollama.
* Seamlessly switch between models depending on internet availability and performance requirements.

### 📦 Inventory Intelligence

* Instantly answers questions about:

  * Stock availability
  * Product quantities
  * Shelf locations
  * Product categories

### 🗺️ Planogram Assistance

* Retrieves item locations directly from store planograms.
* Helps associates quickly locate products within the store.

### 🔄 Smart Product Substitutions

* Suggests alternative products when an item is unavailable.
* Uses substitution mappings stored in the knowledge base.

### 🛍️ Cross-Sell Recommendations

* Automatically recommends adjacent products based on planogram relationships.
* Encourages upselling and improves customer experience.

### 🚚 Automated Store Delivery Suggestions

* If an item is completely out of stock and no substitutes exist, the copilot generates a one-click:

  > **"Order for Store Delivery"**
  > recommendation.

### 🎯 Trending Deals Banner

* Automatically parses active offers and promotions.
* Keeps store associates informed about ongoing discounts and campaigns.

### 🧠 Short-Term Conversational Memory

* Maintains the last three conversational turns.
* Preserves context without exceeding LLM token limits.

### 📊 Data Pipeline Converter

* Converts raw retail JSON data into optimized:

  * Text documents
  * CSV datasets
  * Vector embeddings
* Resolves product SKUs into human-readable product names.

---

# 🏗️ System Architecture

```text
Processed Text + CSV Files
        │
        ▼
build_vector_db.py
        │
        ▼
FAISS Vector Database
        │
        ▼
rag_engine.py
        │
        ▼
LLM (Groq / Ollama)
        │
        ▼
Streamlit Dashboard
```

---

# 🛠️ Technology Stack

| Category               | Technology          |
| ---------------------- | ------------------- |
| Frontend               | Streamlit           |
| Backend                | Python              |
| RAG Framework          | Custom RAG Pipeline |
| Vector Database        | FAISS               |
| Embedding Model        | all-MiniLM-L6-v2    |
| Cloud LLM              | Groq API            |
| Local LLM              | Ollama (Llama 3)    |
| Data Processing        | Pandas, JSON        |
| Environment Management | python-dotenv       |

---

# 📂 Project Structure

```text
store_copilot/
│
├── app.py                     # Streamlit dashboard
├── rag_engine.py              # Retrieval and LLM orchestration
├── build_vector_db.py         # Embedding generation and FAISS indexing
├── convert_data.py            # Data preprocessing pipeline
├── requirements.txt
├── .env
│
├── data/
│   ├── inventory.csv
│   ├── offers.csv
│   ├── planogram.txt
│   ├── sops.txt
│   └── substitutions.txt
│
└── vectorstore/
    ├── faiss_index.bin
    └── metadata.pkl
```

---

# 📋 Prerequisites

Before running the project, ensure you have:

* Python 3.9 or above
* Git
* Ollama installed and running
* Groq API Key

---

# 🚀 Installation

## 1. Clone the Repository

```bash
git clone https://github.com/your-username/store-associate-copilot.git
cd store-associate-copilot
```

---

## 2. Create a Virtual Environment

### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

### Linux / macOS

```bash
python -m venv .venv
source .venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Configure Environment Variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
```

---

## 5. Download Local Llama 3 Model

Start Ollama:

```bash
ollama run llama3
```

Verify that Ollama is running:

```bash
ollama list
```

---

## 6. Prepare Raw Data

Place the following files inside the `data/` directory:

```text
inventory.json
offers.json
planogram.json
sops.json
substitutions.json
```

---

## 7. Convert Raw Data

```bash
python convert_data.py
```

This step:

* Parses retail datasets
* Resolves SKUs to product names
* Generates optimized text and CSV files for retrieval

---

## 8. Build the Vector Database

```bash
python build_vector_db.py
```

This step:

* Generates embeddings using `all-MiniLM-L6-v2`
* Creates a local FAISS index
* Stores document metadata

---

## 9. Launch the Application

```bash
streamlit run app.py
```

Open:

```text
http://localhost:8501
```

---

# 💬 Example Queries

### Inventory

* Do we have Coke Zero in stock?
* How many units of Milk are available?
* Is Bread currently available?

### Planogram

* Where is Toothpaste located?
* Which aisle contains Rice?

### Promotions

* What offers are running today?
* Are there any discounts on snacks?

### SOPs

* What is the procedure for damaged items?
* How do I process product returns?

### Substitutions

* Suggest alternatives for Diet Coke.
* What can I recommend instead of Whole Wheat Bread?

---

# 🔄 Retrieval Pipeline

```text
User Query
      │
      ▼
Query Embedding
      │
      ▼
FAISS Similarity Search
      │
      ▼
Relevant Context Retrieval
      │
      ▼
Prompt Construction
      │
      ▼
Groq / Ollama
      │
      ▼
AI Response
```

---

# 🎯 Business Impact

* Reduces associate search time
* Improves customer service quality
* Provides real-time operational assistance
* Increases cross-selling opportunities
* Minimizes dependency on manual SOP lookup
* Enhances inventory decision-making

---

# 🔮 Future Enhancements

* Voice-based interaction
* Barcode and QR scanning support
* Multi-store inventory integration
* Real-time inventory synchronization
* Personalized recommendations
* Analytics dashboard for store managers
* Support for multilingual conversations

---

# 👨‍💻 Developed For

**PS099 – Retail & E-Commerce**

**Sub-domain:** Store Operations
**AI Focus:** Retrieval-Augmented Generation (RAG)

### Problem Statement

Develop a store associate copilot that answers questions regarding:

* Stock locations
* Inventory availability
* Offers and promotions
* Product substitutions
* Store SOPs

---

# 📄 License

This project is developed for educational and research purposes.
