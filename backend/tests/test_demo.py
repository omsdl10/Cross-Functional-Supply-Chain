from fastapi.testclient import TestClient

from app.agents.demo import run_end_to_end_demo
from app.main import app


def test_run_end_to_end_demo() -> None:
    result = run_end_to_end_demo()

    assert result["demo_name"] == "supplier-delay-to-approved-execution-draft"
    assert result["event_id"] == "MON-SHIP-8821"
    assert result["monitor_summary"]["risk_count"] == 2
    assert result["impact_summary"]["highest_production_risk"] == "high"
    assert "Switch to secondary supplier" in result["strategy_summary"]["recommended_actions"]
    assert result["approval_decision"]["status"] == "approved"
    assert result["approval_decision"]["selected_strategy"]["supplier_id"] == "SUP-207"
    assert result["execution_record"]["execution_id"] == "EXEC-APR-MON-SHIP-8821"
    assert result["execution_record"]["po_change_request"]["requested_supplier_id"] == "SUP-207"


def test_demo_api_run() -> None:
    client = TestClient(app)

    response = client.post("/demo/run")

    assert response.status_code == 200
    body = response.json()
    assert body["approval_decision"]["status"] == "approved"
    assert body["execution_record"]["supplier_inquiry_email"]["to"] == (
        "supply-continuity-sup-207@example.com"
    )


def test_demo_api_missing_event() -> None:
    client = TestClient(app)

    response = client.post("/demo/run", params={"event_id": "missing-event"})

    assert response.status_code == 404
