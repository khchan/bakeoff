from semantic_kernel.functions.kernel_function_decorator import kernel_function
from mql_agent import get_mql_agent
from member_prediction_agent import get_member_prediction_agent
from semantic_kernel.agents import ChatCompletionAgent
from chat_service import get_chat_service
import chainlit as cl

class OrchestrationPlugin:
    @kernel_function(
        description="Given a user query, predicts which members in an OLAP cube are relevant to the query",
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
        description="Given a user query and a list of members, generates syntactically-correct Vena MQL",
        name="generate_mql"
    )
    def generate_mql(self, query: str, members: str) -> str:
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
        You are a helpful assistant that routes user queries to the appropriate agent.
        """,
        plugins=[OrchestrationPlugin()]
    )