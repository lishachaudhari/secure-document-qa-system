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
# Setup Instructions

 # Installation & Setup

## 1. Install dependencies
```bash
pip install -r requirements.txt
```
## 2. Install Ingestion Documents file 
Before running the ingestion script, download or place your sample documents in a local folder.
Then update the file path in ingest.py:
```bash
 ingester.ingest_documents(
        r"Enter the file path of Documents folder"
    )
```
After updating the path, run:

```bash
python ingest.py
```
## 3. Install Ollama
Download from: https://ollama.com/download

## 4. Pull the model
Note that Mistral runs fine on 8GB RAM
```bash
ollama pull mistral
```
## 5. Run the application
```bash
streamlit run app.py
```
## Application UI (Example)

Here is a sample screenshot of the Streamlit interface showing the upload area, query box, and answer display.
<img width="1919" height="983" alt="image" src="https://github.com/user-attachments/assets/ee48a5f5-d8fd-46a6-a6d0-5f45cc945e5d" />

---
### Without uploading Documents 
1. Click Ingest to process them
2. After ingestion completes, enter your query
3. Click Ask

---
### With uploading Documents
1. Upload documents (not ingested yet)
2. Click Ingest to process them
3. After ingestion completes, enter your query
4. Click Ask
   
<p align="center">
  <img src="https://github.com/user-attachments/assets/e8b7b898-52fb-49a1-a5d2-2e1a57836c48" width="45%" />
  <img src="https://github.com/user-attachments/assets/a83dd944-c75b-4a73-9c3e-87596cc26bdc" width="45%" />
</p>

---

# README — Design Decisions
# Tech Stack

- **Interface:** Streamlit  
- **LLM:** Mistral (Ollama)  
- **Embeddings:** all-MiniLM-L6-v2 (Sentence Transformers)  
- **Vector Store:** ChromaDB  
- **File Support:** PDF, DOCX, XLSX, CSV  
- **Backend:** Python  

---

# System Architecture
<img width="2816" height="1536" alt="Architecture Image" src="https://github.com/user-attachments/assets/fdc22250-7c52-4d1d-86a7-91341efb31cd" />

When the user uploads documents, the system reads them, splits them into paragraphs, converts each paragraph into embeddings, and stores them in ChromaDB. When a query arrives, we embed the query, find the top-k similar chunks, and send them + the question to the local Mistral model to generate an answer with citations

---

# Design Decisions

## Why This Architecture Meets NBFC Compliance
- Ollama LLM runs fully offline, ensuring no policy or customer data leaves the device.
- ChromaDB stores vectors locally on disk, satisfying internal data residency rules.
- Sentence Transformer embeddings run offline, with no API calls.
- Streamlit UI does not transmit data externally, all operations occur inside local environment.
---
## LLM Selection

### Chosen Model: **Mistral (via Ollama)**

### **Why this choice?**
- Fully local execution (critical for financial compliance)
- Strong reasoning ability for structured & policy-based Q&A
- Lightweight compared to larger LLMs
- Easy deployment using Ollama

---

### LLM Comparison

| Model | Pros | Cons | Decision |
|-------|------|------|----------|
| **Mistral (Ollama)** | Fast, strong reasoning, runs locally | Slightly weaker than GPT-4 | ✅ **Selected** |
| **LLaMA 2** | Powerful open-source model | Heavy, high RAM usage | ❌ Not chosen |
| **Phi-2** | Very lightweight | Weak reasoning for policy Q&A | ❌ Not chosen |
| **OpenAI APIs** | Excellent performance | External API → data privacy risk | ❌ Rejected |

---

## Embedding Model

### Selected: **all-MiniLM-L6-v2**

### **Why?**
- Fast CPU inference
- Strong semantic similarity for policy documents
- Lightweight (~100MB)
- Ideal for real-time retrieval pipelines

---

### Embedding Comparison

