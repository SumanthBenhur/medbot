import os
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings

load_dotenv()

# Path where the vector database will be stored on disk
CHROMA_PATH = os.path.join(os.path.dirname(__file__), "chroma_db")


def get_embeddings():
    """Initialize and return the Google Gemini embedding model."""
    # Ensure you have your GOOGLE_API_KEY in your .env file
    return GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")


def get_vector_store():
    """Initialize the Chroma vector store with our embeddings."""
    return Chroma(persist_directory=CHROMA_PATH, embedding_function=get_embeddings())


def get_retriever(k=3):
    """
    Returns a retriever interface for the vector store.
    k specifies how many document chunks to retrieve per query.
    """
    db = get_vector_store()
    return db.as_retriever(search_kwargs={"k": k})
