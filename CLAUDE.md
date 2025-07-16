# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a "bakeoff" repository comparing **four multi-agent AI frameworks** for financial data analysis using Vena Solutions API:

1. **Semantic Kernel Implementation** (`semantic-kernel/`) - Microsoft Semantic Kernel v1.33.0 with MCP plugins
2. **LangGraph Implementation** (`langgraph/`) - LangGraph v0.4.8 with StateGraph workflow
3. **Agno Implementation** (`agno/`) - Agno v1.6.4 with Team coordination and session persistence
4. **OpenAI Agents Implementation** (`openai-agents/`) - OpenAI Agents SDK v0.0.19 with handoff system

All implementations translate natural language queries into financial insights via three specialized agents: 
**Orchestration Agent** (routing), **Member Prediction Agent** (OLAP member extraction), and **MQL Agent** (query generation).

## Core Architecture

### Shared Agent Pattern
All implementations follow the same workflow:
1. **Orchestration Agent** (`orchestration_agent.py`) - Routes queries and coordinates workflow
2. **Member Prediction Agent** (`member_prediction_agent.py`) - Identifies relevant OLAP cube members
3. **MQL Agent** (`mql_agent.py`) - Generates Vena MQL queries

### Vena Integration
- **Shared Client** (`utils/vena_client.py`) - REST API client for Vena OLAP platform
- **Key Functions**: `list_models()`, `get_model()`, `get_children_of_member()`, `search_members()`, `get_member()`, `validate_mql()`, `get_hierarchy()`

### Framework Differences
- **Semantic Kernel**: Plugin-based with MCP, sequential workflow
- **LangGraph**: Graph-based with explicit state management via TypedDict
- **Agno**: Team-based with SQLite session persistence and conversation history
- **OpenAI Agents**: Built-in handoff system with comprehensive streaming support

## Development Commands

### Environment Setup
```bash
# Install dependencies
poetry install

# Activate virtual environment
source .venv/bin/activate
```

### Running Applications
```bash
# Semantic Kernel implementation
cd semantic-kernel && chainlit run server.py

# LangGraph implementation  
cd langgraph && chainlit run server.py

# Agno implementation
cd agno && chainlit run server.py

# OpenAI Agents implementation
cd openai-agents && chainlit run server.py
```

### Testing
```bash
# Run tests (pytest configured for async - no test files currently present)
pytest

# Run with coverage
pytest --cov
```

### Jupyter Notebooks
```bash
# Start JupyterLab for exploring notebooks/
jupyter lab
```

## Environment Configuration

Copy `.env.example` to `.env` and configure:
- **Azure Authentication**: `AZURE_CLIENT_ID`, `AZURE_CLIENT_SECRET`, `AZURE_TENANT_ID`
- **Azure OpenAI**: `OPENAI_ENDPOINT`, `OPENAI_DEPLOYMENT_NAME`
- **Vena API**: `VENA_ENDPOINT`, `VENA_USER`, `VENA_KEY`
- **Pool Management**: `POOL_MANAGEMENT_ENDPOINT`, `AI_PROJECT_ENDPOINT`
- **Local Models**: `LOCAL_MODEL_OVERRIDE` (e.g., `qwen3:latest`)

## Project Structure

```
bakeoff/
├── agno/                    # Agno implementation
├── langgraph/              # LangGraph implementation  
├── notebooks/              # Jupyter notebooks for exploration
├── openai-agents/          # OpenAI Agents implementation
├── semantic-kernel/        # Semantic Kernel implementation
├── utils/                  # Shared utilities
│   └── vena_client.py     # Vena API client
├── .env.example           # Environment configuration template
├── pyproject.toml         # Poetry dependencies and configuration
└── CLAUDE.md              # This file
```

## Dependencies

- Python: `>=3.10,<3.13`
- Poetry for dependency management
- Chainlit for UI across all implementations
- Framework-specific dependencies as listed in `pyproject.toml`
