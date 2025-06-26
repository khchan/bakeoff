# Semantic Kernel Multi-Agent Architecture

This diagram shows the plugin-mediated agent structure and coordination patterns in the semantic-kernel implementation.

## Agent Hierarchy with Plugin Distribution
```mermaid
graph TD
    A[User Query] --> B[Orchestration Agent]
    
    subgraph "Orchestration Agent"
        B --> C[OrchestrationPlugin]
        C --> D["OrchestrationPlugin methods:<br/>• list_models<br/>• get_model_info<br/>• get_member_prediction<br/>• generate_mql<br/>• execute_mql"]
        C --> W[3-Phase Workflow]
    end
    
    subgraph "Member Prediction Agent"
        I["Member Prediction Agent<br/>(FinancialPlanningAssistant)"]
        I --> MPA_Plugin[ModelQueryPlugin]
        MPA_Plugin --> MPA_Methods["Uses methods:<br/>• get_top_level_members<br/>• get_children_of_member<br/>• search_members"]
    end
    
    subgraph "MQL Agent"
        J["MQL Agent<br/>(ModelQueryLanguageAgent)"]
        J --> MQLA_Plugin[MQLValidationPlugin]
        MQLA_Plugin --> MQLA_Methods["Uses methods:<br/>• validate_mql"]
    end
    
    subgraph "Shared Plugin - ModelQueryPlugin"
        MQP[ModelQueryPlugin]
        MQP --> F1[list_models]
        MQP --> F2[get_model_info]
        MQP --> F3[get_top_level_members]
        MQP --> F4[get_children_of_member]
        MQP --> F5[search_members]
    end
    
    subgraph "External Integration"
        MCP[MCP StdioPlugin]
        Time[Time Plugin]
        MCP --> Time
    end
    
    W --> I
    W --> J
    
    I --> K[Structured JSON Output]
    J --> L[Validated MQL Query]
    
    K --> B
    L --> B
    
    MPA_Plugin --> MQP
    C --> MQP
    
    style B fill:#e1f5fe
    style I fill:#f3e5f5
    style J fill:#e8f5e8
    style C fill:#fff3e0
    style MQP fill:#fce4ec
    style MQLA_Plugin fill:#f0f8ff
    style MCP fill:#e8f0fe
    style MPA_Methods fill:#e8f5e8
    style MQLA_Methods fill:#ffe8e8
    style D fill:#fff3e0
```

## Workflow Coordination Pattern
```mermaid
sequenceDiagram
    participant User
    participant OA as Orchestration Agent
    participant OP as OrchestrationPlugin
    participant MPA as Member Prediction Agent
    participant MQLA as MQL Agent
    participant Vena as Vena API
    
    User->>OA: Natural Language Query
    
    Note over OA, OP: Phase 1: Model Selection
    OA->>OP: list_models()
    OP->>Vena: API Call
    Vena-->>OP: Model List
    OP-->>OA: Available Models
    
    OA->>OP: get_model_info(id, name)
    OP->>Vena: API Call
    Vena-->>OP: Model Details
    OP-->>OA: Model Information
    
    Note over OA, MPA: Phase 2: Member Prediction
    OA->>OP: get_member_prediction(query)
    OP->>MPA: Delegate to Agent
    MPA->>Vena: Multiple API calls via ModelQueryPlugin
    Vena-->>MPA: Member Data
    MPA-->>OP: Structured JSON
    OP-->>OA: Member Predictions
    
    Note over OA, MQLA: Phase 3: MQL Generation
    OA->>OP: generate_mql(query, members)
    OP->>MQLA: Delegate to Agent
    MQLA->>MQLA: validate_mql()
    MQLA-->>OP: Validated MQL
    OP-->>OA: MQL Query
    
    OA-->>User: Final Response
```

## Session and Threading Architecture
```mermaid
graph LR
    subgraph "Chainlit Session Management"
        Session[Chainlit Session]
        Thread[ChatHistoryAgentThread]
        History[Conversation History]
    end
    
    subgraph "Agent Instances"
        OA[Orchestration Agent]
        MPA[Member Prediction Agent]
        MQLA[MQL Agent]
    end
    
    subgraph "Service Configuration"
        CS[ChatService]
        Azure[Azure OpenAI]
        Local[Local Override]
    end
    
    subgraph "MCP Integration"
        MCP[MCPStdioPlugin]
        TimePlugin[Time Plugin]
        Lifecycle[Plugin Lifecycle]
    end
    
    Session --> Thread
    Thread --> History
    History --> OA
    History --> MPA
    History --> MQLA
    
    CS --> Azure
    CS --> Local
    
    OA --> CS
    MPA --> CS
    MQLA --> CS
    
    Session --> MCP
    MCP --> TimePlugin
    MCP --> Lifecycle
    
    style Session fill:#e1f5fe
    style CS fill:#f3e5f5
    style MCP fill:#e8f0fe
```

## Key Components

- **Orchestration Agent**: Central coordinator with `OrchestrationPlugin` containing 5 kernel functions for workflow management
- **Plugin-Mediated Coordination**: Uses plugin functions as primary mechanism for agent-to-agent communication
- **Shared Plugin Architecture**: `ModelQueryPlugin` is reused across orchestration and member prediction agents
- **Specialized Plugins**: `MQLValidationPlugin` provides domain-specific validation for MQL Agent
- **MCP Integration**: External time plugin demonstrates Model Context Protocol integration
- **3-Phase Workflow**: Sequential model selection → member prediction → MQL generation with validation
- **Session Persistence**: Chainlit-based session management with `ChatHistoryAgentThread`
- **Streaming Support**: Real-time response streaming through `invoke_stream`
- **Azure Integration**: Native Azure OpenAI with AD authentication and local model fallback