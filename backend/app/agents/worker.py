from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent
from app.tools.custom_tools import RESEARCHER_TOOLS, ENGINEER_TOOLS, QA_TOOLS

def create_agent_wrapper(agent, name: str):
    """
    Wrapper to adapt the React Agent (which is a CompiledStateGraph) 
    into a single node function for the parent graph.
    """
    def agent_node(state):
        # We pass the messages to the sub-agent
        result = agent.invoke(state)
        # We extract the last message and append it as a HumanMessage 
        # so the supervisor sees it coming from the 'name' worker.
        last_message = result["messages"][-1]
        return {"messages": [HumanMessage(content=last_message.content, name=name)]}
    return agent_node

def make_researcher_agent(llm):
    prompt = "You are a lead Researcher. Use the web_search tool to find information. Provide detailed summaries. Reply with the requested information."
    agent = create_react_agent(llm, tools=RESEARCHER_TOOLS, state_modifier=prompt)
    return create_agent_wrapper(agent, "Researcher")

def make_engineer_agent(llm):
    prompt = "You are an expert Software Engineer. Use tools to read and write files, and the python repl to test. Once you write the code, confirm completion."
    agent = create_react_agent(llm, tools=ENGINEER_TOOLS, state_modifier=prompt)
    return create_agent_wrapper(agent, "Engineer")

def make_qa_agent(llm):
    prompt = "You are a QA Reviewer. Review code, read files, and test them using the python repl. Report any bugs or confirm the code looks good."
    agent = create_react_agent(llm, tools=QA_TOOLS, state_modifier=prompt)
    return create_agent_wrapper(agent, "QA_Reviewer")
