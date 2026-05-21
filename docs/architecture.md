# Architecture

## System Overview

The Cross-Functional Supply Chain Concierge is planned as an agentic workflow that connects supplier risk signals, retrieval over supplier documents, and internal operational data.

```mermaid
flowchart LR
    A["External Risk Feeds"] --> B["Monitor Agent"]
    C["Supplier Contracts"] --> D["ChromaDB Retrieval"]
    E["Inventory Data"] --> F["Operational Tools"]
    B --> G["Impact Assessment Agent"]
    D --> G
    F --> G
    G --> H["Strategy Agent"]
    H --> I["Human Approval"]
    I --> J["Execution Agent"]
    J --> K["PO Change Request or Supplier Email"]
```

## Initial Components

- **Backend API:** FastAPI service for health checks and future workflow endpoints.
- **Agent Layer:** Planned LangGraph nodes for monitoring, impact assessment, strategy, approval, and execution.
- **Retrieval Layer:** Planned ChromaDB vector store for supplier contracts and logistics documents.
- **Tool Layer:** Planned inventory, supplier, purchase order, and material lookup tools.
- **Frontend:** Placeholder operations dashboard that will become the approval and monitoring console.

## Stage 1 Boundary

Stage 1 does not implement autonomous decision-making yet. It creates the repository foundation needed to add mock data, retrieval, tools, and LangGraph orchestration in later stages.
