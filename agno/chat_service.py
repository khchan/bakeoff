import os
from agno.models.openai import OpenAIChat
from agno.models.azure import AzureOpenAI
from agno.memory.v2 import Memory
from agno.storage.sqlite import SqliteStorage
from azure.identity import EnvironmentCredential, get_bearer_token_provider
from dotenv import load_dotenv

load_dotenv()

def get_chat_model():
    """Get configured chat model based on environment settings
    
    Returns:
        Configured model instance (OpenAIChat for local or AzureOpenAI for Azure)
    """
    local_model_override = os.environ.get("LOCAL_MODEL_OVERRIDE", False)
    
    if local_model_override:
        return OpenAIChat(
            id=local_model_override,
            api_key="localhost",
            base_url="http://localhost:11434/v1"
        )
    else:
        # Azure OpenAI configuration
        chat_endpoint = os.getenv("OPENAI_ENDPOINT")
        model_deployment_name = os.getenv("OPENAI_DEPLOYMENT_NAME")
        api_version = os.getenv("OPENAI_API_VERSION")
        provider = get_bearer_token_provider(
            EnvironmentCredential(), 
            "https://cognitiveservices.azure.com/.default"
        )
        
        return AzureOpenAI(
            id=model_deployment_name,
            azure_ad_token_provider=provider,
            azure_endpoint=chat_endpoint,
            api_version=api_version
        )

def get_memory_config():
    """Get configured memory for session support
    
    Returns:
        Memory instance configured for multi-user, multi-session support
    """
    return Memory()

def get_storage_config():
    """Get configured storage for session persistence
    
    Returns:
        SqliteStorage instance for persisting sessions
    """
    # Create storage directory if it doesn't exist
    os.makedirs("data", exist_ok=True)
    
    return SqliteStorage(
        table_name="agno_sessions",
        db_file="data/sessions.db"
    ) 