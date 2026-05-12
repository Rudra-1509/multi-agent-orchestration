from typing import TypedDict, List
from langgraph.graph import StateGraph, START, END

from app.graph.state import AgentState

# Note: The Analyst graph utilizes no external tools, entirely LLM conceptualization pipeline.

def plan_node(state: AgentState) -> AgentState:
    """Formulate an analytical plan based on input data."""
    query = state.get("query", "General Analysis")
    processed_data = state.get("processed_data", "")
    
    # Generate an analytical plan conceptually
    analysis_plan = f"Plan for '{query}':\n1. Review data segments.\n2. Cross-reference patterns.\n3. Identify core insights."
    
    return {
        "analysis_plan": analysis_plan
    }

def extract_node(state: AgentState) -> AgentState:
    """Extract patterns and insights from data based on the plan."""
    plan = state.get("analysis_plan", "")
    data = state.get("processed_data", "")
    
    # Conceptual insight extraction
    insights = [
        f"Insight 1: Primary data trends correlate with {plan[:10]}.",
        "Insight 2: Identified significant volume of abstract values.",
        "Insight 3: The data context establishes clear action points."
    ]
    
    return {
        "insights": insights
    }

def compile_node(state: AgentState) -> AgentState:
    """Compile insights into a final comprehensive analytical report."""
    insights = state.get("insights", [])
    
    # Formatting analysis output
    formatted_insights = "\n- ".join(insights)
    final_analysis = f"### Final Analytical Report ###\n\nKey Discoveries:\n- {formatted_insights}\n\nConclusion: The dataset effectively provides the insights mentioned above."
    
    return {
        "final_analysis": final_analysis,
        "final_output": final_analysis
    }

def build_graph():
    graph = StateGraph(AgentState)
    
    graph.add_node("plan", plan_node)
    graph.add_node("extract", extract_node)
    graph.add_node("compile", compile_node)
    
    graph.add_edge(START, "plan")
    graph.add_edge("plan", "extract")
    graph.add_edge("extract", "compile")
    graph.add_edge("compile", END)
    
    return graph.compile()
