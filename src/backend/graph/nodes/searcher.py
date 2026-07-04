from langchain_community.tools import DuckDuckGoSearchResults
from ..state import ResearchState

def searcher_node(state: ResearchState):
    """
    Searcher Agent: Executes a web search for the current sub-question using DuckDuckGo.
    """
    idx = state.get("current_question_idx", 0)
    sub_questions = state.get("sub_questions", [])
    
    # Safety check
    if idx >= len(sub_questions):
        print("Searcher bypassed: No remaining questions.")
        return {}
        
    current_question = sub_questions[idx]
    
    print(f"\n--- SEARCHER AGENT: Querying DuckDuckGo ---")
    print(f"Target: {current_question}")
    
    # Initialize DuckDuckGo tool
    search_tool = DuckDuckGoSearchResults(max_results=3)
    
    # Execute the search
    try:
        raw_results = search_tool.invoke(current_question)
        print(f"Search successful. Retrieved {len(raw_results)} chars of context.")
    except Exception as e:
        print(f"Search failed: {e}")
        raw_results = f"Search failed with error: {str(e)}"
    
    contexts = state.get("retrieved_contexts", [])
    contexts.append(raw_results)
    
    # Update the global state
    return {"retrieved_contexts": contexts}
