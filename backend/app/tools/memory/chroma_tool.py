from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.tools import tool
import os

# Lazy initialization
_vectorstore = None
_retriever = None

def get_vectorstore():
    global _vectorstore, _retriever
    if _vectorstore is None:
        try:
            embedding = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
            _vectorstore = Chroma(
                persist_directory="backend/app/tools/memory/chroma_db",
                embedding_function=embedding
            )
            _retriever = _vectorstore.as_retriever(search_kwargs={"k": 3})
        except Exception as e:
            print(f"Warning: Could not initialize Chroma: {e}")
            return None, None
    return _vectorstore, _retriever

@tool
def store_memory_tool(text: str)-> str:
    """Store useful information for future retrieval"""
    try:
        vectorstore, _ = get_vectorstore()
        if not vectorstore:
            return "Error: Memory system not initialized"
        vectorstore.add_texts([text])
        vectorstore.persist()
        return "Memory Stored Successfully"
    except Exception as e:
        return f"Error storing memory: {str(e)}"

@tool
def retrieve_memory_tool(query:str)-> str:
    """Retrieve relevant past information based on a query"""
    try:
        _, retriever = get_vectorstore()
        if not retriever:
            return "Error: Memory system not initialized"
        docs = retriever.invoke(query)
        if not docs:
            return "No relevant memory found"
        
        return "\n\n".join([doc.page_content for doc in docs])[:2000]
    except Exception as e:
        return f"Error retrieving memory: {str(e)}"