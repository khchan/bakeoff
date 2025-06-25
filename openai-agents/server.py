import chainlit as cl
from agents import ItemHelpers, RunConfig, Runner
from openai.types.responses import ResponseTextDeltaEvent
from orchestration_agent import create_orchestration_agent
from chat_service import get_model

@cl.set_starters
async def set_starters():
    return [
        cl.Starter(
            label="What is top revenue across all departments in 2022 in my foundation model",
            message="What is top revenue across all departments in 2022 in my foundation model?",
        ),
        cl.Starter(
            label="What is top revenue across all departments in 2022?",
            message="What is top revenue across all departments in 2022?",
        ),
        cl.Starter(
            label="Generate MQL for quarterly revenue by department",
            message="Generate MQL for quarterly revenue by department",
        ),
        cl.Starter(
            label="Find members related to assets and liabilities",
            message="Find members related to assets and liabilities",
        )
    ]

@cl.on_chat_start
async def on_chat_start():
    """Initialize the chat session with the orchestration agent."""
    # Create the orchestration agent
    agent = create_orchestration_agent()
    cl.user_session.set("agent", agent)
    
    # Store the run configuration for Azure OpenAI
    run_config = RunConfig(model=get_model()) 
    cl.user_session.set("run_config", run_config)
    
    # Initialize conversation history for chat threads
    cl.user_session.set("conversation_history", [])
    
@cl.on_message
async def on_message(message: cl.Message):
    """Handle incoming user messages with streaming support."""
    agent = cl.user_session.get("agent")
    run_config = cl.user_session.get("run_config")
    conversation_history = cl.user_session.get("conversation_history")
    
    # Handle special commands
    if message.content.strip().lower() in ["/clear", "/reset", "/new"]:
        cl.user_session.set("conversation_history", [])
        await cl.Message(content="🔄 Conversation history cleared. Starting fresh!").send()
        return
    
    # Create a response message for streaming
    response_message = cl.Message(content="")
    await response_message.send()
    
    try:
        # Build input for this turn - include conversation history if it exists
        if conversation_history:
            # Add the new user message to the conversation history
            current_input = conversation_history + [{"role": "user", "content": message.content}]
        else:
            # First turn - just use the message content
            current_input = message.content
        
        # Use streaming for better user experience with Azure OpenAI configuration
        result = Runner.run_streamed(
            starting_agent=agent,
            input=current_input,
            run_config=run_config,
            max_turns=100# Pass the Azure OpenAI configuration
        )
        
        # Stream the response as it comes in
        content = ""
        active_steps = {}  # Track active steps by call_id
        buffered_tokens = []  # Buffer tokens during tool execution
        in_tool_execution = False  # Track if we're currently executing tools
        
        async for event in result.stream_events():
            # When the agent updates, print that
            if event.type == "agent_updated_stream_event":
                print(f"Agent updated: {event.new_agent.name}")
                continue
            # When items are generated, print them
            elif event.type == "run_item_stream_event":
                if event.item.type == "tool_call_item":
                    tool_name = event.item.raw_item.name
                    call_id = event.item.raw_item.call_id
                    print(f"-- Tool was called: {tool_name}")
                    
                    # We're now in tool execution phase - buffer any text responses
                    in_tool_execution = True
                    
                    # Start a new step for this tool call
                    step = cl.Step(name=f"🔧 {tool_name}", parent_id=response_message.id)
                    step.input = f"Calling {tool_name}..."
                    await step.send()
                    
                    # Store the step to update it later with the output
                    active_steps[call_id] = step
                    
                elif event.item.type == "tool_call_output_item":
                    # Find the corresponding step using call_id or other identifier
                    # The tool_call_output_item doesn't have call_id directly, so we'll use the most recent active step
                    if active_steps:
                        # Get the most recent step (assuming FIFO order)
                        call_id = list(active_steps.keys())[-1]
                        step = active_steps.pop(call_id)
                        
                        print(f"-- Tool output: {event.item.output}")
                        step.output = event.item.output
                        await step.update()
                        
                        # If no more active steps, we're done with tool execution
                        if not active_steps:
                            in_tool_execution = False
                            # Stream any buffered tokens now that tools are complete
                            for buffered_token in buffered_tokens:
                                await response_message.stream_token(buffered_token)
                            buffered_tokens.clear()
                        
                elif event.item.type == "message_output_item":
                    content = ItemHelpers.text_message_output(event.item)
                else:
                    pass  # Ignore other event types
            # Handle raw response event deltas
            elif (
                event.type == "raw_response_event"
                and isinstance(event.data, ResponseTextDeltaEvent)
                and (token := event.data.delta)
            ):
                # If we're in tool execution, buffer the token instead of streaming immediately
                if in_tool_execution:
                    buffered_tokens.append(token)
                else:
                    await response_message.stream_token(token)
        
        # Update conversation history for chat threads
        # Note: We need to collect the complete result for conversation history
        # For now, we'll store the user input and final response
        updated_history = conversation_history.copy() if conversation_history else []
        updated_history.append({"role": "user", "content": message.content})
        if content:
            updated_history.append({"role": "assistant", "content": content})
        cl.user_session.set("conversation_history", updated_history)
            
    except Exception as e:
        # Handle different types of errors appropriately
        error_type = type(e).__name__
        if "MaxTurnsExceeded" in error_type:
            error_message = "⏱️ The conversation exceeded the maximum number of turns. Please try a simpler query."
        elif "ModelBehaviorError" in error_type:
            error_message = "🤖 The AI model produced an unexpected response. Please try rephrasing your question."
        elif "InputGuardrailTripwireTriggered" in error_type:
            error_message = "🚨 Your input was flagged by our safety checks. Please try a different approach."
        else:
            error_message = f"❌ An error occurred: {str(e)}"
        
        response_message.content = error_message
        await response_message.send()

if __name__ == "__main__":
    cl.run() 