import json
import os
from typing import Literal
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from app.graph.state import AgentState
from app.agents.subagents.researcher import build_graph as build_researcher
from app.agents.subagents.executor import build_graph as build_executor
from app.agents.subagents.writer import build_graph as build_writer
from app.agents.subagents.analyst import build_graph as build_analyst

from langchain_groq import ChatGroq

load_dotenv()


def get_llm() -> ChatGroq:
    """Lazily initialize Groq client so imports/tests work without env at import time."""
    groq_token = os.getenv("GROQ_API_TOKEN") or os.getenv("GROQ_API_KEY")
    if not groq_token:
        raise RuntimeError(
            "Missing Groq API key. Set GROQ_API_TOKEN (or GROQ_API_KEY) in your environment."
        )
    return ChatGroq(model="llama-3.1-8b-instant", api_key=groq_token)

# Build worker graphs
researcher_graph = build_researcher()
executor_graph = build_executor()
writer_graph = build_writer()
analyst_graph = build_analyst()


class RouteDecision(BaseModel):
    """Decision model for agent routing"""
    agent: Literal["researcher", "executor", "writer", "analyst", "end"]
    reasoning: str = Field(description="Why this agent was chosen")


def _parse_route_decision(response_text: str) -> RouteDecision:
    """Parse supervisor JSON robustly, including fenced JSON responses."""
    normalized = response_text.strip()

    # Handle markdown code fences such as ```json ... ```
    if normalized.startswith("```"):
        lines = normalized.splitlines()
        if len(lines) >= 3:
            normalized = "\n".join(lines[1:-1]).strip()

    try:
        return RouteDecision.model_validate_json(normalized)
    except Exception:
        # Fallback: extract first JSON object from mixed text output.
        start = normalized.find("{")
        end = normalized.rfind("}")
        if start != -1 and end != -1 and end > start:
            candidate = normalized[start : end + 1]
            return RouteDecision.model_validate_json(candidate)
        raise


def supervisor_node(state: AgentState) -> AgentState:
    """
    Main supervisor node that analyzes the task and decides routing.
    Uses LLM to intelligently determine which agent(s) to use.
    """
    query = state.get("query", "")
    messages_history = state.get("messages", [])
    
    # Build context from previous exchanges
    conversation_context = ""
    if messages_history:
        conversation_context = "\n".join(
            [f"- {msg.get('role', 'unknown')}: {msg.get('content', '')[:100]}" 
             for msg in messages_history[-5:]]  # Last 5 messages for context
        )
    
    # Routing prompt
    routing_prompt = f"""You are a supervisor agent coordinating specialized workers.
    
Current Task: {query}

Available Workers:
1. researcher - Searches the web, scrapes content, stores knowledge
2. executor - Runs Python code, executes scripts, performs calculations
3. writer - Writes documents, creates content, generates reports
4. analyst - Analyzes data, extracts insights, finds patterns

Recent Conversation:
{conversation_context if conversation_context else "No previous context"}

Based on the task, which agent should handle this? Return your decision as JSON.
Consider:
- Does it need web research? → researcher
- Does it need code execution? → executor  
- Does it need document creation? → writer
- Does it need data analysis? → analyst
- Is the task complete? → end

Respond with a JSON object: {{"agent": "...", "reasoning": "..."}}"""

    try:
        response = get_llm().invoke([HumanMessage(content=routing_prompt)])
        
        response_text = response.content.strip()
        decision = _parse_route_decision(response_text)
        selected_agent = decision.agent
        reasoning = decision.reasoning
            
    except Exception as e:
        selected_agent = "end"
        reasoning = f"Routing error: {str(e)}"
    
    return {
        "selected_agent": selected_agent,
        "supervisor_reasoning": reasoning
    }


def researcher_node(state: AgentState) -> AgentState:
    """Invoke researcher agent for web search and content gathering"""
    try:
        result = researcher_graph.invoke(state)
        return {
            "processed_data": result.get("processed_data", ""),
            "search_results": result.get("search_results", []),
            "status": "Researcher completed successfully"
        }
    except Exception as e:
        return {
            "status": f"Researcher error: {str(e)}"
        }


