import os
import chromadb
from sentence_transformers import SentenceTransformer
import requests
from pathlib import Path

# =========================
# CACHE
# =========================
os.environ["HF_HOME"] = r"D:\hf_cache"
os.environ["TRANSFORMERS_CACHE"] = r"D:\hf_cache"


# =========================
# MODEL SINGLETON
# =========================
class EmbeddingModel:
    _model = None

    @staticmethod
    def get():
        if EmbeddingModel._model is None:
            print("Loading embedding model...")
            EmbeddingModel._model = SentenceTransformer(
                "all-MiniLM-L6-v2",
                cache_folder=r"D:\hf_cache",
                device="cpu"
            )
        return EmbeddingModel._model


# =========================
# MAIN ENGINE
# =========================
class DocumentQuery:
    def __init__(self, persist_dir="./chroma_db"):
        self.model = EmbeddingModel.get()
        self.client = chromadb.PersistentClient(path=persist_dir)

        try:
            self.collection = self.client.get_collection(name="documents")
        except:
            raise Exception("❌ No collection found. Run ingestion first.")

    # =========================
    # RETRIEVAL
    # =========================
    def query(self, query_text, n_results=10, distance_threshold=0.5, final_k=4):

        query_embedding = self.model.encode(
            [query_text],
            normalize_embeddings=True
        ).tolist()

        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=n_results
        )

        docs = results["documents"][0]
        metas = results["metadatas"][0]
        dists = results["distances"][0]

        # =========================
        # 🔥 NEW: HARD REJECTION LOGIC
        # =========================
        if not dists:
            print("❌ No results returned from DB")
            return [], [], []

        best_dist = min(dists)

        # If everything is too far → DO NOT FALLBACK (prevents hallucination)
        if best_dist > 0.8:
            print("❌ No relevant match found (distance too high)")
            return [], [], []

        # keep your original filtering but safer
        filtered = [
            (doc, meta, dist)
            for doc, meta, dist in zip(docs, metas, dists)
            if dist < distance_threshold
        ]

        # fallback ONLY if still empty, but now controlled
        if len(filtered) == 0:
            print("⚠️ No good matches within threshold, using top results (SAFE MODE)")
            filtered = list(zip(docs, metas, dists))

        filtered.sort(key=lambda x: x[2])
        top_results = filtered[:final_k]

        final_docs = [x[0] for x in top_results]
        final_metas = [x[1] for x in top_results]
        final_dists = [x[2] for x in top_results]

        print("\n🎯 Selected Chunks:")
        for d in final_dists:
            print(f"Distance: {d:.3f}")

        return final_docs, final_metas, final_dists

    # =========================
    # ANSWER GENERATION (SIMPLE)
    # =========================
    def generate_answer(self, query_text, docs, metas):
        
        # =========================
        # 🔥 NEW: NO CONTEXT → NO LLM CALL
        # =========================
        if not docs or len(docs) == 0:
            return (
                "Answer: Not found in documents\nConfidence: 0",
                [], 
                ""
            )

        context = "\n\n".join(docs[:4])
        print("\n🧱 CONTEXT SIZE:", len(context))

        prompt = f"""
You are a STRICT document-grounded question answering system for a Financial Services compliance environment.

Your job is to answer ONLY using the provided context from internal policy documents.

========================
CRITICAL RULES (MANDATORY)
========================
1. Use ONLY the information present in the context below.
2. NEVER use outside knowledge, assumptions, or inference.
3. If the answer is not explicitly present in the context, respond exactly:
   Answer: Not found in documents
   Confidence: 0
4. Do NOT hallucinate or guess missing details.
5. Keep answers short, precise, and factual (max 5–6 lines).
6. Prefer quoting or close paraphrasing from context.
7. Every answer MUST include source citation with:
   - Document Name
   - Section/Paragraph

========================
CONFIDENCE SCORING RULES (VERY IMPORTANT)
========================
Assign a confidence score from 0 to 100 based ONLY on:

- 90–100 → Answer is explicitly stated in context (direct match or near-verbatim)
- 70–89  → Answer is clearly present but requires combining 2–3 context parts
- 40–69  → Partial information available, some ambiguity exists
- 10–39  → Weak relevance, mostly inferred (but still grounded)
- 0      → No relevant information found

DO NOT give high confidence unless context directly supports the answer.

======================== HEADING EXTRACTION RULES ========================
Extract the heading from the MOST RELEVANT paragraph used to answer.
Heading = ?
Rules:
1. The section may contain numbered headings like:
   - "1.3 Objectives"
   - "2 Introduction"
   - "4.2.1 Scope"
2. If a line starts with a numbering pattern (digits separated by dots):
   - Extract ONLY the heading text (ignore numbers)
   - Example: "1.3 Objectives" → "Objectives"
3. If no numbered heading is found:
   - Line length must be between 5 and 80 characters
   - Must satisfy at least one:
     a) Fully uppercase
     b) Title Case
     c) Ends with a colon (:)
4. Return the FIRST valid heading found from the relevant section.
5. If no valid heading is found: Return "General"

======================== SECTION EXTRACTION RULES ========================
Extract the section number from the MOST RELEVANT paragraph used.
Section = ?
Rules:
1. Valid formats:
   - "1"
   - "1.2"
   - "2.3.4"
2. Must:
   - Appear at the START of a line
   - Contain digits separated by dots
3. Examples:
   - "1 Introduction" → "1"
   - "1.2 Scope" → "1.2"
   - "3.4.5 Details" → "3.4.5"
4. Return the FIRST valid section number found.
5. If no section number is found: Return None

========================
OUTPUT FORMAT (STRICT)
========================
FORMAT:
Answer: <your answer>

leave a blank line for space

Sources:<Section>

leave a blank line for space

Confidence: <0 to 1>


========================
CONTEXT
========================
{context}

========================
QUESTION
========================
{query_text}

========================
FINAL ANSWER
========================
"""
 
        response = requests.post(
            "http://localhost:11434/api/chat",
            json={
                "model": "mistral",
                "messages": [
                    {
                        "role": "system",
                        "content": "Follow format strictly. No extra text."
                    },
                    {"role": "user", "content": prompt}
                ],
                "stream": False,
                "options": {
                    "temperature": 0,
                    "num_predict": 200
                }
            }
        )

        output = response.json()["message"]["content"].strip()

        return output, metas, context


# =========================
# RUNNER
# =========================
if __name__ == "__main__":
    query_engine = DocumentQuery()

    while True:
        q = input("\nAsk: ")

        if q.lower() == "exit":
            break

        docs, metas, dists = query_engine.query(q)

        result, metas, context = query_engine.generate_answer(q, docs, metas)

        file_name = Path(metas[0]["source"]).name if metas else "Unknown"

        print("\n========================")
        print(result)
        print("\n📄 Source:", file_name)

        