from typing import TypedDict, List, Dict, Any

class AgentState(TypedDict, total=False):
    # Core routing
    query: str
    selected_agent: str
    supervisor_reasoning: str
    supervisor_status: str
    messages: List[Dict[str, Any]]  # For conversation history
    event_log: List[Dict[str, Any]]
    
    # Researcher States
    search_results: List[dict]
    urls: List[str]
    scraped_data: List[str]
    processed_data: str
    
    # Executor States
    code: str
    execution_result: str
    
    # Writer States
    draft: str
    file_status: str
    
    # Analyst States
    analysis_plan: str
    insights: List[str]
    final_analysis: str
    
    # General states
    final_output: str
    status: str
    final_response: str
