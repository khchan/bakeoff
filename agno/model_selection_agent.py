from agno.agent import Agent
from vena_tools import VenaTools
from chat_service import get_chat_model, get_memory_config, get_storage_config
from dotenv import load_dotenv

load_dotenv()

def get_model_selection_agent():
    """Create a model selection agent that helps the user select the correct model to use for their query."""
    
    model = get_chat_model()
    tools = VenaTools()
    
    return Agent(
        name="ModelSelectionAgent",
        model=model,
        memory=get_memory_config(),  # Enable conversation memory
        storage=get_storage_config(),  # Enable session persistence
        tools=[tools.list_models, tools.get_model_info],
        description="A helpful assistant that helps the user select the correct model to use for their query.",
        instructions="""
        You are a helpful assistant that helps the user select the correct model to use for their query.
        You have access to conversation history to provide context-aware model selection.
        
        WORKFLOW:
        1. First, use the list_models() function to get a list of all available models.
        2. If the user's query mentions a specific model name (e.g., "foundation model", "budget model"), try to match it to available models.
        3. If multiple models could be relevant, use get_model_info(model_id: int) to examine dimensions and suggest the best match.
        4. Consider any previous model selections from the conversation history to maintain consistency.
        
        TERMINATION CONDITIONS:
        - If there's only 1 available model, select it immediately
        - If the user's query clearly indicates a specific model, select it
        - If multiple models are available and the query is ambiguous, ask the user to clarify by listing the available options
        - Do NOT make more than 3 tool calls - if you can't determine the model after examining available options, ask for user clarification
        
        USER CLARIFICATION FORMAT:
        When clarification is needed, respond with:
        "I need clarification on which model to use. Available models:
        [List models with brief descriptions]
        
        Which model would you like me to use for your query about [user's question]?"
        """,
        add_history_to_messages=True,  # Include conversation history in context
        markdown=True
    ) 