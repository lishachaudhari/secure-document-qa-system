import streamlit as st
import os
from ingest import DocumentIngester
from query import DocumentQuery
from pathlib import Path

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="Secure Document Q&A", layout="wide")

st.title("📄 Secure Document Q&A System (Financial Services)")

# =========================
# HELPERS
# =========================
def is_db_available():
    return os.path.exists("chroma_db") and len(os.listdir("chroma_db")) > 0


# =========================
# SESSION STATE INIT
# =========================
if "query_engine" not in st.session_state:
    if is_db_available():
        st.session_state.query_engine = DocumentQuery()
        st.session_state.ingested = True
    else:
        st.session_state.query_engine = None
        st.session_state.ingested = False


# =========================
# SIDEBAR - INGESTION
# =========================
st.sidebar.header("📥 Document Setup (Optional)")

if is_db_available():
    st.sidebar.info("📚 Existing knowledge base detected")
else:
    st.sidebar.warning("⚠️ No documents indexed yet")

uploaded_files = st.sidebar.file_uploader(
    "Upload new documents (optional)",
    type=["pdf", "docx", "xlsx", "xls", "csv"],
    accept_multiple_files=True
)

if st.sidebar.button("🚀 Process Documents"):

    save_path = "temp_docs"
    os.makedirs(save_path, exist_ok=True)

    # CASE 1: Upload new docs
    if uploaded_files:
        with st.spinner("Processing uploaded documents..."):
            for file in uploaded_files:
                with open(os.path.join(save_path, file.name), "wb") as f:
                    f.write(file.getbuffer())

            ingester = DocumentIngester()
            ingester.ingest_documents(save_path)

        st.session_state.query_engine = DocumentQuery()
        st.session_state.ingested = True

        st.sidebar.success(f"✅ {len(uploaded_files)} new documents indexed!")

    # CASE 2: Use existing DB
    elif is_db_available():
        st.session_state.query_engine = DocumentQuery()
        st.session_state.ingested = True

        st.sidebar.success("✅ Using existing indexed documents!")

    # CASE 3: Nothing available
    else:
        st.sidebar.error("❌ No documents found. Upload at least once.")


# =========================
# MAIN UI - Q&A
# =========================
st.subheader("💬 Ask a Question")



query = st.text_input(
    "Enter your question:",
    placeholder="Ask here..."
)

if st.button("Get Answer"):

    if not st.session_state.query_engine:
        st.warning("⚠️ No document base available. Upload or process documents first.")
        st.stop()

    elif not query.strip():
        st.warning("Please enter a question.")
        st.stop()

    else:
        with st.spinner("🔎 Searching documents and generating answer..."):

            engine = st.session_state.query_engine

            # Retrieve docs
            docs, metas, dists = engine.query(query)

            # ❌ No answer found
            if not docs or len(docs) == 0:
                st.warning("❌ No relevant information found in documents.")
                st.write("📊 Confidence: 0")
                st.stop()

            # Generate answer
            answer, metas, context = engine.generate_answer(query, docs, metas)

        st.success("Answer generated!")
        data = metas[0]['source']
        file_name = Path(data).name

        # =========================
        # ANSWER
        # =========================
        st.markdown("## 🧠 Answer")
        st.write(answer)
        st.write(f"Document name: {file_name}")

     

