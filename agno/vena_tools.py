from typing import List, Dict, Any
from utils import vena_client as vc

class VenaTools:
    """Tools for querying and searching Vena model information"""

    def get_model_info(self, id: int, model_name: str) -> str:
        """Get information about a specific model by its ID
        
        Args:
            id: The model ID to get information for
            model_name: The name of the model to get information for
        Returns:
            JSON string containing model dimension information
        """
        return str(vc.get_model(id, model_name))

    def list_models(self) -> str:
        """List all available models with their basic information
        
        Returns:
            JSON string containing list of models with id, name, and description
        """
        return str(vc.list_models())
    
    def get_top_level_members(self, model_id: int, dimension_number: int) -> str:
        """Fetch top-level members from a dimension
        
        Args:
            model_id: The model ID
            dimension_number: The dimension number
            
        Returns:
            JSON string containing list of top-level members with id, name, alias, and numChildren
        """
        return str(vc.get_children_of_member(model_id, dimension_number, "root"))
    
    def get_children_of_member(self, model_id: int, dimension_number: int, member_id: str) -> str:
        """Fetch child members of a member from a dimension
        
        Args:
            model_id: The model ID
            dimension_number: The dimension number  
            member_id: The parent member ID
            
        Returns:
            JSON string containing list of child members with id, name, alias, and numChildren
        """
        return str(vc.get_children_of_member(model_id, dimension_number, member_id))
    
    def search_members(self, model_id: int, dimension_id: int, query: str) -> str:
        """Search for members in a model given model ID, dimension ID, and a search query
        
        Args:
            model_id: The model ID
            dimension_id: The dimension ID
            query: The search query string
            
        Returns:
            JSON string containing search results
        """
        return str(vc.search_members(model_id, dimension_id, query)) 