"""Build one FAISS index per company from its PDF.

Keeping a separate vector store per company (instead of one store with a
metadata filter) makes access isolation structural: a user's query can only
ever load the FAISS indexes for companies they are allowed to see, so there
is no shared index for a bug in a filter expression to leak past.
"""

from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter

from config import COMPANIES, INDEX_DIR, PDF_DIR

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


def get_embeddings() -> HuggingFaceEmbeddings:
    return HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)


def build_index(company_id: str, embeddings: HuggingFaceEmbeddings) -> None:
    meta = COMPANIES[company_id]
    pdf_path = PDF_DIR / meta["file"]
    if not pdf_path.exists():
        raise FileNotFoundError(
            f"missing {pdf_path}; run generate_sample_pdfs.py first"
        )

    loader = PyPDFLoader(str(pdf_path))
    pages = loader.load()

    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=120)
    chunks = splitter.split_documents(pages)

    for chunk in chunks:
        chunk.metadata["company_id"] = company_id
        chunk.metadata["company_name"] = meta["name"]
        chunk.metadata["source"] = meta["file"]

    store = FAISS.from_documents(chunks, embeddings)
    out_dir = INDEX_DIR / company_id
    out_dir.mkdir(parents=True, exist_ok=True)
    store.save_local(str(out_dir))
    print(f"indexed {company_id}: {len(chunks)} chunks -> {out_dir}")


def main() -> None:
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    embeddings = get_embeddings()
    for company_id in COMPANIES:
        build_index(company_id, embeddings)


if __name__ == "__main__":
    main()
