import os
from typing import Literal
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate

from ..state import ResearchState

class SupervisorRoute(BaseModel):
    """Schema forcing the Supervisor to pick a valid destination."""
    next_agent: Literal["Planner", "Searcher", "Verifier", "Generator", "FINISH"] = Field(
        description="The next agent to route to. Choose Planner if query is not decomposed. Choose Searcher to fetch info. Choose Verifier to check info. Choose Generator if all questions are answered."
    )

def supervisor_node(state: ResearchState):
    """
    The Supervisor Agent: Reads the global state and dynamically decides the next best action.
    """
    query = state.get("original_query", "")
    sub_questions = state.get("sub_questions", [])
    idx = state.get("current_question_idx", 0)
    contexts = state.get("retrieved_contexts", [])
    claims = state.get("verified_claims", [])
    
    print("\n--- SUPERVISOR AGENT: Analyzing State ---")
    
    # Hardcoded safety bounds
    if not sub_questions:
        print("Supervisor bypassing LLM: Forcing Planner (No sub-questions exist)")
        return {"next_agent": "Planner"}
        
    if idx >= len(sub_questions):
        print("Supervisor bypassing LLM: Forcing Generator (All questions answered)")
        return {"next_agent": "Generator"}

    # Initialize the LLM Router via Factory
    from ...llm.factory import LLMFactory
    llm = LLMFactory.get_llm(temperature=0)
    router = llm.with_structured_output(SupervisorRoute)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", (
            "You are the orchestrator of a research swarm. Your job is to route to the correct agent based on the state.\n"
            "Agents:\n"
            "- Searcher: Use this if we need to gather web data for the current sub-question.\n"
            "- Verifier: Use this if the Searcher has returned context that needs fact-checking.\n"
            "DO NOT route to Verifier if the context is empty.\n"
            "DO NOT route to Searcher if the context has already been gathered but not verified."
        )),
        ("human", (
            "Current State:\n"
            "Query: {query}\n"
            "Current Sub-question: {current_question}\n"
            "Contexts Gathered: {context_len}\n"
            "Claims Verified Total: {claims_len}\n\n"
            "Where should we route next?"
        ))
    ])
    
    # Safely get current question
    current_q = sub_questions[idx] if idx < len(sub_questions) else "None"
    
    chain = prompt | router
    result: SupervisorRoute = chain.invoke({
        "query": query,
        "current_question": current_q,
        "context_len": len(contexts),
        "claims_len": len(claims)
    })
    
    print(f"Supervisor decided to route to -> {result.next_agent}")
    
    # Return the dictionary that will UPDATE the global LangGraph state
    return {"next_agent": result.next_agent}
