# Cross-Functional Supply Chain Concierge

An autonomous AI workflow for manufacturing and logistics teams that monitors supplier risk, assesses inventory impact, recommends mitigation strategies, and prepares approved execution drafts.

## Product Goal

Manufacturing CFOs need AI that creates operational capacity and responsiveness, not another passive chatbot. This project is designed as an operational supply chain concierge that connects supplier contracts, logistics risk signals, and inventory requirements into a decision-making workflow.

## Current Stage

Stage 2 adds a mock supply chain operating model:

- Supplier master data
- Material master data
- Inventory positions
- Purchase orders
- Shipment statuses
- Risk events
- Supplier contract summaries for future retrieval

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
