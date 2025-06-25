# Financial Planning Multi-Agent System - OpenAI Agents SDK

This implementation replicates the semantic-kernel multi-agent system using the [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/). The system provides intelligent financial planning assistance through specialized agents that work together to process OLAP cube queries and generate Vena MQL.

## Architecture

The system consists of three main agents that coordinate through handoffs:

### 1. OrchestrationAgent
- **Role**: Main coordinator that routes user queries to specialized agents
- **Features**: 
  - Uses [recommended handoff prompts](https://openai.github.io/openai-agents-python/handoffs/#recommended-prompts) for better LLM understanding
  - Intelligent routing based on query type and intent
  - Support for chaining operations (member prediction → MQL generation)
  - Provides user guidance throughout the process

### 2. MemberPredictionAgent
- **Role**: Translates natural language into OLAP cube member extraction
- **Features**:
  - **Tools**: `get_model_info`, `list_models`, `get_top_level_members`, `get_children_of_member`, `search_members`
  - **Handoff Description**: Optimized for LLM understanding of when to use this agent
  - **Workflow**: Model selection → Member extraction → Results summary

### 3. MQLAgent
- **Role**: Generates syntactically-correct Vena MQL queries
- **Features**:
  - **Handoff Description**: Clear routing logic for MQL generation tasks
  - **Comprehensive MQL syntax**: Supports all major MQL constructs and operators
  - **Structured approach**: Analysis → Identification → Construction → Validation

## Configuration

The system supports multiple deployment options through centralized configuration:

### Azure OpenAI Configuration

Set these environment variables to use Azure OpenAI:

```bash
# Required for Azure OpenAI
OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
OPENAI_DEPLOYMENT_NAME=your-gpt-4o-deployment-name
OPENAI_API_VERSION=2024-02-15-preview

# Option 1: API Key Authentication
OPENAI_API_KEY=your-azure-openai-api-key

# Option 2: Azure AD Authentication (omit OPENAI_API_KEY for this option)
AZURE_CLIENT_ID=your-client-id
AZURE_CLIENT_SECRET=your-client-secret
AZURE_TENANT_ID=your-tenant-id
```

### Standard OpenAI Configuration

For direct OpenAI usage:

```bash
OPENAI_API_KEY=sk-your-openai-api-key
```

### Local Model Configuration

For local models (e.g., Ollama):

```bash
LOCAL_MODEL_OVERRIDE=llama2  # or your preferred local model
```

The system automatically detects which configuration to use based on the environment variables present.

## Key Features

### ✅ **OpenAI Agents SDK Best Practices**
- **Proper Tool Decoration**: All tools use `@function_tool` decorator
- **Recommended Handoff Prompts**: Uses `RECOMMENDED_PROMPT_PREFIX` for better handoff understanding
- **Streaming Support**: Full streaming implementation with real-time updates
- **Flexible Model Configuration**: Support for Azure OpenAI, OpenAI, and local models
- **Error Handling**: Comprehensive error handling for all SDK exception types

### 🔄 **Streaming & Real-time Updates**
- **Token-by-token streaming**: Real-time response generation
- **Agent handoff notifications**: Visual feedback when switching between agents
- **Progress indicators**: Clear status updates during complex operations

### 🛡️ **Robust Error Handling**
- **MaxTurnsExceeded**: Handles conversation length limits
- **ModelBehaviorError**: Manages unexpected model responses
- **InputGuardrailTripwireTriggered**: Processes safety check violations
- **General Exception Handling**: Comprehensive fallback error management

## Implementation Details

### Centralized Configuration
```python
# chat_service.py handles all model configuration
def get_openai_client():
    if local_model_override:
        return AsyncOpenAI(api_key="localhost", base_url="http://localhost:11434/v1")
    elif chat_endpoint and model_deployment_name:
        # Azure OpenAI with API key or Azure AD
        return AzureOpenAI(...)
    else:
        # Standard OpenAI
        return AsyncOpenAI(api_key=openai_api_key)
```

### Agent Configuration
```python
# Each agent is configured with:
Agent(
    name="AgentName",
    handoff_description="Clear description for routing logic",
    instructions=f"{RECOMMENDED_PROMPT_PREFIX}\n{custom_instructions}",
    tools=[function_tool_1, function_tool_2],  # Tools with @function_tool decorator
    # Model configuration handled centrally via RunConfig
)
```

### Tool Implementation
```python
from agents import function_tool

@function_tool
def get_model_info(id: int) -> str:
    """Get information about a specific model by its ID"""
    return vc.get_model(id)
```

### Handoff Pattern
```python
# Orchestration agent with proper handoffs
Agent(
    name="OrchestrationAgent",
    instructions=f"{RECOMMENDED_PROMPT_PREFIX}\n{orchestration_instructions}",
    handoffs=[member_prediction_agent, mql_agent]  # Direct agent references
)
```

### Streaming Implementation
```python
# Server with streaming support and Azure OpenAI configuration
result = Runner.run_streamed(
    starting_agent=agent, 
    input=message.content,
    run_config=run_config  # Azure OpenAI configuration
)

async for event in result.stream_events():
    if event.type == "raw_response_event":
        # Handle token-by-token streaming
    elif event.type == "agent_updated_stream_event":
        # Handle agent handoffs
```

## Usage Examples

### 1. Member Prediction
```
User: "Find revenue accounts for Q1 2022"
→ Routes to MemberPredictionAgent
→ Uses tools to explore OLAP cube
→ Returns structured member list
```

### 2. MQL Generation
```
User: "Generate MQL for quarterly sales by department"
→ Routes to MQLAgent
→ Analyzes business requirements
→ Generates syntactically-correct MQL
```

### 3. End-to-End Analysis
```
User: "What is the top revenue across all departments in 2022?"
→ Routes to MemberPredictionAgent (find relevant members)
→ Handoff to MQLAgent (generate query with found members)
→ Returns complete analysis with executable MQL
```

## Getting Started

1. **Install Dependencies**:
   ```bash
   pip install openai-agents chainlit python-dotenv azure-identity
   ```

2. **Configure Environment Variables**:
   Create a `.env` file with your Azure OpenAI or OpenAI configuration (see Configuration section above)

3. **Run the Server**:
   ```bash
   chainlit run server.py
   ```

4. **Access the Interface**:
   - Open your browser to the provided URL
   - Try the starter examples or ask custom questions
   - Watch the streaming responses and agent handoffs in real-time

## File Structure

```
openai-agents/
├── server.py                    # Chainlit server with streaming
├── orchestration_agent.py       # Main coordinator agent
├── member_prediction_agent.py   # OLAP cube member extraction
├── mql_agent.py                 # MQL query generation
├── vena_tools.py               # Tool functions with @function_tool
├── chat_service.py             # Centralized model configuration
├── chainlit.md                 # Chainlit configuration
├── .env.example                # Environment configuration template
└── README.md                   # This documentation
```

## Comparison with Semantic-Kernel

| Feature | Semantic-Kernel | OpenAI Agents SDK |
|---------|----------------|-------------------|
| **Agent Definition** | Custom classes | Simple `Agent()` constructor |
| **Tool Integration** | Plugin system | `@function_tool` decorator |
| **Handoffs** | Manual coordination | Built-in handoff system |
| **Streaming** | Custom implementation | Native streaming support |
| **Error Handling** | Manual try/catch | Built-in exception types |
| **Model Configuration** | Service-specific classes | Centralized client configuration |
| **Azure OpenAI Support** | Built-in AzureChatCompletion | Standard AzureOpenAI client |

## Advanced Features

### Tracing Support
The implementation automatically supports [OpenAI Agents SDK tracing](https://openai.github.io/openai-agents-python/tracing/), allowing you to:
- View agent runs in the OpenAI Dashboard
- Debug handoff logic and tool usage
- Optimize agent performance

### Guardrails (Optional)
You can add [input/output guardrails](https://openai.github.io/openai-agents-python/guardrails/) for additional safety:
```python
from agents import InputGuardrail

agent = Agent(
    name="Agent",
    instructions="...",
    input_guardrails=[InputGuardrail(guardrail_function=your_guardrail)]
)
```

## Contributing

When making changes:
1. Follow the [OpenAI Agents SDK documentation](https://openai.github.io/openai-agents-python/) patterns
2. Use proper tool decoration with `@function_tool`
3. Include handoff descriptions for better routing
4. Test streaming functionality
5. Ensure error handling covers all SDK exception types
6. Test with both Azure OpenAI and standard OpenAI configurations

---

This implementation demonstrates the power and simplicity of the OpenAI Agents SDK for building sophisticated multi-agent workflows with minimal code and maximum functionality, supporting enterprise Azure OpenAI deployments. 