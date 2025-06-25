import sys
import os

# Add the utils directory to the path to import vena_client
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'utils'))
import vena_client as vc
from agents import function_tool

@function_tool
def get_model_info(id: int, model_name: str) -> str:
    """Get information about a specific model by its ID
    Args:
        id: int - The ID of the model to get information about
        model_name: str - The name of the model to get information about
    Returns:
        str: JSON string containing model information with id, name, and description
    """
    return vc.get_model(id, model_name)

@function_tool
def list_models() -> str:
    """List all available models with their basic information.
    Args:
        None
    Returns:
        str: JSON string containing list of models with id, name, and description
    """
    return vc.list_models()

@function_tool
def get_top_level_members(model_id: int, dimension_number: int) -> str:
    """Fetch top-level members from a dimension.
    
    Args:
        model_id: int - The ID of the model to get top-level members from
        dimension_number: int - The number of the dimension to get top-level members from
    Returns:
        str: JSON string containing list top-level members with id, name, alias, and numChildren
    """
    return vc.get_children_of_member(model_id, dimension_number, "root")

@function_tool
def get_children_of_member(model_id: int, dimension_number: int, member_id: str) -> str:
    """Fetch child members of a member from a dimension.
    
    Args:
        model_id: int - The ID of the model to get child members from
        dimension_number: int - The number of the dimension to get child members from
        member_id: str - The ID of the member to get child members from
    Returns:
        str: JSON string containing list child members with id, name, alias, and numChildren
    """
    return vc.get_children_of_member(model_id, dimension_number, member_id)

@function_tool
def search_members(model_id: int, dimension_id: int, query: str) -> str:
    """Search for members in a model given model ID, dimension ID, and a search query.
    If the query is unclear, use one of the top-level members from the dimension.
    Args:
        model_id: int - The ID of the model to search members from
        dimension_id: int - The ID of the dimension to search members from
        query: str - The search query to find members
    Returns:
        str: JSON string containing list of members with id, name, alias, and numChildren
    """
    return vc.search_members(model_id, dimension_id, query) 