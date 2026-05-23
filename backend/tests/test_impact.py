from fastapi.testclient import TestClient

from app.agents.impact import (
    assess_risk_event_impact,
    assess_risk_events_impact,
    calculate_stockout_gap,
    classify_production_risk,
    summarize_impact_assessments,
)
from app.agents.monitor import poll_logistics_risk_feed
from app.main import app
from app.workflows.impact import run_impact_workflow


def test_calculate_stockout_gap() -> None:
    assert calculate_stockout_gap(days_of_cover=4.0, delay_days=7) == 3.0
    assert calculate_stockout_gap(days_of_cover=10.0, delay_days=3) == -7.0


def test_classify_production_risk_for_critical_delay() -> None:
    risk = classify_production_risk(
        criticality="high",
        severity="high",
        days_of_cover=4.0,
        delay_days=7,
    )

    assert risk == "high"


def test_assess_risk_event_impact_for_lithium_cells() -> None:
    risk_event = poll_logistics_risk_feed()[0]
    assessment = assess_risk_event_impact(risk_event)

    assert assessment["assessment_status"] == "assessed"
    assert assessment["material_id"] == "MAT-445"
    assert assessment["material_criticality"] == "high"
    assert assessment["days_of_cover"] == 4.0
    assert assessment["incoming_delay_days"] == 7
    assert assessment["projected_stockout_gap_days"] == 3.0
    assert assessment["production_risk"] == "high"
    assert assessment["alternate_supplier_count"] == 1


def test_summarize_impact_assessments() -> None:
    assessments = assess_risk_events_impact(poll_logistics_risk_feed())
    summary = summarize_impact_assessments(assessments)

    assert summary == {
        "assessed_count": 2,
        "highest_production_risk": "high",
        "critical_materials_at_risk": ["MAT-330", "MAT-445"],
        "stockout_risk_count": 1,
    }


def test_run_impact_workflow() -> None:
    result = run_impact_workflow()

    assert result["monitor_summary"]["risk_count"] == 2
    assert result["impact_summary"]["highest_production_risk"] == "high"
    assert result["impact_assessments"][0]["material_id"] == "MAT-445"


def test_impact_api_run() -> None:
    client = TestClient(app)

    response = client.post("/impact/run")

    assert response.status_code == 200
    body = response.json()
    assert body["impact_summary"]["assessed_count"] == 2
    assert body["impact_summary"]["highest_production_risk"] == "high"


def test_impact_api_event_lookup() -> None:
    client = TestClient(app)

    response = client.get("/impact/events/MON-SHIP-8821")

    assert response.status_code == 200
    body = response.json()
    assert body["material_id"] == "MAT-445"
    assert body["production_risk"] == "high"
