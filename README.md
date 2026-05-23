# Cross-Functional Supply Chain Concierge

An autonomous AI workflow for manufacturing and logistics teams that monitors supplier risk, assesses inventory impact, recommends mitigation strategies, and prepares approved execution drafts.

## Product Goal

Manufacturing CFOs need AI that creates operational capacity and responsiveness, not another passive chatbot. This project is designed as an operational supply chain concierge that connects supplier contracts, logistics risk signals, and inventory requirements into a decision-making workflow.

## Current Stage

Stage 6 adds an Impact Assessment Agent:

- Consumes monitor risk events
- Calls inventory and supplier tools
- Calculates days of cover versus delay days
- Classifies production risk
- Summarizes critical materials at risk

## Stage 1 Scope

This first stage establishes the project foundation:

- Backend application skeleton
- Basic health endpoint
- Frontend placeholder
- Documentation structure
- Sample data directories
- Environment configuration template

## Target Workflow

1. **Retrieval**
   - Vectorize supplier contracts, logistics documents, and inventory policies with ChromaDB.

2. **Monitoring**
   - Detect shipping delays, supplier disruptions, environmental risks, and logistics issues.

3. **Impact Assessment**
   - Query inventory and production data to determine whether a risk affects critical materials.

4. **Strategy**
   - Recommend mitigation options such as switching suppliers, buffering stock, or delaying production.

5. **Execution**
   - After human approval, draft supplier emails, purchase order changes, or internal escalation notes.

## Repository Structure

```txt
backend/
  app/
    agents/
    api/
    db/
    retrieval/
    tools/
    workflows/
  tests/
frontend/
data/
  sample_contracts/
  sample_inventory/
  sample_logistics/
docs/
```

## Mock Data

Stage 2 includes a working demo scenario:

```txt
SUP-102 shipment SHIP-8821 is delayed by 7 days.
The shipment affects MAT-445 Lithium Battery Cells.
Current stock covers 4 days of production at 300 units per day.
This creates the first high-impact scenario for the Stage 5-7 agents.
```

## Retrieval

Stage 3 indexes supplier contracts into ChromaDB.

Ingest contracts:

```txt
POST http://localhost:8000/retrieval/contracts/ingest
```

Query contracts:

```txt
GET http://localhost:8000/retrieval/contracts/query?q=inventory cover below 5 days
```

## Operational Tools

Stage 4 exposes the mock operating model through tool functions and API endpoints.

Example endpoints:

```txt
GET http://localhost:8000/tools/suppliers/SUP-102
GET http://localhost:8000/tools/materials/MAT-445/inventory
GET http://localhost:8000/tools/materials/MAT-445/purchase-orders
GET http://localhost:8000/tools/materials/MAT-445/alternate-suppliers
GET http://localhost:8000/tools/materials/MAT-445/risk-snapshot
```

## Monitor Agent

Stage 5 uses LangGraph to run the first autonomous workflow node.

Example endpoints:

```txt
GET http://localhost:8000/monitor/risks
POST http://localhost:8000/monitor/run
```

Example monitor output:

```json
{
  "summary": {
    "risk_detected": true,
    "risk_count": 2,
    "highest_severity": "high",
    "affected_suppliers": ["SUP-102", "SUP-518"],
    "affected_materials": ["MAT-330", "MAT-445"]
  }
}
```

## Impact Assessment Agent

Stage 6 chains monitoring into impact assessment.

Example endpoints:

```txt
GET http://localhost:8000/impact/events/MON-SHIP-8821
POST http://localhost:8000/impact/run
```

Example impact output:

```json
{
  "material_id": "MAT-445",
  "days_of_cover": 4.0,
  "incoming_delay_days": 7,
  "projected_stockout_gap_days": 3.0,
  "production_risk": "high"
}
```

## Local Setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Run tests from the repository root:

```bash
python -m pytest
```

Health check:

```txt
GET http://localhost:8000/health
```

Expected response:

```json
{
  "status": "ok",
  "service": "cross-functional-supply-chain-concierge",
  "stage": "stage-1-foundation"
}
```

## Roadmap

See [docs/roadmap.md](docs/roadmap.md) for the staged GitHub delivery plan.
