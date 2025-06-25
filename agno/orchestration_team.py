from agno.team import Team
from model_selection_agent import get_model_selection_agent
from member_prediction_agent import get_member_prediction_agent
from mql_agent import get_mql_agent
from chat_service import get_chat_model, get_memory_config, get_storage_config
from dotenv import load_dotenv
from vena_tools import VenaTools

load_dotenv()

def get_orchestration_team():
    """Create a orchestration team using Agno's Team concept with session support"""
    
    # Get the specialized agents
    model_selection_agent = get_model_selection_agent()
    member_prediction_agent = get_member_prediction_agent()
    mql_agent = get_mql_agent()
    tools = VenaTools()
    
    # Create the team with coordinate mode and session support
    team = Team(
        name="Orchestration Team",
        mode="coordinate",  # Team leader delegates tasks and synthesizes outputs
        model=get_chat_model(),
        memory=get_memory_config(),  # Enable conversation memory
        storage=get_storage_config(),  # Enable session persistence
        tools=[tools.list_models, tools.get_model_info],
        members=[model_selection_agent, member_prediction_agent, mql_agent],
        description="A team of specialists that help analyze OLAP cube data for answering financial questions.",
        instructions=[
            "You are a financial planning team coordinator that works with specialized agents.",
            "You have access to conversation history to provide context-aware responses.",
            "When a user asks about financial data or OLAP cubes:",
            "1. First, delegate to the ModelSelectionAgent to identify the correct model to use for the query",
            "2. Once a model is confirmed, delegate to the MemberPredictionAgent to identify relevant cube members",
            "3. Finally, delegate to the ModelQueryLanguageAgent to generate the appropriate Vena MQL",
            "4. Reference previous conversation context when relevant to provide better assistance",
            "5. If any agent requests user clarification, pause coordination and prompt the user for input",
            "6. Limit coordination to maximum 3 rounds per agent to prevent infinite loops"
        ],
        add_datetime_to_instructions=True,
        add_history_to_messages=True,  # Include conversation history in context
        markdown=True,
    )
    
    return team 