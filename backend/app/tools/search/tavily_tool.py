from langchain_core.tools import tool
from langchain_tavily import TavilySearch
import os

# Lazy initialize - only when tool is actually invoked
_tavily = None

def get_tavily():
    global _tavily
    if _tavily is None:
        api_key = os.getenv("TAVILY_API_KEY")
        if not api_key:
            return None
        _tavily = TavilySearch(max_results=5)
    return _tavily

@tool
def search_tool(query:str) ->str:
    """Performs a web search using Tavily."""
    try:
        tavily = get_tavily()
        if not tavily:
            return "Error: TAVILY_API_KEY not configured"
        results=tavily.invoke({"query": query})
        return str(results) if isinstance(results, list) else results
    except Exception as e:
        return f"Error in search tool: {str(e)}"

