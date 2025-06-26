# LangGraph Multi-Agent State Flow

This diagram shows the state graph architecture and agent flows in the langgraph implementation.

## StateGraph Flow Architecture

```mermaid
graph TD
    A[START] --> B[Orchestration Node]
    
    B --> C{Route Orchestration}
    C -->|MODEL_SELECTION| D[Model Selection Node]
    C -->|MEMBER_PREDICTION| E[Member Prediction Node]
    C -->|ERROR| F[Error Handler Node]
    C -->|END| G[END]
    
    D --> H{Route Model Selection}
    H -->|MEMBER_PREDICTION| E
    H -->|ERROR| F
    H -->|END| G
    
    E --> I{Route Member Prediction}
    I -->|MQL_GENERATION| J[MQL Generation Node]
    I -->|ERROR| F
    I -->|END| G
    
    J --> K{Route MQL Generation}
    K -->|RESPONSE_GENERATION| L[Response Generation Node]
    K -->|ERROR| F
    K -->|END| G
    
    L --> M{Route Response Generation}
    M -->|END| G
    M -->|ERROR| F
    
    F --> N{Route Error Handler}
    N -->|END| G
    
    style B fill:#e1f5fe
    style D fill:#f3e5f5
    style E fill:#fff3e0
    style J fill:#e8f5e8
    style L fill:#f0f8ff
    style F fill:#ffebee
```

## State Management and Data Flow

```mermaid
graph LR
    subgraph "GraphState (TypedDict)"
        S1["user_query: str"]
        S2["selected_model: ModelInfo"]
        S3["predicted_members: List of Member"]
        S4["generated_mql: str"]
        S5["response: str"]
        S6["error: str"]
        S7["next_step: str"]
        S8["tool_calls: List of Dict"]
    end
    
    subgraph "Node Operations"
        N1[Orchestration]
        N2[Model Selection]
        N3[Member Prediction]
        N4[MQL Generation]
        N5[Response Generation]
    end
    
    S1 --> N1
    N1 --> S7
    N1 --> S8
    
    S7 --> N2
    N2 --> S2
    N2 --> S7
    N2 --> S8
    
    S2 --> N3
    N3 --> S3
    N3 --> S7
    N3 --> S8
    
    S3 --> N4
    N4 --> S4
    N4 --> S7
    N4 --> S8
    
    S4 --> N5
    N5 --> S5
    N5 --> S7
    
    style S7 fill:#fce4ec
    style S8 fill:#f0f8ff
```

## Node-Tool Integration

```mermaid
graph TB
    subgraph "Tool System"
        TC[tool_calls.py]
        VC[Vena Client]
    end
    
    subgraph "Orchestration Node"
        ON[Orchestration]
        ON_LLM[LLM Analysis]
    end
    
    subgraph "Model Selection Node"
        MSN[Model Selection]
        MSN_Tool[list_models]
        MSN_LLM[LLM Model Choice]
    end
    
    subgraph "Member Prediction Node"
        MPN[Member Prediction]
        MPN_Tool1[get_model_info]
        MPN_Tool2[get_top_level_members]
        MPN_Tool3[get_children_of_member]
        MPN_Tool4[search_members]
        MPN_LLM[LLM Member Analysis]
    end
    
    subgraph "MQL Generation Node"
        MGN[MQL Generation]
        MGN_LLM[LLM MQL Generation]
    end
    
    subgraph "Response Generation Node"
        RGN[Response Generation]
        RGN_LLM[LLM Response Formatting]
    end
    
    ON --> ON_LLM
    
    MSN --> MSN_Tool
    MSN_Tool --> TC
    MSN --> MSN_LLM
    
    MPN --> MPN_Tool1
    MPN --> MPN_Tool2
    MPN --> MPN_Tool3
    MPN --> MPN_Tool4
    MPN_Tool1 --> TC
    MPN_Tool2 --> TC
    MPN_Tool3 --> TC
    MPN_Tool4 --> TC
    MPN --> MPN_LLM
    
    MGN --> MGN_LLM
    RGN --> RGN_LLM
    
    TC --> VC
    
    style ON fill:#e1f5fe
    style MSN fill:#f3e5f5
    style MPN fill:#fff3e0
    style MGN fill:#e8f5e8
    style RGN fill:#f0f8ff
    style TC fill:#fce4ec
```

## Conditional Routing Logic

```mermaid
graph TD
    subgraph "Routing Flow"
        Start[Node Execution]
        Router{Router Function}
        NextStep[Check next_step]
    end
    
    subgraph "Route Destinations"
        MS[Model Selection]
        MP[Member Prediction]
        MG[MQL Generation]
        RG[Response Generation]
        EH[Error Handler]
        EndNode[END]
    end
    
    Start --> Router
    Router --> NextStep
    
    NextStep -->|MODEL_SELECTION| MS
    NextStep -->|MEMBER_PREDICTION| MP
    NextStep -->|MQL_GENERATION| MG
    NextStep -->|RESPONSE_GENERATION| RG
    NextStep -->|ERROR| EH
    NextStep -->|END| EndNode
    
    MS --> Router
    MP --> Router
    MG --> Router
    RG --> Router
    EH --> EndNode
    
    style Router fill:#fce4ec
    style NextStep fill:#fff3e0
    style MS fill:#f3e5f5
    style MP fill:#fff3e0
    style MG fill:#e8f5e8
    style RG fill:#f0f8ff
    style EH fill:#ffebee
```

## Streaming and UI Integration

```mermaid
graph LR
    subgraph "Chainlit Server"
        Server[Server.py]
        Stream["app.astream()"]
    end
    
    subgraph "State Graph Execution"
        Graph[StateGraph]
        Nodes[Graph Nodes]
        Tools[Tool Calls]
    end
    
    subgraph "UI Visualization"
        Steps[Chainlit Steps]
        ToolSteps[Tool Sub-steps]
        Status[Status Updates]
    end
    
    Server --> Stream
    Stream --> Graph
    Graph --> Nodes
    Nodes --> Tools
    
    Nodes --> Steps
    Tools --> ToolSteps
    Graph --> Status
    
    style Server fill:#e1f5fe
    style Graph fill:#f3e5f5
    style Steps fill:#fff3e0
```

## Key Components

- **StateGraph**: Sequential pipeline with conditional routing based on `next_step` field
- **GraphState**: TypedDict that preserves complete state between nodes with accumulative tool call tracking
- **Router Functions**: Deterministic routing logic based on string matching in `next_step`
- **Tool Integration**: Structured tool calls with error handling and UI visualization
- **Node Specialization**: Each node handles specific domain (orchestration, model selection, member prediction, MQL generation, response formatting)
- **Error Handling**: Dedicated error node with comprehensive error propagation
- **Streaming**: Real-time execution updates through Chainlit with step-by-step visualization
- **State Persistence**: Immutable state updates with complete data flow tracking