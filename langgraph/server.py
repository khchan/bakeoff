import chainlit as cl
import json
from contextlib import AsyncExitStack
from graph import app
from state import GraphState

# Global context manager for cleanup
exit_stack = AsyncExitStack()

@cl.on_app_startup
async def on_app_startup():
    """Initialize any required services on app startup"""
    pass
    
@cl.on_app_shutdown
async def on_app_shutdown():
    """Cleanup on app shutdown"""
    await exit_stack.aclose()
    
@cl.set_starters
async def set_starters():
    """Set example starter prompts"""
    return [
        cl.Starter(
            label="What is top revenue across all departments in 2022 in my foundation model?",
            message="What is top revenue across all departments in 2022 in my foundation model?",
        ),
        cl.Starter(
            label="What is top revenue across all departments in 2022?",
            message="What is top revenue across all departments in 2022?",
        ),
        cl.Starter(
            label="Show me the net income for Q4 2023",
            message="Show me the net income for Q4 2023",
        ),
        cl.Starter(
            label="What are the total assets for the current year?",
            message="What are the total assets for the current year?",
        )
    ]

@cl.on_chat_start
async def on_chat_start():
    """Initialize chat session"""
    cl.user_session.set("initialized", True)

@cl.on_message
async def on_message(message: cl.Message):
    """Handle incoming messages"""
    
    # Create initial state
    initial_state: GraphState = {
        "user_query": message.content,
        "selected_model": None,
        "predicted_members": [],
        "generated_mql": None,
        "response": None,
        "error": None,
        "next_step": None,
        "tool_calls": []
    }
    
    # Create a Chainlit message for the response stream
    answer = cl.Message(content="")
    
    try:
        # Process through the LangGraph workflow with step visualization
        current_step = None
        previous_tool_calls = []
        
        async for chunk in app.astream(initial_state):
            for node_name, node_state in chunk.items():
                # Create step for each node execution
                if node_name not in ["__start__", "__end__"]:
                    if current_step:
                        await current_step.send()
                    
                    current_step = cl.Step(name=f"Agent: {node_name.replace('_', ' ').title()}")
                    current_step.start = True
                    current_step.output = "🔄 Processing..."
                    
                    # Show new tool calls if present
                    current_tool_calls = node_state.get("tool_calls", [])
                    new_tool_calls = current_tool_calls[len(previous_tool_calls):]
                    
                    for tool_call in new_tool_calls:
                        tool_name = tool_call.get('name', 'Unknown Tool')
                        tool_args = tool_call.get('args', {})
                        tool_result = tool_call.get('result', '')
                        tool_success = tool_call.get('success', True)
                        
                        # Create tool step
                        tool_icon = "🔧" if tool_success else "❌"
                        tool_step = cl.Step(
                            name=f"{tool_icon} {tool_name.replace('_', ' ').title()}", 
                            parent_id=current_step.id
                        )
                        
                        # Format tool arguments for display
                        if tool_args:
                            tool_step.input = f"Arguments:\n{json.dumps(tool_args, indent=2)}"
                        
                        # Show tool result
                        if tool_result:
                            # Truncate long results for display
                            display_result = str(tool_result)
                            if len(display_result) > 500:
                                display_result = display_result[:500] + "...\n[Result truncated]"
                            
                            tool_step.output = f"Result:\n{display_result}"
                            await tool_step.stream_token(display_result)
                        
                        await tool_step.send()
                    
                    # Update previous tool calls count
                    previous_tool_calls = current_tool_calls
                    
                    # Show node progress
                    if node_state.get("status"):
                        current_step.output = node_state["status"]
                        await current_step.stream_token(node_state["status"])
                
                # Handle final response
                if node_state.get("response"):
                    if current_step:
                        current_step.output = "✅ Completed"
                        await current_step.send()
                    await answer.stream_token(node_state["response"])
                    break
                elif node_state.get("error"):
                    if current_step:
                        current_step.output = f"❌ Error: {node_state['error']}"
                        await current_step.send()
                    await answer.stream_token(f"Error: {node_state['error']}")
                    break
        
        # Complete any remaining step
        if current_step:
            if not current_step.output or current_step.output == "🔄 Processing...":
                current_step.output = "✅ Completed"
            await current_step.send()
        
        # If no streaming response was found, get the final state
        if not answer.content:
            final_result = await app.ainvoke(initial_state)
            final_response = final_result.get("response", "No response generated")
            await answer.stream_token(final_response)
    
    except Exception as e:
        await answer.stream_token(f"An error occurred: {str(e)}")
    
    await answer.send()