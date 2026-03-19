from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.tools import StructuredTool
from pydantic import BaseModel

embedding = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vectorstore=Chroma(persist_directory="memory/chroma_db",embedding_function=embedding)
retriever=vectorstore.as_retriever(search_kwargs={"k": 3})

class StoreMemoryInput(BaseModel):
    text: str

def store_memory(text: str)-> str:
    try:
        vectorstore.add_texts([text])
        vectorstore.persist()
        return "Memory Stored Successfully"
    except Exception as e:
        return f"Error storing memory: {str(e)}"
    
store_memory_tool = StructuredTool.from_function(
    func=store_memory,
    name="store_memory",
    description="Store useful information for future retrieval",
    args_schema=StoreMemoryInput
)

class RetrieveMemoryInput(BaseModel):
    query: str

def retrieve_memory(query:str)-> str:
    try:
        docs=retriever.invoke(query)
        if not docs:
            return "No relevant memory found"
        
        return "\n\n".join([doc.page_content for doc in docs])[:2000]
    except Exception as e:
        return f"Error retrieving memory: {str(e)}"
    

retrieve_memory_tool = StructuredTool.from_function(
    func=retrieve_memory,
    name="retrieve_memory",
    description="Retrieve relevant past information based on a query",
    args_schema=RetrieveMemoryInput
)