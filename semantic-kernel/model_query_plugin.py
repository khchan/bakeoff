from semantic_kernel.functions.kernel_function_decorator import kernel_function
from mql_agent import get_mql_agent
import vena_client as vc

class ModelQueryPlugin:
    """Plugin for querying and searching model information"""

    @kernel_function(
        description="Get information about a specific model by its ID",
        name="get_model_info"
    )
    def get_model_info(
        self, 
        id: int,
    ) -> str:
        return vc.get_model(id)

    @kernel_function(
        description="List all available models with their basic information",
        name="list_models"
    )
    def list_models(self) -> str:
        """
        List all available models with their basic information.
        
        Returns:
            str: JSON string containing list of models with id, name, and description
        """
        return vc.list_models()
    
    @kernel_function(
        description="Fetch top-level members from a dimension",
        name="get_top_level_members"
    )
    def get_top_level_members(self, model_id: int, dimension_number: int) -> str:
        """
        Fetch top-level members from a dimension.
        
        Returns:
            str: JSON string containing list top-level members with id, name, alias, and numChildren
        """
        return vc.get_children_of_member(model_id, dimension_number, "root")
    
    @kernel_function(
        description="Fetch child members of a member from a dimension",
        name="get_children_of_member"
    )
    def get_children_of_member(self, model_id: int, dimension_number: int, member_id: str) -> str:
        """
        Fetch child members of a member from a dimension.
        
        Returns:
            str: JSON string containing list child members with id, name, alias, and numChildren
        """
        return vc.get_children_of_member(model_id, dimension_number, member_id)
    
    @kernel_function(
        description="Search for members in a model given model ID, dimension ID, and a search query.  If the query is unclear, use one of the top-level members from the dimension.",
        name="search_members"
    )
    def search_members(self, model_id: int, dimension_id: int, query: str) -> str:
        return vc.search_members(model_id, dimension_id, query)