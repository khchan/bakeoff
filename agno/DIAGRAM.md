# Agno Multi-Agent Architecture

This diagram shows the team-based agent structure and tool relationship hierarchy in the agno implementation.

## Team Coordination Architecture

```mermaid
graph TD
    A[User Query] --> B[Orchestration Team]
    
    subgraph "Orchestration Team (coordinate mode)"
        B --> C[Team Leader]
        C --> D{Delegate Decision}
    end
    
    subgraph "Team Members"
        E[Model Selection Agent]
        F[Member Prediction Agent] 
        G[MQL Agent]
    end
    
    D -->|Step 1: Select Model| E
    D -->|Step 2: Find Members| F
    D -->|Step 3: Generate MQL| G
    
    E --> H[Model Selected]
    F --> I[Members Identified]
    G --> J[MQL Generated]
    
    H --> C
    I --> C
    J --> C
    
    C --> K[Synthesized Response]
    K --> L[User]
    
    style B fill:#e1f5fe
    style E fill:#f3e5f5
    style F fill:#fff3e0
    style G fill:#e8f5e8
```

## Agent-Tool Relationship Hierarchy

```mermaid
graph TB
    subgraph "VenaTools (Centralized Tool Provider)"
        Tools[VenaTools Class]
    end
    
    subgraph "Orchestration Team"
        OT[Team Leader]
        OT --> OT_Tools[Tools: list_models, get_model_info]
    end
    
    subgraph "Model Selection Agent"
        MSA[Model Selection Agent]
        MSA --> MSA_Tools[Tools: list_models, get_model_info]
        MSA_Constraint[Max 3 tool calls]
    end
    
    subgraph "Member Prediction Agent"
        MPA[Member Prediction Agent]
        MPA --> MPA_Tools[Tools: get_top_level_members, get_children_of_member, search_members]
        MPA_Constraint[Max 5 calls/dimension, 3 levels deep]
    end
    
    subgraph "MQL Agent"
        MQLA[MQL Agent]
        MQLA --> MQLA_Tools[Tools: list_models, get_model_info]
        MQLA_Constraint[Max 2 tool calls]
    end
    
    Tools --> OT_Tools
    Tools --> MSA_Tools
    Tools --> MPA_Tools
    Tools --> MQLA_Tools
    
    style OT fill:#e1f5fe
    style MSA fill:#f3e5f5
    style MPA fill:#fff3e0
    style MQLA fill:#e8f5e8
    style Tools fill:#fce4ec
```

## Session Persistence and Memory Flow

```mermaid
graph LR
    subgraph "Session Management"
        Session[Chainlit Session ID]
        Storage[SQLite Storage]
        Memory[Conversation Memory]
    end
    
    subgraph "Agent Coordination"
        Team[Orchestration Team]
        Agent1[Model Selection]
        Agent2[Member Prediction]
        Agent3[MQL Agent]
    end
    
    Session --> Storage
    Storage --> Memory
    Memory --> Team
    Memory --> Agent1
    Memory --> Agent2
    Memory --> Agent3
    
    Team -.->|delegate| Agent1
    Agent1 -.->|context| Agent2
    Agent2 -.->|context| Agent3
    Agent3 -.->|results| Team
    
    style Team fill:#e1f5fe
    style Storage fill:#fce4ec
    style Memory fill:#fff3e0
```

## Tool Distribution Strategy

```mermaid
graph TD
    subgraph "Model Discovery Tools"
        T1[list_models]
        T2[get_model_info]
    end
    
    subgraph "Member Navigation Tools"
        T3[get_top_level_members]
        T4[get_children_of_member]
        T5[search_members]
    end
    
    subgraph "Shared Access"
        OT[Orchestration Team]
        MSA[Model Selection Agent]
        MQLA[MQL Agent]
    end
    
    subgraph "Exclusive Access"
        MPA[Member Prediction Agent]
    end
    
    T1 --> OT
    T1 --> MSA
    T1 --> MQLA
    T2 --> OT
    T2 --> MSA
    T2 --> MQLA
    
    T3 --> MPA
    T4 --> MPA
    T5 --> MPA
    
    style OT fill:#e1f5fe
    style MSA fill:#f3e5f5
    style MPA fill:#fff3e0
    style MQLA fill:#e8f5e8
    style T1 fill:#fce4ec
    style T2 fill:#fce4ec
    style T3 fill:#f0f8ff
    style T4 fill:#f0f8ff
    style T5 fill:#f0f8ff
```

## Key Components

- **Orchestration Team**: Team leader in "coordinate" mode that delegates tasks and synthesizes responses
- **Model Selection Agent**: Identifies the correct OLAP model using model discovery tools
- **Member Prediction Agent**: Navigates OLAP cube hierarchies using specialized member tools
- **MQL Agent**: Generates Vena MQL queries with validation using model info tools
- **VenaTools**: Centralized tool provider that wraps the shared Vena client
- **Tool Specialization**: Model tools shared among multiple agents, member tools exclusive to Member Prediction
- **Session Persistence**: SQLite storage with conversation memory across all agents
- **Sequential Delegation**: Team leader coordinates workflow through explicit delegation pattern