from typing import Literal
from pydantic import BaseModel
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

members = ["Researcher", "Engineer", "QA_Reviewer"]
options = ["FINISH"] + members

class RouteResponse(BaseModel):
    next: Literal["FINISH", "Researcher", "Engineer", "QA_Reviewer"]

def make_supervisor_node(llm):
    system_prompt = (
        "You are a supervisor tasked with managing a conversation between the"
        f" following workers: {', '.join(members)}. Given the following user request,"
        " respond with the worker to act next. Each worker will perform a"
        " task and respond with their results and status. When finished,"
        " respond with FINISH."
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="messages"),
        ("system", f"Given the conversation above, who should act next? Or should we FINISH? Select one of: {options}")
    ])
    
    supervisor_chain = prompt | llm.with_structured_output(RouteResponse)
    
    # The supervisor node function takes the state and returns the "next" key
    def supervisor_node(state):
        # We invoke the LLM with the messages
        res = supervisor_chain.invoke(state)
        # Return {"next": RouteResponse.next} as defined in AgentState
        return {"next": res.next}
        
    return supervisor_node
