#!/usr/bin/env python3
import os
import fitz  # PyMuPDF for PDFs
import pypandoc  # for converting .md
from tqdm import tqdm
from dotenv import load_dotenv  # ✅ NEW
from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer

# =========================
# CONFIG
# =========================
load_dotenv()  # ✅ loads variables from .env into os.environ
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

if not PINECONE_API_KEY:
    raise ValueError("❌ Pinecone API key not found. Did you set it in .env?")

INDEX_NAME = "doc-embeddings-e5"

# load multilingual-e5-large model
print("Loading multilingual-e5-large model...")
model = SentenceTransformer("intfloat/multilingual-e5-large")

# =========================
# 1. Extract text
# =========================
def extract_pdf_text(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text("text") + "\n"
    return text

def extract_md_text(md_path):
    return pypandoc.convert_file(md_path, "plain")

docs = {
    "doc1.pdf": extract_pdf_text("/Users/shriya/Documents/GitHub/logo_detect/hackbuild-Elite/backend/market_pdf/Principle_Marketing.pdf"),
    "doc2.pdf": extract_pdf_text("/Users/shriya/Documents/GitHub/logo_detect/hackbuild-Elite/backend/market_pdf/ultimate-guide-to-digital-marketing.pdf"),
    "README.md": extract_md_text("/Users/shriya/Documents/GitHub/logo_detect/hackbuild-Elite/backend/market_pdf/README.md")
}

# =========================
# 2. Create Embeddings with multilingual-e5-large
# =========================
def embed_text(text, doc_name, chunk_size=500):
    chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
    vectors = []
    for i, chunk in enumerate(tqdm(chunks, desc=f"Embedding {doc_name}")):
        embedding = model.encode("passage: " + chunk).tolist()
        vectors.append({
            "id": f"{doc_name}_{i}",
            "values": embedding,
            "metadata": {"source": doc_name, "text": chunk}
        })
    return vectors

all_vectors = []
for doc_name, text in docs.items():
    all_vectors.extend(embed_text(text, doc_name))

# =========================
# 3. Store in Pinecone
# =========================
# =========================
# 3. Store in Pinecone (with batching)
# =========================
print("Connecting to Pinecone...")
pc = Pinecone(api_key=PINECONE_API_KEY)

if INDEX_NAME not in pc.list_indexes().names():
    pc.create_index(
        name=INDEX_NAME,
        dimension=1024,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1")
    )

index = pc.Index(INDEX_NAME)

# ✅ batch upserts (e.g. 100 vectors per request)
def batch_upsert(vectors, batch_size=100):
    for i in range(0, len(vectors), batch_size):
        batch = vectors[i:i + batch_size]
        index.upsert(vectors=batch)
        print(f"Upserted batch {i//batch_size + 1}/{(len(vectors) + batch_size - 1)//batch_size}")

batch_upsert(all_vectors, batch_size=100)

print(f"✅ Stored {len(all_vectors)} embeddings in Pinecone index '{INDEX_NAME}'")
