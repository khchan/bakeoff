import os
from openai import AsyncOpenAI
from dotenv import load_dotenv
from azure.identity import EnvironmentCredential, get_bearer_token_provider

load_dotenv()

chat_endpoint=os.getenv("OPENAI_ENDPOINT")
model_deployment_name=os.getenv("OPENAI_DEPLOYMENT_NAME")
api_version=os.getenv("OPENAI_API_VERSION")
provider = get_bearer_token_provider(EnvironmentCredential(), "https://cognitiveservices.azure.com/.default")

class ChatService:
    def __init__(self):
        self.local_model_override = os.environ.get("LOCAL_MODEL_OVERRIDE", False)
        
        if self.local_model_override:
            self.client = AsyncOpenAI(
                api_key="localhost",
                base_url="http://localhost:11434/v1"
            )
            self.model = self.local_model_override
        else:
            # Azure OpenAI configuration
            from openai import AsyncAzureOpenAI
            self.client = AsyncAzureOpenAI(
                azure_ad_token_provider=provider,
                azure_endpoint=chat_endpoint,
                api_version=api_version
            )
            self.model = model_deployment_name
    
    async def get_completion(self, messages, temperature=0.7):
        """Get completion from configured LLM service"""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"Error getting completion: {str(e)}")

# Global instance - initialize lazily to avoid credential errors during import
chat_service = None

def get_chat_service():
    global chat_service
    if chat_service is None:
        chat_service = ChatService()
    return chat_service