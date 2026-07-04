import os
from src.backend.llm.factory import LLMFactory
from langchain_core.prompts import ChatPromptTemplate

def evaluate_report(report_path: str):
    """
    Reads a generated markdown report and uses the LLM as a Judge 
    to evaluate its quality across three dimensions.
    """
    if not os.path.exists(report_path):
        print(f"Error: Report file '{report_path}' not found.")
        return
        
    with open(report_path, "r", encoding="utf-8") as f:
        report_content = f.read()
        
    print(f"Loaded report from {report_path}. Starting evaluation...\n")
    
    # Initialize our local LLM judge
    llm = LLMFactory.get_llm(temperature=0.2)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", (
            "You are an expert AI evaluator. Please read the provided research report and rate it out of 10 on the following three criteria:\n"
            "1. Relevance: Does it directly address the main topic?\n"
            "2. Depth: Does it provide detailed, substantial information rather than superficial fluff?\n"
            "3. Formatting: Is it well-structured with clear headings, bullet points, and citations?\n\n"
            "Provide a brief 2-3 sentence critique, and then list your final scores."
        )),
        ("human", "Here is the report:\n\n{report}")
    ])
    
    chain = prompt | llm
    
    # Run the evaluation
    result = chain.invoke({"report": report_content})
    
    print("=" * 60)
    print("RAG SWARM EVALUATION RESULTS")
    print("=" * 60)
    print(result.content)
    print("=" * 60)

if __name__ == "__main__":
    # We point it directly to the saved report file
    evaluate_report("report_output.md")
