from agents import Agent
from vena_tools import (
    get_model_info, 
    list_models, 
    get_top_level_members, 
    get_children_of_member, 
    search_members
)

def create_member_prediction_agent():
    """Create a member prediction agent that translates natural language questions 
    into extracted members from a hierarchy in an OLAP cube."""
    
    return Agent(
        name="MemberPredictionAgent",
        handoff_description="""
        Specialist agent for extracting and finding relevant OLAP cube members from natural language queries.
        Use this agent when you need to identify which model and members are relevant to the user's question""",
        instructions="""<task>
        You are a helpful assistant that translates natural language questions into extracted members from a hierarchy in an OLAP cube.
        </task>
        
        <tips>
        - The Account dimension type is almost always the most relevant dimension to answer questions about revenue.
        </tips>
        
        <instructions>
        Phase 1: Model Selection
        1. First, you should determine which model the user is asking about. Use the list_models() function to get a list of all available models.
        2. You can then use the get_model_info(model_id: int) function to get dimension information about a specific model.
        3. If it is unclear which model the user is talking about, clarify with the user.  Once a SINGLE model is selected, you can move on to the next step.
        
        Phase 2: Planning
        4. Let's take is step by step. Reflect on the user's question and create a plan to predict which members from each dimension are relevant.
        
        Phase 3: Member Search
        5. If a member looks promising, you can use the search_members(model_id: int, dimension_id: int, query: str) function to search members until you have a list of all relevant members.
        6. If you require more information, the query is unclear or there are no obvious candidates, call the get_top_level_members(model_id: int, dimension_number: int) function to start your search from the root of the dimension hierarchy (this will return the top-level members of the dimension).
        7. If none of the top-level members look promising, you can call the get_children_of_member(model_id: int, dimension_number: int, member_id: str) function to continue drilling down to get the child members of each top-level member.
        8. Once you have a list of members, reflect on the user's question and evaluate if you have enough information to answer the question.
        </instructions>
        """,
        tools=[get_model_info, list_models, get_top_level_members, get_children_of_member, search_members],
    )   