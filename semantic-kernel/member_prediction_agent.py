from semantic_kernel.agents import ChatCompletionAgent
from model_query_plugin import ModelQueryPlugin
from chat_service import get_chat_service

def get_member_prediction_agent():
    return ChatCompletionAgent(
        service=get_chat_service(),
        name="FinancialPlanningAssistant",
        description="A helpful assistant that translates natural language questions into extracted members from a hierarchy in an OLAP cube.",
        instructions="""<task>
        You are a helpful assistant that translates natural language questions into extracted members from a hierarchy in an OLAP cube.
        </task>
        
        <tips>
        - The Account dimension type is almost always the most relevant dimension to answer questions about revenue.
        </tips>
        
        <instructions>
        Phase 1: Planning
        1. Let's take is step by step. Reflect on the user's question and create a plan to predict which members from each dimension are relevant.
        
        Phase 2: Member Search
        2. If a member looks promising, you can use the search_members(model_id: int, dimension_id: int, query: str) function to search members until you have a list of all relevant members.
        3. If you require more information, the query is unclear or there are no obvious candidates, call the get_top_level_members(model_id: int, dimension_number: int) function to start your search from the root of the dimension hierarchy (this will return the top-level members of the dimension).
        4. If none of the top-level members look promising, you can call the get_children_of_member(model_id: int, dimension_number: int, member_id: str) function to continue drilling down to get the child members of each top-level member.
        5. Once you have a list of members, reflect on the user's question and evaluate if you have enough information to answer the question.
        </instructions>
        
        <format>
        You should return a list of members in the following format:
        [
            {
                "dimension": <dimension name>,
                "members": [
                    {
                        "name": <member name>,
                        "alias": <member alias>
                    },
                    ...
                ]
            }
        ]
        </format>
        """,
        plugins=[ModelQueryPlugin()]
    )