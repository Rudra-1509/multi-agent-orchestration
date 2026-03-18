from pydantic import BaseModel
from langchain.tools import StructuredTool
from langchain_tavily import TavilySearchResults

class TavilySearchInput(BaseModel):
    query: str
tavily=TavilySearchResults(max_results=5,search_depth="advanced")

def search_func(query:str) ->str:
    """
    Performs a web search using Tavily
    """
    try:
        results=tavily.run(query)
        return results
    except Exception as e:
        return f"Error in search tool: {str(e)}"

search_tool = StructuredTool.from_function(
    func=search_func,
    name="tavily_search",
    description="Performs a web search using Tavily.",
    args_schema=TavilySearchInput
)

