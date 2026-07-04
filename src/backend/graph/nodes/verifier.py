from typing import Literal, List
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate

from ..state import ResearchState

class Claim(BaseModel):
    """A single factual claim extracted from the search context."""
    fact: str = Field(description="The extracted factual claim answering the question.")
    source: str = Field(description="The URL or source of the claim from the context.")
    confidence: Literal["High", "Medium", "Low", "Uncertain"] = Field(
        description="High if multiple sources agree, Medium if one solid source, Low if inferred, Uncertain if conflicting."
    )

class VerificationResult(BaseModel):
    """The structured output of the Verifier Agent."""
    is_answered: bool = Field(description="True if the provided context sufficiently answers the sub-question.")
    claims: List[Claim] = Field(description="List of verified claims extracted from the context.")

def verifier_node(state: ResearchState):
    """
    Verifier Agent: Evaluates the search context against the current sub-question.
    If sufficient, it extracts claims with confidence scores and advances the state.
    If insufficient, it leaves the state as-is, causing the Supervisor to trigger another search.
    """
    idx = state.get("current_question_idx", 0)
    sub_questions = state.get("sub_questions", [])
    contexts = state.get("retrieved_contexts", [])
    
    if idx >= len(sub_questions):
        return {}
        
    current_question = sub_questions[idx]
    
    # Merge all retrieved contexts into one block for the LLM to read
    context_text = "\n\n---\n\n".join(contexts)
    
    print(f"\n--- VERIFIER AGENT: Evaluating Context ---")
    print(f"Target: {current_question}")
    
    # Initialize the LLM via Factory
    from ...llm.factory import LLMFactory
    llm = LLMFactory.get_llm(temperature=0)
    structured_llm = llm.with_structured_output(VerificationResult)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", (
            "You are a meticulous fact-checking Verifier Agent. "
            "Your job is to read the provided Search Context and determine if it sufficiently answers the Sub-Question. "
            "If it does, extract the factual claims, cite the sources, and assign a Confidence score (High, Medium, Low, Uncertain). "
            "If the context is irrelevant or insufficient, set is_answered to false and return an empty claims list."
        )),
        ("human", "Sub-Question: {question}\n\nSearch Context:\n{context}")
    ])
    
    # Execute the evaluation
    chain = prompt | structured_llm
    result: VerificationResult = chain.invoke({
        "question": current_question,
        "context": context_text
    })
    
    updates = {}
    
    if result.is_answered:
        print(f"Verdict: Answered! Extracted {len(result.claims)} claims.")
        for claim in result.claims:
            print(f"  - [{claim.confidence}] {claim.fact}")
            
        updates["verified_claims"] = [claim.dict() for claim in result.claims]
    else:
        print("Verdict: Insufficient context. Moving to next question to prevent infinite search loop.")
        
    # Always advance to the next question
    updates["current_question_idx"] = idx + 1
    
    # Clear the context buffer for the next question's search
    updates["retrieved_contexts"] = []
        
    return updates
