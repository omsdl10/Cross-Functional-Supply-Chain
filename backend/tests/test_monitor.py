from fastapi.testclient import TestClient

from app.agents.monitor import poll_logistics_risk_feed, summarize_risk_events
from app.main import app
from app.workflows.monitor import run_monitor_workflow


def test_poll_logistics_risk_feed_detects_delays() -> None:
    events = poll_logistics_risk_feed()

    assert len(events) == 2
    assert events[0]["shipment_id"] == "SHIP-8821"
    assert events[0]["supplier_id"] == "SUP-102"
    assert events[0]["material_id"] == "MAT-445"
    assert events[0]["severity"] == "high"
    assert events[0]["delay_days"] == 7


def test_summarize_risk_events() -> None:
    events = poll_logistics_risk_feed()
    summary = summarize_risk_events(events)

    assert summary == {
        "risk_detected": True,
        "risk_count": 2,
        "highest_severity": "high",
        "affected_suppliers": ["SUP-102", "SUP-518"],
        "affected_materials": ["MAT-330", "MAT-445"],
    }


def test_run_monitor_workflow() -> None:
    result = run_monitor_workflow()

    assert result["summary"]["risk_detected"] is True
    assert result["summary"]["highest_severity"] == "high"
    assert result["risk_events"][0]["shipment_id"] == "SHIP-8821"


def test_monitor_api_run() -> None:
    client = TestClient(app)

    response = client.post("/monitor/run")

    assert response.status_code == 200
    body = response.json()
    assert body["summary"]["risk_count"] == 2
    assert body["summary"]["highest_severity"] == "high"
