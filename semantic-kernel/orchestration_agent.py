from semantic_kernel import Kernel
from semantic_kernel.functions.kernel_function_decorator import kernel_function
from mql_agent import get_mql_agent
from member_prediction_agent import get_member_prediction_agent
from semantic_kernel.agents import ChatCompletionAgent
from chat_service import get_chat_service
import chainlit as cl
from utils import vena_client as vc

class OrchestrationPlugin:
    
    @kernel_function(
        description="Get information about a specific model by its ID",
        name="get_model_info"
    )
    def get_model_info(
        self, 
        id: int,
        model_name: str,
    ) -> str:
        return vc.get_model(id, model_name)

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
        description="""
        Given a user query, predicts which members in an OLAP cube are relevant to the query.
        DO NOT USE THIS FUNCTION UNTIL YOU KNOW WHICH MODEL THE USER IS ASKING ABOUT.
        """,
        name="get_member_prediction"
    )
    def get_member_prediction(
        self, 
        query: str,
    ) -> str:
        thread = cl.user_session.get("thread")
        member_prediction_agent = get_member_prediction_agent()
        cl.SemanticKernelFilter(kernel=member_prediction_agent.kernel)
        return member_prediction_agent.get_response(message=query, thread=thread)
    
    @kernel_function(
        description="""
        Given a user query, and the result of OrchestrationPlugin-get_member_prediction in the context, generates syntactically-correct Vena MQL.
        DO NOT USE THIS FUNCTION UNTIL YOU KNOW WHICH MODEL THE USER IS ASKING ABOUT AND HAVE A LIST OF MEMBERS.
        If you don't have a list of members, or if it seems like the user wants to look for different members, use the get_member_prediction function again.
        If it seems like the user wants to refer to another model, use the list_models() function to get a list of all available models.
        """,
        name="generate_mql"
    )
    def generate_mql(self, query: str, members: list[dict]) -> str:
        thread = cl.user_session.get("thread")
        mql_agent = get_mql_agent()
        cl.SemanticKernelFilter(kernel=mql_agent.kernel)
        request = f"Given the user query: {query} and the list of members: {members}, generate syntactically-correct Vena MQL"
        return mql_agent.get_response(message=request, thread=thread)
    
def get_orchestration_agent():
    return ChatCompletionAgent(
        service=get_chat_service(),
        name="OrchestrationAgent",
        description="A helpful assistant that routes user queries to the appropriate agent.",
        instructions="""
        <task>
        You are a helpful assistant that routes user queries to the appropriate agent.
        </task>
        
        <instructions>
        Phase 1: Model Selection
        1. First, you should determine which model the user is asking about. Use the list_models() function to get a list of all available models.
        2. If there are multiple models that seem relevant, clarify with the user.  Once a SINGLE model is selected, you can move on to the next step.
        3. You can use the get_model_info(model_id: int) function to get dimension information about a specific model.
        
        Phase 2: Member Prediction
        4. If you don't know which members to use yet, start with the get_member_prediction function
        
        Phase 3: MQL Generation
        5. If you have a list of members, use the generate_mql function to generate the appropriate Vena MQL
        6. If the user asks any follow up questions, clarify if they'd like to use the same model, members, or MQL first
        </instructions>
        """,
        plugins=[OrchestrationPlugin()]
    )