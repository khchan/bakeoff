# LangGraph Implementation

This directory contains a LangGraph implementation of the multi-agent financial Q&A system, ported from the Semantic Kernel version.

## Architecture

The LangGraph implementation uses a **StateGraph** to orchestrate the multi-agent workflow:

```
User Query → Orchestration → Model Selection → Member Prediction → MQL Generation → Response
```

### Core Components

1. **StateGraph Workflow** (`graph.py`): Defines the workflow with nodes and conditional edges
2. **State Management** (`state.py`): Shared state structure using TypedDict
3. **Nodes** (`nodes.py`): Individual processing functions for each agent capability
4. **Vena Integration** (`vena_client.py`): REST API client for Vena platform
5. **Chat Service** (`chat_service.py`): LLM backend (Azure OpenAI/local models)
6. **Chainlit Server** (`server.py`): Web interface with streaming responses

### Workflow Nodes

- **Orchestration Node**: Routes queries and determines workflow path
- **Model Selection Node**: Selects appropriate OLAP model based on query
- **Member Prediction Node**: Identifies relevant cube members using Vena API
- **MQL Generation Node**: Creates syntactically correct Vena MQL queries
- **Response Generation Node**: Formats final response for user
- **Error Node**: Handles errors and provides user feedback

## Key Differences from Semantic Kernel

1. **Graph-based Architecture**: Uses LangGraph's StateGraph instead of agent plugins
2. **Explicit State Management**: All data flows through a shared TypedDict state
3. **Conditional Routing**: Uses conditional edges instead of function calling for orchestration
4. **Node-based Processing**: Each agent capability is a separate async node function
5. **Streaming Support**: Built-in support for streaming responses through Chainlit

## Getting Started

1. Configure environment variables for Vena API and LLM provider
2. `poetry install` (from root directory)
3. `cd langgraph && chainlit run server.py`

## Dependencies

- `langgraph`: Graph-based workflow orchestration
- `chainlit`: Web interface and streaming
- `openai`: LLM integration
- `requests`: HTTP client for Vena API
- `python-dotenv`: Environment variable management