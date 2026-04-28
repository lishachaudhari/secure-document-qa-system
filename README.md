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

