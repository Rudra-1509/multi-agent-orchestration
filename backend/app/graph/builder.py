from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_openai import ChatOpenAI

from app.graph.state import AgentState
from app.agents.supervisor import make_supervisor_node
from app.agents.worker import make_researcher_agent, make_engineer_agent, make_qa_agent

def create_multi_agent_graph():
    # In production, ensure OPENAI_API_KEY is set in environment variables
    llm = ChatOpenAI(model="gpt-4o")
    
    # Initialize nodes
    supervisor_node = make_supervisor_node(llm)
    researcher_node = make_researcher_agent(llm)
    engineer_node = make_engineer_agent(llm)
    qa_node = make_qa_agent(llm)

    # Initialize Graph
    workflow = StateGraph(AgentState)
    
    # Add nodes referencing exact string names used in supervisor
    workflow.add_node("Supervisor", supervisor_node)
    workflow.add_node("Researcher", researcher_node)
    workflow.add_node("Engineer", engineer_node)
    workflow.add_node("QA_Reviewer", qa_node)
    
    # Add edges
    # All workers report back to the supervisor
    for worker in ["Researcher", "Engineer", "QA_Reviewer"]:
        workflow.add_edge(worker, "Supervisor")
        
    # Supervisor routing edges
    conditional_map = {
        "Researcher": "Researcher",
        "Engineer": "Engineer",
        "QA_Reviewer": "QA_Reviewer",
        "FINISH": END
    }
    
    # Add a conditional edge from Supervisor based on the `next` key in state
    workflow.add_conditional_edges(
        "Supervisor",
        lambda state: state["next"],
        conditional_map
    )
    
    # Start goes to Supervisor
    workflow.add_edge(START, "Supervisor")
    
    # Memory checkpointer
    memory = MemorySaver()
    
    # Compile the graph
    graph = workflow.compile(checkpointer=memory)
    return graph

# We can instantiate a global instance to be used by the API routers
agent_graph = create_multi_agent_graph()
