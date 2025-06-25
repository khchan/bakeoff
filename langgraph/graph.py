from langgraph.graph import StateGraph, START, END
from state import GraphState
from nodes import (
    orchestration_node,
    model_selection_node, 
    member_prediction_node,
    mql_generation_node,
    response_generation_node,
    error_node
)

def route_orchestration(state: GraphState) -> str:
    """Router function for orchestration node"""
    next_step = state.get("next_step")
    if next_step == "MODEL_SELECTION":
        return "model_selection"
    elif next_step == "MEMBER_PREDICTION":
        return "member_prediction"
    elif next_step == "ERROR":
        return "error_handler"
    else:
        return END

def route_model_selection(state: GraphState) -> str:
    """Router function for model selection node"""
    next_step = state.get("next_step")
    if next_step == "MEMBER_PREDICTION":
        return "member_prediction"
    elif next_step == "ERROR":
        return "error_handler"
    else:
        return END

def route_member_prediction(state: GraphState) -> str:
    """Router function for member prediction node"""
    next_step = state.get("next_step")
    if next_step == "MQL_GENERATION":
        return "mql_generation"
    elif next_step == "ERROR":
        return "error_handler"
    else:
        return END

def route_mql_generation(state: GraphState) -> str:
    """Router function for MQL generation node"""
    next_step = state.get("next_step")
    if next_step == "RESPONSE_GENERATION":
        return "response_generation"
    elif next_step == "ERROR":
        return "error_handler"
    else:
        return END

def route_response_generation(state: GraphState) -> str:
    """Router function for response generation node"""
    return END

def create_graph():
    """Create and configure the LangGraph workflow"""
    
    # Initialize the graph
    workflow = StateGraph(GraphState)
    
    # Add nodes
    workflow.add_node("orchestration", orchestration_node)
    workflow.add_node("model_selection", model_selection_node)
    workflow.add_node("member_prediction", member_prediction_node)
    workflow.add_node("mql_generation", mql_generation_node)
    workflow.add_node("response_generation", response_generation_node)
    workflow.add_node("error_handler", error_node)
    
    # Set entry point
    workflow.add_edge(START, "orchestration")
    
    # Add conditional edges
    workflow.add_conditional_edges(
        "orchestration",
        route_orchestration,
        {
            "model_selection": "model_selection",
            "member_prediction": "member_prediction", 
            "error_handler": "error_handler",
            END: END
        }
    )
    
    workflow.add_conditional_edges(
        "model_selection",
        route_model_selection,
        {
            "member_prediction": "member_prediction",
            "error_handler": "error_handler",
            END: END
        }
    )
    
    workflow.add_conditional_edges(
        "member_prediction", 
        route_member_prediction,
        {
            "mql_generation": "mql_generation",
            "error_handler": "error_handler",
            END: END
        }
    )
    
    workflow.add_conditional_edges(
        "mql_generation",
        route_mql_generation,
        {
            "response_generation": "response_generation",
            "error_handler": "error_handler", 
            END: END
        }
    )
    
    workflow.add_edge("response_generation", END)
    workflow.add_edge("error_handler", END)
    
    # Compile the graph
    return workflow.compile()

# Create the compiled graph
app = create_graph()