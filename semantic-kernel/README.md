# Semantic Kernel

This project demonstrates multi-agent collaboration using Semantic Kernel (v1.33.0) to translate natural language queries into financial data insights via Vena Solutions integration.

## Architecture

**Flow**: User Query → Orchestration Agent → Specialized Agents → Vena API → Results

### Core Agents
- **Orchestration Agent**: Routes queries and coordinates workflow
- **Member Prediction Agent**: Identifies relevant OLAP cube members from natural language and interacts with Vena model APIs to refine members
- **MQL Agent**: Generates syntactically correct Vena MQL queries

### Supporting Components
- **Chat Service**: Configurable LLM backend (Azure OpenAI/local models)
- **Vena Client**: REST API integration with Vena platform
- **Chainlit Server**: Web interface with streaming responses

## Observations
- `AgentGroupChat` is transitioning to new [orchestration primitives](https://learn.microsoft.com/en-us/semantic-kernel/frameworks/agent/agent-orchestration/?pivots=programming-language-python)
- Sequential orchestration works reliably; group chat and handoff patterns encounter jailbreak violations, possibly due to SK's self-prompting mechanisms

## Getting Started

1. Configure environment variables for Vena API and LLM provider
2. `poetry install`
3. `chainlit run server.py` 