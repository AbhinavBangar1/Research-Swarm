from typing import TypedDict, List, Annotated
import operator

class ResearchState(TypedDict):
    """
    Represents the global state of our Multi-Agent Research Graph.
    """
    original_query: str
    
    # Planner outputs
    sub_questions: List[str]
    current_question_idx: int
    
    # Supervisor Routing
    next_agent: str
    
    # Searcher & Verifier outputs
    retrieved_contexts: List[str]
    
    verified_claims: Annotated[List[dict], operator.add]
    
    # Generator output
    final_report: str
