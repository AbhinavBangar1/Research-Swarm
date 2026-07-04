from langgraph.graph import StateGraph, END
from .state import ResearchState
from .nodes.supervisor import supervisor_node
from .nodes.planner import planner_node
from .nodes.searcher import searcher_node
from .nodes.verifier import verifier_node
from .nodes.generator import generator_node

def route_from_supervisor(state: ResearchState):
    """
    Reads the 'next_agent' field updated by the Supervisor Node
    and maps it to the actual LangGraph node names.
    """
    next_agent = state.get("next_agent", "FINISH")
    
    if next_agent == "Planner":
        return "planner"
    elif next_agent == "Searcher":
        return "searcher"
    elif next_agent == "Verifier":
        return "verifier"
    elif next_agent == "Generator":
        return "generator"
    else:
        return END

workflow = StateGraph(ResearchState)

workflow.add_node("supervisor", supervisor_node)
workflow.add_node("planner", planner_node)
workflow.add_node("searcher", searcher_node)
workflow.add_node("verifier", verifier_node)
workflow.add_node("generator", generator_node)

workflow.set_entry_point("supervisor")

workflow.add_conditional_edges(
    "supervisor",
    route_from_supervisor,
    {
        "planner": "planner",
        "searcher": "searcher",
        "verifier": "verifier",
        "generator": "generator",
        END: END
    }
)

workflow.add_edge("planner", "supervisor")
workflow.add_edge("searcher", "verifier")
workflow.add_edge("verifier", "supervisor")

workflow.add_edge("generator", END)

swarm_app = workflow.compile()
