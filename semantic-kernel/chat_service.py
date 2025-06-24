import os
from openai import AsyncOpenAI
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion, AzureChatCompletion
from azure.identity import EnvironmentCredential, get_bearer_token_provider
from dotenv import load_dotenv

load_dotenv()

local_model_override = os.environ.get("LOCAL_MODEL_OVERRIDE", False)
chat_endpoint=os.getenv("OPENAI_ENDPOINT")
model_deployment_name=os.getenv("OPENAI_DEPLOYMENT_NAME")
api_version=os.getenv("OPENAI_API_VERSION")
provider = get_bearer_token_provider(EnvironmentCredential(), "https://cognitiveservices.azure.com/.default")

def get_chat_service():
    if local_model_override:
        chat_service = OpenAIChatCompletion(service_id="chat_service", ai_model_id=local_model_override, async_client=AsyncOpenAI(
            api_key="localhost",
            base_url="http://localhost:11434/v1"
        ))
    else:
        chat_service = AzureChatCompletion(
            service_id="chat_service",
            endpoint=chat_endpoint,
            ad_token_provider=provider,
            deployment_name=model_deployment_name,
            api_version=api_version
        )
    return chat_service