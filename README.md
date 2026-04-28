# Local RAG-based Document Q&A System for Financial Services (NBFC Use Case)

A fully **local**, secure, and lightweight RAG-based Question Answering (Q&A) system designed for internal policy documents within an NBFC.  
This system enables employees to ask natural language questions and receive **accurate, document-grounded answers** with **source attribution**—all while ensuring **no data leaves the organization’s infrastructure**.

---

# Project Overview

NBFCs maintain a large and frequently updated set of internal documents—policies, credit guidelines, operational manuals, compliance circulars, and more.  
Employees often struggle to locate specific details quickly.

This system solves that through:

- Local LLM (Mistral via Ollama)  
- Local vector DB (ChromaDB)  
- Local embeddings (Sentence Transformers)  
- A user-friendly Streamlit interface  

**No cloud, no external API calls. Fully on-device.**

---

# Tech Stack

- **Interface:** Streamlit  
- **LLM:** Mistral (Ollama)  
- **Embeddings:** all-MiniLM-L6-v2 (Sentence Transformers)  
- **Vector Store:** ChromaDB  
- **File Support:** PDF, DOCX, XLSX, CSV  
- **Backend:** Python  

---

# System Architecture



---

# 💡 Design Decisions
## 🤖 LLM Selection

### ✅ Chosen Model: **Mistral (via Ollama)**

### **Why this choice?**
- Fully local execution (critical for financial compliance)
- Strong reasoning ability for structured & policy-based Q&A
- Lightweight compared to larger LLMs
- Easy deployment using Ollama

---

### 🔍 LLM Comparison

| Model | Pros | Cons | Decision |
|-------|------|------|----------|
| **Mistral (Ollama)** | Fast, strong reasoning, runs locally | Slightly weaker than GPT-4 | ✅ **Selected** |
| **LLaMA 2** | Powerful open-source model | Heavy, high RAM usage | ❌ Not chosen |
| **Phi-2** | Very lightweight | Weak reasoning for policy Q&A | ❌ Not chosen |
| **OpenAI APIs** | Excellent performance | External API → data privacy risk | ❌ Rejected |

---

## 🔎 Embedding Model

### ✅ Selected: **all-MiniLM-L6-v2**

### **Why?**
- Fast CPU inference
- Strong semantic similarity for policy documents
- Lightweight (~100MB)
- Ideal for real-time retrieval pipelines

---

### 🔍 Embedding Comparison

| Model | Pros | Cons | Decision |
|--------|------|------|----------|
| **all-MiniLM-L6-v2** | Fast, lightweight, good accuracy | Slight dip vs larger models | ✅ **Selected** |
| **BGE Models** | Higher semantic accuracy | Heavy, slower locally | ❌ Not chosen |
| **E5 Models** | Excellent retrieval quality | Higher inference cost | ❌ Not chosen |
| **OpenAI Embeddings** | Top-tier performance | Cloud dependency | ❌ Rejected |

---

## 🗄️ Vector Database

### ✅ Selected: **ChromaDB (Local)**

### **Why?**
- Fully local → meets strict NBFC privacy requirements
- Persistent storage on disk
- Simple, clean Python API
- Lightweight and easy to deploy

---

### 🔍 Vector DB Comparison

| Database | Pros | Cons | Decision |
|-----------|------|------|----------|
| **ChromaDB** | Local, simple API, persistent storage | Limited horizontal scaling | ✅ **Selected** |
| **FAISS** | Extremely fast similarity search | No metadata storage | ❌ Not chosen |
| **Weaviate** | Feature-rich, hybrid search | Requires running a separate service | ❌ Not chosen |
| **Pinecone** | Highly scalable | Cloud-based → violates data constraints | ❌ Rejected |

---
## ✂️ Chunking Strategy Used

### ✅ Section-Based (Paragraph-Level) Chunking

The system uses a **section-based chunking strategy**, splitting documents at natural paragraph boundaries to preserve meaningful context.

### 📌 Key Points
- Splits text at paragraph breaks  
- Filters out very small or noisy sections  
- Creates **non-overlapping** chunks  
- Ensures each chunk is context-rich and usable  

### 🎯 Why This Approach
- Aligns well with structured policy documents  
- Improves retrieval accuracy  
- Lightweight and efficient for local systems  

### ⚠️ Limitations
- Cannot capture cross-section context  
- Rule-based (no semantic understanding)  

### 📝 Summary

---
# 🚀 Installation & Setup

## 1. Clone the repository
```bash
git clone https://github.com/<your-username>/<repo-name>.git
cd <repo-name>
```
## 2. Install dependencies
```bash
pip install -r requirements.txt
```
## 3. Install Ollama
Download from: https://ollama.com/download

## 4. Pull the model
```bash
ollama pull mistral
```
## 5. Run the application
```bash
streamlit run app.py
```
# How It Works (End-to-End)

# Limitations
- Weak performance on complex multi-document reasoning
- No reranking model
- Limited handling of unstructured PDFs
- UI does not highlight exact answer spans
# Future Improvements
Semantic chunking

📘 Learning Journal (7-Day Journey)
Day 1

Understood the problem, designed architecture, explored LLMs (Phi, LLaMA3, Mistral), selected embeddings and vector DB.

Day 2

Built ingestion pipeline, tested chunking strategies, improved chunk quality.

Day 3

Integrated LLM using Ollama, handled RAM constraints, designed strict anti-hallucination prompt.

Day 4

Tested system end-to-end, fixed incomplete answers, improved retrieval & filtering.

Day 5

Added Excel & PDF improvements, tested across various document types.

Day 6

Handled edge cases, added rejection logic, improved reliability and consistency.

🔧 Key Challenges
Chunk quality → improved filtering
RAM limitations → optimized model choice
Hallucination → strict prompting + rejection logic
Retrieval accuracy → distance thresholds + filtering
🔁 One Decision Reversed

Initially: Used basic chunking → resulted in poor quality retrieval
Revised: Switched to filtered, section-based chunking → major accuracy improvement

✅ What Works Well
Accurate policy-based answers
Strong hallucination control
Fully local system (NBFC-compliant)
Clean and intuitive UI
⚠️ What Doesn’t Work Well
Complex multi-document reasoning
Weak handling of unstructured PDFs
No reranking to boost retrieval precision
