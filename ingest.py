import os
import chromadb
from pathlib import Path
import pandas as pd
import PyPDF2
from docx import Document
from sentence_transformers import SentenceTransformer
import uuid
import shutil


class DocumentIngester:
    def __init__(self, persist_dir="./chroma_db", reset=False):
        self.persist_dir = persist_dir

        if reset:
            shutil.rmtree(persist_dir, ignore_errors=True)
            print("Old DB deleted.")

        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        print("Model loaded.")

        self.client = chromadb.PersistentClient(path=persist_dir)

        self.collection = self.client.get_or_create_collection(
            name="documents",
            metadata={"hnsw:space": "cosine"}
        )

    # -------------------------
    def clean_text(self, text):
        return "\n".join([line.strip() for line in text.splitlines() if line.strip()])

    # -------------------------
    def extract_text_from_pdf(self, file_path):
        text = ""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    content = page.extract_text()
                    if content:
                        text += content + "\n"
        except Exception as e:
            print(f"Error reading PDF {file_path}: {e}")
        return text

    def extract_text_from_docx(self, file_path):
        text = ""
        try:
            doc = Document(file_path)
            for para in doc.paragraphs:
                text += para.text + "\n"
        except Exception as e:
            print(f"Error reading DOCX {file_path}: {e}")
        return text

    def extract_text_from_excel(self, file_path):
        text = ""
        try:
            ext = Path(file_path).suffix.lower()

            if ext == ".csv":
                df = pd.read_csv(file_path)
                text += df.astype(str).apply(lambda x: " | ".join(x), axis=1).str.cat(sep="\n")
            else:
                xls = pd.ExcelFile(file_path)
                for sheet in xls.sheet_names:
                    df = pd.read_excel(file_path, sheet_name=sheet)
                    text += f"\n--- Sheet: {sheet} ---\n"
                    text += df.astype(str).apply(lambda x: " | ".join(x), axis=1).str.cat(sep="\n")

        except Exception as e:
            print(f"Error reading Excel {file_path}: {e}")
        return text

    def extract_text(self, file_path):
        ext = Path(file_path).suffix.lower()

        if ext == '.pdf':
            return self.extract_text_from_pdf(file_path)
        elif ext == '.docx':
            return self.extract_text_from_docx(file_path)
        elif ext in ['.xlsx', '.xls', '.csv']:
            return self.extract_text_from_excel(file_path)
        else:
            print(f"Skipping unsupported: {file_path}")
            return ""

    # -------------------------
    def ingest_documents(self, folder_path):
        supported_exts = ["*.pdf", "*.docx", "*.xlsx", "*.xls", "*.csv"]

        files_found = []
        for ext in supported_exts:
            files_found.extend(Path(folder_path).rglob(ext))

        print(f"\n📂 Files found: {len(files_found)}")

        if len(files_found) == 0:
            print("❌ NO FILES FOUND → CHECK PATH")
            return

        for file_path in files_found:
            print(f"\nProcessing: {file_path}")

            raw_text = self.extract_text(str(file_path))
            raw_text = self.clean_text(raw_text)

            print(f"Text length: {len(raw_text)}")

            if len(raw_text) < 50:
                print("⚠️ Empty or too small, skipping")
                continue

            sections = raw_text.split("\n\n")

            print(f"Sections: {len(sections)}")

            chunks = [sec.strip() for sec in sections if len(sec.strip()) > 50]

            print(f"Chunks created: {len(chunks)}")

            if len(chunks) == 0:
                print("❌ No chunks → skipping")
                continue

            embeddings = self.model.encode(chunks).tolist()
            ids = [str(uuid.uuid4()) for _ in chunks]
            metadatas = [{"source": str(file_path)} for _ in chunks]

            self.collection.add(
                ids=ids,
                documents=chunks,
                metadatas=metadatas,
                embeddings=embeddings
            )

            print("✅ Added to DB")

        count = self.collection.count()
        print(f"\n📊 TOTAL RECORDS IN DB: {count}")

    # -------------------------
    def query(self, query_text):
        count = self.collection.count()
        print(f"\n📊 DB Count before query: {count}")

        if count == 0:
            print("❌ DB EMPTY → INGEST FAILED")
            return

        results = self.collection.query(
            query_texts=[query_text],
            n_results=3
        )

        print("\n🔍 RESULTS:\n")

        for doc in results["documents"][0]:
            print("--------------------")
            print(doc)


# -------------------------
if __name__ == "__main__":
    ingester = DocumentIngester(reset=True)

    ingester.ingest_documents(
        r"D:\Lisha\Documents"
    )

    ingester.query("Review Frequency of Fraud Risk")