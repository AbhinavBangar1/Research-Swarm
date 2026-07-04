from langchain_core.prompts import ChatPromptTemplate
from ..state import ResearchState

def generator_node(state: ResearchState):
    """
    Generator Agent: Synthesizes a Markdown report from verified claims.
    """
    query = state.get("original_query", "")
    claims = state.get("verified_claims", [])
    
    print("\n--- GENERATOR AGENT: Synthesizing Final Report ---")
    
    if not claims:
        print("No claims found to generate a report.")
        return {"final_report": "The swarm was unable to find any verified information regarding this topic."}
        
    claims_text = ""
    for i, claim in enumerate(claims):
        confidence = claim.get('confidence', 'Unknown')
        fact = claim.get('fact', '')
        source = claim.get('source', '')
        claims_text += f"Fact {i+1} [Confidence: {confidence}]: {fact}\nSource: {source}\n\n"
        
    from ...llm.factory import LLMFactory
    llm = LLMFactory.get_llm(temperature=0.3)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", (
            "You are an expert technical writer and researcher. Your job is to take a list of explicitly verified claims "
            "and synthesize them into a comprehensive, highly readable Markdown report that answers the original query.\n\n"
            "Rules:\n"
            "1. Organize the report with logical Markdown headers (H2, H3).\n"
            "2. Cite your sources directly inline using Markdown link syntax.\n"
            "3. Explicitly note the confidence level of claims if they are 'Low' or 'Uncertain'.\n"
            "4. Do NOT hallucinate or add any outside information. Rely entirely on the provided verified claims."
        )),
        ("human", "Original Query: {query}\n\nVerified Claims Dataset:\n{claims}")
    ])
    
    chain = prompt | llm
    
    result = chain.invoke({
        "query": query,
        "claims": claims_text
    })
    
    print(f"Report generation complete. ({len(result.content)} characters)")
    
    return {"final_report": result.content}
