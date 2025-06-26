# OpenAI Agents Multi-Agent Architecture

This diagram shows the agent hierarchies and tool calling setup in the openai-agents implementation.

## Agent Hierarchy with Handoff System

```mermaid
graph TD
    A[User Query] --> B[Orchestration Agent]
    
    subgraph "Orchestration Agent"
        B --> C[Intent Analysis]
        C --> D{Handoff Decision}
    end
    
    subgraph "Specialized Agents"
        E[Member Prediction Agent]
        F[MQL Agent]
    end
    
    D -->|Model/Members Unknown| E
    D -->|Members Known, Need MQL| F
    D -->|Direct Response| G[User Response]
    
    E --> H{Complete?}
    H -->|Need MQL| F
    H -->|Done| G
    
    F --> G
    
    style B fill:#e1f5fe
    style E fill:#f3e5f5
    style F fill:#e8f5e8
```

## Agent-Tool Distribution

```mermaid
graph TB
    subgraph "Orchestration Agent"
        OA[Orchestration Agent]
        OA_Role[Role: Query routing & coordination]
        OA_Tools[Tools: None]
    end
    
    subgraph "Member Prediction Agent"
        MPA[Member Prediction Agent]
        MPA_Role[Role: OLAP cube navigation]
        MPA_Tools[Tools: 5 Vena API tools]
        
        subgraph "MPA Tools"
            T1[list_models]
            T2[get_model_info]
            T3[get_top_level_members]
            T4[get_children_of_member]
            T5[search_members]
        end
    end
    
    subgraph "MQL Agent"
        MQLA[MQL Agent]
        MQLA_Role[Role: MQL query generation]
        MQLA_Tools[Tools: None - Knowledge-based]
    end
    
    subgraph "Vena Tools Integration"
        VT[vena_tools.py]
        VC[Vena Client]
    end
    
    OA --> OA_Role
    OA --> OA_Tools
    
    MPA --> MPA_Role
    MPA --> MPA_Tools
    MPA_Tools --> T1
    MPA_Tools --> T2
    MPA_Tools --> T3
    MPA_Tools --> T4
    MPA_Tools --> T5
    
    MQLA --> MQLA_Role
    MQLA --> MQLA_Tools
    
    T1 --> VT
    T2 --> VT
    T3 --> VT
    T4 --> VT
    T5 --> VT
    VT --> VC
    
    style OA fill:#e1f5fe
    style MPA fill:#f3e5f5
    style MQLA fill:#e8f5e8
    style VT fill:#fce4ec
```

## Built-in Handoff System

```mermaid
graph LR
    subgraph "OpenAI Agents SDK"
        SDK[OpenAI Agents SDK]
        Runner["Runner.run_streamed()"]
        Handoffs["Built-in Handoff System"]
    end
    
    subgraph "Agent Configuration"
        OA[Orchestration Agent]
        OA_Config["handoffs=[member_prediction_agent,<br/>mql_agent]"]
        
        MPA_Desc[MemberPredictionAgent<br/>handoff_description]
        MQLA_Desc[MQLAgent<br/>handoff_description]
    end
    
    subgraph "Execution Flow"
        Query[User Query]
        Analysis[Intent Analysis]
        Selection[Agent Selection]
        Execution[Tool Execution]
        Response[Streamed Response]
    end
    
    SDK --> Runner
    Runner --> Handoffs
    
    OA --> OA_Config
    OA_Config --> MPA_Desc
    OA_Config --> MQLA_Desc
    
    Query --> Analysis
    Analysis --> Selection
    Selection --> Execution
    Execution --> Response
    
    Handoffs --> Selection
    
    style SDK fill:#fff3e0
    style Runner fill:#f0f8ff
    style Handoffs fill:#fce4ec
```

## Tool Calling Flow

```mermaid
graph TD
    subgraph "Member Prediction Agent Workflow"
        MPA[Member Prediction Agent]
        Phase1[Phase 1: Model Selection]
        Phase2[Phase 2: Planning & Analysis]
        Phase3[Phase 3: Member Search]
    end
    
    subgraph "Tool Execution Sequence"
        Step1[list_models]
        Step2[get_model_info]
        Step3[get_top_level_members]
        Step4[get_children_of_member]
        Step5[search_members]
    end
    
    subgraph "Vena API Integration"
        API[Vena API Client]
        Models[Model Management]
        Members[Member Navigation]
        Search[Member Search]
    end
    
    MPA --> Phase1
    Phase1 --> Step1
    Phase1 --> Step2
    
    MPA --> Phase2
    Phase2 --> Step2
    Phase2 --> Step3
    
    MPA --> Phase3
    Phase3 --> Step4
    Phase3 --> Step5
    
    Step1 --> API
    Step2 --> API
    Step3 --> API
    Step4 --> API
    Step5 --> API
    
    API --> Models
    API --> Members
    API --> Search
    
    style MPA fill:#f3e5f5
    style API fill:#fce4ec
```

## Streaming and Event Handling

```mermaid
graph LR
    subgraph "Event Stream Processing"
        Events["stream_events()"]
        Buffer[Event Buffer]
    end
    
    subgraph "Event Types"
        E1[agent_updated_stream_event]
        E2[run_item_stream_event]
        E3[raw_response_event]
    end
    
    subgraph "UI Visualization"
        Steps[Chainlit Steps]
        Handoff[Agent Handoff Indicators]
        Tools[Tool Execution Progress]
        Tokens[Real-time Token Stream]
    end
    
    Events --> Buffer
    Buffer --> E1
    Buffer --> E2
    Buffer --> E3
    
    E1 --> Handoff
    E2 --> Tools
    E3 --> Tokens
    
    Handoff --> Steps
    Tools --> Steps
    Tokens --> Steps
    
    style Events fill:#e1f5fe
    style Steps fill:#f0f8ff
```

## Multi-Agent Coordination Pattern

```mermaid
graph TB
    subgraph "Coordination Layer"
        Coordinator[Orchestration Agent]
        Routing[Intelligent Routing Logic]
    end
    
    subgraph "Execution Layer"
        Agent1[Member Prediction Agent]
        Agent2[MQL Agent]
        Chain[Agent Chaining]
    end
    
    subgraph "Tool Layer"
        ToolSet1[Vena API Tools]
        ToolSet2[Knowledge Base]
    end
    
    subgraph "Integration Layer"
        VenaAPI[Vena OLAP Platform]
        Streaming[Real-time Streaming]
    end
    
    Coordinator --> Routing
    Routing --> Agent1
    Routing --> Agent2
    Agent1 --> Chain
    Chain --> Agent2
    
    Agent1 --> ToolSet1
    Agent2 --> ToolSet2
    
    ToolSet1 --> VenaAPI
    Agent1 --> Streaming
    Agent2 --> Streaming
    
    style Coordinator fill:#e1f5fe
    style Agent1 fill:#f3e5f5
    style Agent2 fill:#e8f5e8
    style VenaAPI fill:#fce4ec
```

## Key Components

- **Orchestration Agent**: Top-level coordinator with handoff references to specialized agents
- **Member Prediction Agent**: OLAP specialist with 5 Vena API tools for model and member operations
- **MQL Agent**: Knowledge-based query generator with no tools (embedded MQL expertise)
- **Built-in Handoff System**: OpenAI Agents SDK native handoff with direct object references
- **Tool Distribution**: Centralized tools in vena_tools.py with @function_tool decorators
- **Streaming Architecture**: Event-driven streaming with real-time progress tracking
- **Agent Chaining**: MemberPredictionAgent → MQLAgent workflow for end-to-end processing
- **Error Handling**: SDK-specific exception handling with comprehensive error types