import chainlit as cl
from contextlib import AsyncExitStack
from semantic_kernel.agents import ChatCompletionAgent, ChatHistoryAgentThread
from semantic_kernel.contents import ChatMessageContent
from semantic_kernel.connectors.mcp import MCPStdioPlugin
from semantic_kernel.contents import ChatHistory
from orchestration_agent import get_orchestration_agent

# Globals for plugin and its context manager
time_plugin: MCPStdioPlugin | None = None
exit_stack = AsyncExitStack()

def agent_response_callback(message: ChatMessageContent) -> None:
    print(f"# {message.name}\n{message.content}")

@cl.on_app_startup
async def on_app_startup():
    global time_plugin
    time_plugin = await exit_stack.enter_async_context(
        MCPStdioPlugin(
            name="Time",
            description="Time Plugin",
            command="uvx",
            args=["mcp-server-time", "--local-timezone", "UTC"],
        )
    )
    
@cl.on_app_shutdown
async def on_app_shutdown():
    await exit_stack.aclose()
    
@cl.set_starters
async def set_starters():
    return [
        cl.Starter(
            label="What is the time in Tokyo?",
            message="What is the time in Tokyo?",
        ),
        cl.Starter(
            label="What is top revenue across all departments in 2022 in my foundation model",
            message="What is top revenue across all departments in 2022 in my foundation model?",
        ),
        cl.Starter(
            label="What is top revenue across all departments in 2022?",
            message="What is top revenue across all departments in 2022?",
        )
    ]

@cl.on_chat_start
async def on_chat_start():
    thread: ChatHistoryAgentThread = ChatHistoryAgentThread(ChatHistory())
    agent = get_orchestration_agent()
    agent.kernel.add_plugin(time_plugin)

    # Instantiate and add the Chainlit filter to the kernel, this will automatically capture function calls as Steps
    cl.SemanticKernelFilter(kernel=agent.kernel)
    cl.user_session.set("agent", agent)
    cl.user_session.set("thread", thread)

@cl.on_message
async def on_message(message: cl.Message):
    agent: ChatCompletionAgent = cl.user_session.get("agent")
    thread: ChatHistoryAgentThread = cl.user_session.get("thread")
    
    # Create a Chainlit message for the response stream
    answer = cl.Message(content="")
    
    async for response in agent.invoke_stream(messages=message.content, thread=thread):
        if response.content:
            await answer.stream_token(response.content.content)
    
        cl.user_session.set("thread", response.thread)
    
    await answer.send()