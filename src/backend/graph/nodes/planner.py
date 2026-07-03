import os
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from pydantic import BaseModel, Field
from typing import List

from .state import ResearchState

class Plan(BaseModel):
    """Schema for the Planner's structured output."""
    sub_questions: List[str] = Field(
        description="A list of distinct, atomic research questions needed to fully answer the original query. Order them logically."
    )

def planner_node(state: ResearchState):
    """
    The Planner Agent: Decomposes the original complex query into smaller, atomic sub-questions.
    """
    query = state.get("original_query", "")
    
    print(f"--- PLANNER AGENT: Decomposing Query ---")
    print(f"Query: {query}")

    llm = ChatGroq(model="llama3-70b-8192", temperature=0)
    
    # Bind the Pydantic schema so the LLM returns a guaranteed JSON structure
    structured_llm = llm.with_structured_output(Plan)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", (
            "You are an expert research planner. Your task is to break down complex user queries "
            "into a comprehensive list of atomic, searchable sub-questions. "
            "These questions will be handed off to a web-search agent. "
            "Make them specific, targeted, and logically ordered."
        )),
        ("human", "Decompose the following research query into sub-questions: {query}")
    ])
    
    # Create the LCEL chain
    chain = prompt | structured_llm
    
    # Execute the chain
    result: Plan = chain.invoke({"query": query})
    
    print(f"Planner generated {len(result.sub_questions)} sub-questions.")
    
    # Return the dictionary that will UPDATE the global LangGraph state
    return {
        "sub_questions": result.sub_questions,
        "current_question_idx": 0,
        "retrieved_contexts": [], # Reset contexts for the first question
    }
