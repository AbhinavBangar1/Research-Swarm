import os
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from typing import List

from ..state import ResearchState

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
    
    # Initialize the LLM via Factory
    from ...llm.factory import LLMFactory
    llm = LLMFactory.get_llm(temperature=0)
    
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
    
    chain = prompt | structured_llm
    
    # Execute the chain
    result: Plan = chain.invoke({"query": query})
    
    print(f"Planner generated {len(result.sub_questions)} sub-questions.")
    

    return {
        "sub_questions": result.sub_questions,
        "current_question_idx": 0,
        "retrieved_contexts": [], # Reset contexts for the first question
    }
