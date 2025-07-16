import json
import os
from typing import Dict, Any, List
from utils import vena_client as vc

async def make_tool_call(name: str, args: Dict[str, Any]) -> Dict[str, Any]:
    """Make a tool call and return structured information for UI display"""
    try:
        if name == "list_models":
            result = vc.list_models()
        elif name == "get_model_info":
            result = vc.get_model(args["id"], args.get("model_name", ""))
        elif name == "get_top_level_members":
            result = vc.get_children_of_member(args["model_id"], args["dimension_number"], "root")
        elif name == "get_children_of_member":
            result = vc.get_children_of_member(args["model_id"], args["dimension_number"], args["member_id"])
        elif name == "search_members":
            result = vc.search_members(args["model_id"], args["dimension_id"], args["query"])
        else:
            raise ValueError(f"Unknown tool: {name}")
        
        return {
            "name": name,
            "args": args,
            "result": result,
            "success": True
        }
    except Exception as e:
        return {
            "name": name,
            "args": args,
            "result": f"Error: {str(e)}",
            "success": False
        }

def create_tool_call_info(name: str, args: Dict[str, Any], result: Any) -> Dict[str, Any]:
    """Create tool call information for state tracking"""
    return {
        "name": name,
        "args": args,
        "result": result
    }