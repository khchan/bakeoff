import os
from agents import OpenAIChatCompletionsModel
from openai import AsyncOpenAI, AsyncAzureOpenAI
from azure.identity import EnvironmentCredential, get_bearer_token_provider
from dotenv import load_dotenv

load_dotenv()

# Configuration from environment variables
local_model_override = os.environ.get("LOCAL_MODEL_OVERRIDE", False)
chat_endpoint=os.getenv("OPENAI_ENDPOINT")
model_deployment_name=os.getenv("OPENAI_DEPLOYMENT_NAME")
api_version=os.getenv("OPENAI_API_VERSION")
provider = get_bearer_token_provider(EnvironmentCredential(), "https://cognitiveservices.azure.com/.default")

def get_model() -> OpenAIChatCompletionsModel:
    """Get the appropriate OpenAI client based on configuration."""
    
    if local_model_override:
        # Local model (e.g., Ollama)
        return OpenAIChatCompletionsModel( 
            model=local_model_override,
            openai_client=AsyncOpenAI(
                api_key="localhost",
                base_url="http://localhost:11434/v1"
            )
        )
    else:
        return OpenAIChatCompletionsModel( 
            model=model_deployment_name,
            openai_client=AsyncAzureOpenAI(
                azure_ad_token_provider=provider,
                azure_endpoint=chat_endpoint,
                api_version=api_version or "2024-02-15-preview",
            )
        )