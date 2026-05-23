# Roadmap

## Stage 1: Project Foundation

- Repository structure
- Backend health endpoint
- Frontend placeholder
- Documentation
- Environment template

## Stage 2: Mock Supply Chain Data

- Supplier dataset
- Inventory dataset
- Shipment dataset
- Purchase order sample data
- Data loading utilities
- Tests for loading and querying mock data

## Stage 3: ChromaDB Supplier Retrieval

- Supplier contract ingestion
- Text chunking
- Embedding storage
- Contract query endpoint
- Tests for contract ingestion and retrieval

## Stage 4: Operational Tool Layer

- Supplier lookup tools
- Inventory tools
- Purchase order tools
- Days-of-cover calculation
- Alternate supplier lookup
- Material risk snapshot API

## Stage 5: Monitor Agent

- Mock logistics polling
- Risk event schema
- LangGraph monitor node
- Monitor API endpoints
- Tests for delayed and at-risk shipments

## Stage 6: Impact Assessment Agent

- Inventory impact calculation
- Critical material check
- Stockout risk scoring
- LangGraph monitor-to-impact workflow
- Impact API endpoints

## Stage 7: Strategy Agent

- Three mitigation strategies
- Cost, lead time, and risk scoring
- Recommended action selection

## Stage 8: Human Approval Workflow

- Approval checkpoint
- API endpoint for approval decisions
- Approval queue foundation

## Stage 9: Execution Agent

- Supplier inquiry email draft
- Purchase order change request draft
- Execution history

## Stage 10: End-to-End Demo

- Full risk-to-execution flow
- Demo scenario
- README walkthrough
