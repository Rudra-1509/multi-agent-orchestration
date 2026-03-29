from typing import TypedDict,List

class AgentState(TypedDict):
    query: str
    search_results: List[dict]
    urls: List[str]
    scraped_data: List[str]
    processed_data: str
    final_output: str
