import os
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from rag.vector_store import get_vector_store

DOCS_DIR = os.path.join(os.path.dirname(__file__), "docs")


def ingest_documents():
    """Loads markdown documents, chunks them, and stores them in ChromaDB."""
    print(f"Loading documents from {DOCS_DIR}...")

    # Use TextLoader to read markdown files
    loader = DirectoryLoader(DOCS_DIR, glob="*.md", loader_cls=TextLoader)
    documents = loader.load()

    if not documents:
        print("No documents found in the docs directory.")
        return

    print(f"Loaded {len(documents)} documents. Splitting text into chunks...")

    # Split text into manageable chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        add_start_index=True,
    )
    chunks = text_splitter.split_documents(documents)

    print(f"Split documents into {len(chunks)} chunks. Saving to vector database...")

    # Add documents to our Chroma vector store
    db = get_vector_store()
    db.add_documents(chunks)

    print("Ingestion complete! Knowledge base is now ready.")


if __name__ == "__main__":
    ingest_documents()
