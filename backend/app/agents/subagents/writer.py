from typing import TypedDict, List
from langgraph.graph import StateGraph, START, END

from app.tools.file.file_manager_tool import get_file_tools
from app.graph.state import AgentState

file_tools = get_file_tools()
# Extracting necessary file management tools
input_read_tool = next((tool for tool in file_tools["input"] if "read_file" in tool.name), None)
output_write_tool = next((tool for tool in file_tools["output"] if "write_file" in tool.name), None)

def read_files_node(state: AgentState) -> AgentState:
    """Read content from input files if necessary for writing."""
    # Assuming the writer attempts to read context from external files
    query = state.get("query", "draft")
    
    try:
        if input_read_tool:
            # We attempt to read a generic context file or process existing global data
            # Realistically, this would be parameterized by an LLM providing a file name.
            # Using a fallback to global processed data for now.
            context = input_read_tool.invoke({"file_path": "context.txt"})
        else:
            context = "No file read tool access."
        file_status = "Successfully read input context."
    except Exception as e:
        context = f"File read error: {str(e)}"
        file_status = context
        
    return {
        "processed_data": str(context),
        "file_status": file_status
    }

def draft_node(state: AgentState) -> AgentState:
    """Format and draft the gathered text information."""
    data = state.get("processed_data", "")
    query = state.get("query", "Default Topic")
    
    # In a full setup, an LLM call happens here. For blueprint, we simulate processing.
    draft = f"TITLE: Document regarding {query}\n\nCONTENT:\n{data}\n\n-- Draft finalized."
    
    return {
        "draft": draft
    }

def save_file_node(state: AgentState) -> AgentState:
    """Save the final draft to the output directory."""
    draft = state.get("draft", "")
    
    try:
        if output_write_tool:
            output_write_tool.invoke({"file_path": "final_draft.md", "text": draft})
            file_status = "Draft successfully saved to output directory."
        else:
            file_status = "Output write tool missing."
    except Exception as e:
        file_status = f"File save error: {str(e)}"
        
    return {
        "file_status": file_status,
        "final_output": draft
    }

def build_graph():
    graph = StateGraph(AgentState)
    
    graph.add_node("read_files", read_files_node)
    graph.add_node("draft_node", draft_node)
    graph.add_node("save_file", save_file_node)
    
    graph.add_edge(START, "read_files")
    graph.add_edge("read_files", "draft_node")
    graph.add_edge("draft_node", "save_file")
    graph.add_edge("save_file", END)
    
    return graph.compile()