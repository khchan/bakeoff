from agents import Agent
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX
from member_prediction_agent import create_member_prediction_agent
from mql_agent import create_mql_agent

def create_orchestration_agent():
    """Create the main orchestration agent that routes queries to specialized agents."""
    
    # Create the specialized agents
    member_prediction_agent = create_member_prediction_agent()
    mql_agent = create_mql_agent()
    
    return Agent(
        name="OrchestrationAgent",
        instructions=f"""{RECOMMENDED_PROMPT_PREFIX}
<task>
You are a helpful assistant that routes user queries to the appropriate agent.
</task>
<tips>
- If don't know which model to use yet, start with the MemberPredictionAgent
- If you don't know which members to use yet, start with the MQLAgent
- If you have a list of members, use the MQLAgent function to generate the appropriate Vena MQL
- If the user asks any follow up questions, clarify if they'd like to use the same model, members, or MQL first
</tips>
""",
        handoffs=[member_prediction_agent, mql_agent]
    ) 