| Model | Pros | Cons | Decision |
|--------|------|------|----------|
| **all-MiniLM-L6-v2** | Fast, lightweight, good accuracy | Slight dip vs larger models | ✅ **Selected** |
| **BGE Models** | Higher semantic accuracy | Heavy, slower locally | ❌ Not chosen |
| **E5 Models** | Excellent retrieval quality | Higher inference cost | ❌ Not chosen |
| **OpenAI Embeddings** | Top-tier performance | Cloud dependency | ❌ Rejected |

---

## Vector Database

### Selected: **ChromaDB (Local)**

### **Why?**
- Fully local → meets strict NBFC privacy requirements
- Persistent storage on disk
- Simple, clean Python API
- Lightweight and easy to deploy

---

### Vector DB Comparison

| Database | Pros | Cons | Decision |
|-----------|------|------|----------|
| **ChromaDB** | Local, simple API, persistent storage | Limited horizontal scaling | ✅ **Selected** |
| **FAISS** | Extremely fast similarity search | No metadata storage | ❌ Not chosen |
| **Weaviate** | Feature-rich, hybrid search | Requires running a separate service | ❌ Not chosen |
| **Pinecone** | Highly scalable | Cloud-based → violates data constraints | ❌ Rejected |

---
## Chunking Strategy Used

### Section-Based (Paragraph-Level) Chunking

The system uses a **paragraph-level chunking approach**, where document text is split based on natural paragraph or section boundaries. Each paragraph is treated as an individual chunk, and very small or irrelevant sections are filtered out to ensure only meaningful content is stored. This results in clean, non-overlapping chunks that preserve the original structure of the document.

### Why This Approach

This strategy works well for policy and financial documents, which are typically structured into sections and paragraphs. By preserving this structure, each chunk retains enough context to answer queries effectively. It also improves retrieval accuracy while keeping the system lightweight and efficient, which is important for a fully local setup with limited computational resources.

#### Why Not Fixed Token Size?
Fixed-size chunks (200–500 tokens) were rejected because financial policy documents have structured paragraphs, definitions, and tables. Cutting mid-paragraph reduces semantic meaning and introduces hallucinations.

#### Why No Overlap?
Overlapping chunks increase storage and latency. Policy documents are already cleanly structured, so paragraph-level boundaries provide enough context without overlap.

---
### Retrieval Alternatives Considered
| Approach                          | Why Not Used                                                           |
| --------------------------------- | ---------------------------------------------------------------------- |
| Fixed-size token chunking         | Breaks policy paragraphs and reduces context quality                   |
| Overlapping chunks                | Higher latency + more disk usage with minimal accuracy gain            |
| Hybrid search (BM25 + embeddings) | Requires additional infra; unnecessary for structured policy documents |
| Re-ranking model                  | Too heavy for fully local CPU-only deployment                          |
| Summarized chunks                 | Risk of losing compliance-critical details                             |

---

# How It Works (End-to-End)
<img width="2816" height="1536" alt="Workflow image" src="https://github.com/user-attachments/assets/2dbfd137-e731-4f96-9f80-a8c78a896708" />

# Limitations
- Weak performance on complex multi-document reasoning
- No reranking model
- Limited handling of unstructured PDFs
- UI does not highlight exact answer spans
- Struggles with questions requiring synthesis across multiple documents
(e.g., combining KYC and Underwriting guidelines in one answer)
- Fails on scanned/image-based PDFs
because no OCR pipeline is implemented.

# What Works Well
- Accurate for section-specific and definition-based queries
  (e.g., “What are KYC requirements?” or “What is the loan approval limit?”)
- Strong hallucination control
  The model is constrained to retrieved chunks, reducing generation of unsupported answers
- Reliable performance on structured policy documents
  Paragraph-based chunking preserves context effectively
- Fully local and NBFC-compliant architecture
  No external API calls, ensuring data privacy
- Clean and intuitive UI for non-technical users

