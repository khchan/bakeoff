from typing import TypedDict, List, Dict, Optional, Annotated, Any
from dataclasses import dataclass

@dataclass
class Member:
    name: str
    alias: str
    dimension: str

@dataclass
class ModelInfo:
    id: int
    name: str
    description: str

class GraphState(TypedDict):
    """State shared across all nodes in the LangGraph workflow"""
    
    # User input
    user_query: str
    
    # Model information
    selected_model: Optional[ModelInfo]
    
    # Member prediction results
    predicted_members: Annotated[List[Member], "List of predicted OLAP members"]
    
    # MQL generation
    generated_mql: Optional[str]
    
    # Final response
    response: Optional[str]
    
    # Error handling
    error: Optional[str]
    
    # Next step routing
    next_step: Optional[str]
    
    # Tool calls for UI display
    tool_calls: Annotated[List[Dict[str, Any]], "List of tool calls made during processing"]