def executor_node(state: AgentState) -> AgentState:
    """Invoke executor agent for code execution"""
    try:
        result = executor_graph.invoke(state)
        return {
            "execution_result": result.get("execution_result", ""),
            "status": "Executor completed successfully"
        }
    except Exception as e:
        return {
            "status": f"Executor error: {str(e)}"
        }


def writer_node(state: AgentState) -> AgentState:
    """Invoke writer agent for document creation"""
    try:
        result = writer_graph.invoke(state)
        return {
            "draft": result.get("draft", ""),
            "final_output": result.get("final_output", ""),
            "status": "Writer completed successfully"
        }
    except Exception as e:
        return {
            "status": f"Writer error: {str(e)}"
        }


def analyst_node(state: AgentState) -> AgentState:
    """Invoke analyst agent for data analysis"""
    try:
        result = analyst_graph.invoke(state)
        return {
            "final_analysis": result.get("final_analysis", ""),
            "insights": result.get("insights", []),
            "status": "Analyst completed successfully"
        }
    except Exception as e:
        return {
            "status": f"Analyst error: {str(e)}"
        }


def aggregate_node(state: AgentState) -> AgentState:
    """Aggregate results from worker agents into final response"""
    
    # Collect outputs from different agents
    outputs = {
        "research": state.get("processed_data", ""),
        "execution": state.get("execution_result", ""),
        "writing": state.get("final_output", "") or state.get("draft", ""),
        "analysis": state.get("final_analysis", "")
    }
    
    # Filter out empty outputs
    outputs = {k: v for k, v in outputs.items() if v}
    
    # FIX: Increased truncation limit to 4000 to preserve agent insights
    aggregation_prompt = f"""Review these worker outputs and create a concise, coherent final response.
    
Original Request: {state.get('query', '')}

Worker Outputs:
{chr(10).join([f'- {k}: {str(v)[:4000]}...' for k, v in outputs.items()])}

Create a unified response that:
1. Directly answers the original request
2. Incorporates insights from all workers
3. Is clear and actionable
4. Mentions which agents contributed"""

    try:
        response = get_llm().invoke([HumanMessage(content=aggregation_prompt)])
        final_response = response.content
    except Exception as e:
        final_response = f"Aggregation error: {str(e)}"
    
    return {
        "final_response": final_response,
        "supervisor_status": "Task completed - aggregated results"
    }


def route_to_next_agent(state: AgentState) -> str:
    """Route function between supervisor and worker agents"""
    agent = state.get("selected_agent", "end")
    
    routing_map = {
        "researcher": "researcher",
        "executor": "executor",
        "writer": "writer",
        "analyst": "analyst",
        "end": "aggregate"
    }
    
    return routing_map.get(agent, "aggregate")


def build_graph():
    """Build the supervisor graph"""
    graph = StateGraph(AgentState)
    
    # Add supervisor and worker nodes
    graph.add_node("supervisor", supervisor_node)
    graph.add_node("researcher", researcher_node)
    graph.add_node("executor", executor_node)
    graph.add_node("writer", writer_node)
    graph.add_node("analyst", analyst_node)
    graph.add_node("aggregate", aggregate_node)
    
    # Start with supervisor
    graph.add_edge(START, "supervisor")
    
    # Supervisor routes to appropriate agent
    graph.add_conditional_edges(
        "supervisor",
        route_to_next_agent,
        {
            "researcher": "researcher",
            "executor": "executor",
            "writer": "writer",
            "analyst": "analyst",
            "aggregate": "aggregate"
        }
    )
    
    # All worker agents route to aggregation
    graph.add_edge("researcher", "aggregate")
    graph.add_edge("executor", "aggregate")
    graph.add_edge("writer", "aggregate")
    graph.add_edge("analyst", "aggregate")
    
    # Aggregation is the end
    graph.add_edge("aggregate", END)
    
    return graph.compile()


if __name__ == "__main__":
    # Test the supervisor
    supervisor = build_graph()
    print("Supervisor graph built successfully!")