# ❌ What Doesn’t Work Well
- Struggles with multi-document reasoning
  Cannot reliably combine information across multiple policies in a single answer
- Weak performance on unstructured or scanned PDFs
  No OCR or layout-aware parsing implemented
- No re-ranking step
  Retrieved chunks may not always be the most relevant, affecting answer quality
- Limited contextual understanding for vague queries
  (e.g., “Explain the process” without specifying a policy area)
--- 
# README — Learning Journal

## Day 1 — Starting Point

I started with a clear idea of the final output, but I will be honest:
I had never run a local LLM before and had never built a full RAG pipeline end-to-end. I only had theoretical understanding.

I spent Day 1 breaking the problem into parts: ingestion → chunking → embeddings → retrieval → LLM response.
Explored small and medium LLMs (Phi, LLaMA3, Mistral) to see which ones could realistically run on my laptop.
Sketched the initial architecture and selected a simple embeddings + vector DB setup.

---
## Day 2 — Ingestion and Chunking Experiments

I built the ingestion pipeline and quickly realized how tricky chunking actually is.

What didn’t work:

First attempt used very large chunks, causing irrelevant retrieval.
Second attempt used very small chunks, losing context.
Tried semantic/heading-based splitting, but it broke PDFs and tables badly.

After several rounds of testing, I chose fixed-size chunking with small overlaps because it provided the most consistent results across document types.

Reasoning:
Consistency mattered more than being smart, especially with messy PDFs.

---
## Day 3 — Local LLM Setup & RAM Limitations

I integrated Ollama today. This is where the biggest challenge appeared:

RAM was not enough.

I tried:

LLaMA3 → system froze
Mistral  → worked
Running multiple tools at once → slowed everything
Phi4-mini → poor reasoning

I had to switch to a  Mistral model, close background apps, and optimize the process.
This forced me to be more resource-aware.

I also created a strict anti-hallucination prompt because initial responses included guesses when information wasn’t available.

---
## Day 4 — First End-to-End Test & Retrieval Tuning

Ran the full pipeline end-to-end for the first time.
Results were mixed:

Some answers were incomplete
Some answers pulled unrelated chunks
Sometimes too many chunks were retrieved

I tuned the similarity threshold, added filtering logic, and tested multiple combinations.

Key decision:
Increase relevance threshold to reduce noise.
This resulted in clearer and more focused answers.

---
## Day 5 — Handling PDFs, Excel & Parsing Issues

Now I focused on document formats.
PDFs with tables produced broken text. Excel files pulled merged cells in strange ways.

Things I tried that did not work:

A PDF parser that reordered text randomly
An Excel extractor that ignored formatting
A naive table parser that created garbled output

After testing alternatives, I selected a stable PDF parser and improved preprocessing for Excel files.
Cleaned and normalized extracted text to make it reliable for embeddings.

---
## Day 6 — Edge Cases, Rejection Logic & Final Refinement

Tested edge cases like:

Questions not present in the document
Ambiguous questions
Very short or overly specific queries

Earlier, the model guessed answers.
I added rejection logic so the system cleanly responds with “Not found in the document” instead of hallucinating.

Also refined the prompt again for consistency.
After multiple document tests, responses became stable and predictable.

---
##  One Design Decision I Reversed

Initially, I tried fixed-size chunking with overlap.
However, it broke the natural structure of policy documents and reduced context quality.

I switched to paragraph-level chunking, which preserved document structure and gave more meaningful and accurate retrieval results.

---
## Resources That Helped Me

Throughout the 6 days, I used:

- Ollama documentation
- LangChain documentation (mainly for understanding chunking & embeddings concepts)
- YouTube tutorials on RAG basics
- StackOverflow for parsing issues
- Blog posts on PDF extraction challenges
- ChatGPT for debugging and code explanations
- Google Code assistance for coding.

These were essential since I did not know many of these topics on Day 1.

 
