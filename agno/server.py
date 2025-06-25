import chainlit as cl
import uuid
from agno.team import Team
from orchestration_team import get_orchestration_team

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
            label="Show me total expenses by department for Q4",
            message="Show me total expenses by department for Q4",
        )
    ]

@cl.on_chat_start
async def on_chat_start():
    """Initialize the chat session with the financial planning team and session management"""
    team: Team = get_orchestration_team()
    
    # Generate unique user and session IDs for this Chainlit session
    # In a production app, you might get the user_id from authentication
    user_id = f"user_{uuid.uuid4().hex[:8]}"
    session_id = f"session_{uuid.uuid4().hex[:8]}"
    
    # Store team and session info in Chainlit session
    cl.user_session.set("team", team)
    cl.user_session.set("user_id", user_id)
    cl.user_session.set("session_id", session_id)

@cl.on_message
async def on_message(message: cl.Message):
    """Handle incoming messages and process them through the financial planning team with session context"""
    team: Team = cl.user_session.get("team")
    user_id = cl.user_session.get("user_id")
    session_id = cl.user_session.get("session_id")
    
    # Create main response message
    response_message = cl.Message(content="")
    await response_message.send()
    
    try:
        current_step = None
        current_agent = None
        agent_steps = {}
        response_started = False
        
        # Use streaming to show real-time progress with session context
        async for response in await team.arun(
            message=message.content, 
            user_id=user_id, 
            session_id=session_id,
            stream=True, 
            stream_intermediate_steps=True
        ):
            if hasattr(response, 'content') and response.content:
                # Check if this is a user clarification request
                if "I need clarification" in response.content:
                    # Complete current step if active
                    if current_step:
                        current_step.output = "⏸️ Waiting for user clarification"
                        await current_step.send()
                    
                    # Send clarification directly through main response
                    await response_message.stream_token("\n\n" + response.content)
                    return
                
                # Detect agent transitions by looking for agent names in content
                agent_detected = None
                if "ModelSelectionAgent" in str(response) or "model selection" in response.content.lower():
                    agent_detected = "Model Selection"
                elif "MemberPredictionAgent" in str(response) or "member prediction" in response.content.lower():
                    agent_detected = "Member Prediction"
                elif "ModelQueryLanguageAgent" in str(response) or "mql" in response.content.lower():
                    agent_detected = "MQL Generation"
                
                # Create or update agent step
                if agent_detected and agent_detected != current_agent:
                    # Complete previous step
                    if current_step:
                        current_step.output = "✅ Completed"
                        await current_step.send()
                    
                    # Create new agent step
                    current_agent = agent_detected
                    current_step = cl.Step(name=f"🤖 {current_agent} Agent")
                    current_step.input = f"Processing with {current_agent} Agent"
                    current_step.output = "🔄 Working..."
                    agent_steps[current_agent] = current_step
                    
                    await current_step.send()
                
                # Detect tool calls in the response
                if "list_models" in response.content or "get_model_info" in response.content:
                    tool_step = cl.Step(
                        name="🔧 Model Information Tools", 
                        parent_id=current_step.id if current_step else None
                    )
                    tool_step.output = "Fetching model information..."
                    await tool_step.send()
                elif "search_members" in response.content or "get_children_of_member" in response.content:
                    tool_step = cl.Step(
                        name="🔍 Member Search Tools", 
                        parent_id=current_step.id if current_step else None
                    )
                    tool_step.output = "Searching OLAP cube members..."
                    await tool_step.send()
                
                # Stream the actual response content
                await response_message.stream_token(response.content)
                response_started = True
        
        # Complete final step
        if current_step:
            current_step.output = "✅ Completed"
            await current_step.send()
        
        # If no response was generated, provide a helpful message
        if not response_started:
            await response_message.stream_token("I apologize, but I wasn't able to generate a response. Please try rephrasing your question or ask about a specific financial model.")
            
    except TimeoutError:
        if current_step:
            current_step.output = "⏱️ Timeout"
            await current_step.send()
            
        error_content = f"""⏱️ **Request Timeout**: The team took too long to coordinate a response.

**Suggestions:**
- Try asking a more specific question
- Mention which financial model you're interested in
- Break complex queries into smaller parts

**Session Info**: `{session_id}` | **User**: `{user_id}`"""
        await response_message.stream_token("\n\n" + error_content)
        
    except Exception as e:
        if current_step:
            current_step.output = f"❌ Error: {str(e)[:100]}..."
            await current_step.send()
            
        error_type = type(e).__name__
        error_content = f"""❌ **{error_type}**: {str(e)}

**Troubleshooting:**
- Please try rephrasing your question
- Check if you're asking about a valid financial model
- Ensure your question relates to OLAP cube analysis

**Session Info**: `{session_id}` | **User**: `{user_id}`"""
        await response_message.stream_token("\n\n" + error_content)

if __name__ == "__main__":
    cl.run() 