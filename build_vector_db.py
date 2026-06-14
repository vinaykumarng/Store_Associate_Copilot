import os
import pandas as pd
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings


def load_and_format_data():
    documents = []

    # 1. Load newly formatted Inventory
    if os.path.exists('data/inventory.csv'):
        df_inv = pd.read_csv('data/inventory.csv')
        for _, row in df_inv.iterrows():
            # Formatted to perfectly match the JSON extracted fields
            text = f"Product: {row['Product_Name']} (SKU: {row['SKU']}) | Brand: {row['Brand']} | Category: {row['Category']} | Stock: {row['Stock_Count']} available | Price: ${row['Price']} | Location: {row['Aisle']}, Section {row['Section']}, {row['Shelf']}."
            documents.append(text)

    # 2. Load newly formatted Offers
    if os.path.exists('data/offers.csv'):
        df_off = pd.read_csv('data/offers.csv')
        for _, row in df_off.iterrows():
            text = f"Active Promotion [{row['Promo_Tag']}]: {row['Product_Name']} (SKU: {row['SKU']}) | Offer Type: {row['Offer_Type']} | Details: {row['Description']} | Discount Price: ${row['Offer_Price']}."
            documents.append(text)

    # 3. Load Text Files (SOPs, Substitutions, Planogram)
    for filename in ['substitutes.txt', 'SOP.txt', 'planogram.txt']:
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
                # Split by double newline to treat each product/SOP/substitution block as a unique vector
                paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
                for para in paragraphs:
                    documents.append(f"Source Document ({filename}):\n{para}")

    return documents


def build_vector_store():
    print("Extracting text blocks from converted files...")
    docs = load_and_format_data()

    if not docs:
        print("Error: No documents found. Please run convert_data.py first.")
        return

    print("Loading Local Embeddings Engine (all-MiniLM-L6-v2)...")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    print(f"Creating FAISS vector database from {len(docs)} text segments...")
    vector_store = FAISS.from_texts(docs, embeddings)

    vector_store.save_local("faiss_store_index")
    print("Vector database successfully built and stored in 'faiss_store_index/'.")


if __name__ == "__main__":
    build_vector_store()