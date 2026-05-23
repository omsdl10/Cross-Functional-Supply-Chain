from fastapi.testclient import TestClient

from app.agents.impact import assess_risk_event_impact, assess_risk_events_impact
from app.agents.monitor import poll_logistics_risk_feed
from app.agents.strategy import (
    generate_mitigation_strategies,
    generate_strategy_plan,
    summarize_strategy_plan,
)
from app.main import app
from app.workflows.strategy import run_strategy_workflow


def test_generate_mitigation_strategies_for_lithium_cells() -> None:
    risk_event = poll_logistics_risk_feed()[0]
    assessment = assess_risk_event_impact(risk_event)

    plan = generate_mitigation_strategies(assessment)

    assert plan["event_id"] == "MON-SHIP-8821"
    assert plan["material_id"] == "MAT-445"
    assert len(plan["strategies"]) == 3
    assert {strategy["name"] for strategy in plan["strategies"]} == {
        "Switch to secondary supplier",
        "Buffer existing stock",
        "Delay production start",
    }
    assert plan["recommended_strategy"]["name"] == "Switch to secondary supplier"
    assert plan["recommended_strategy"]["supplier_id"] == "SUP-207"


def test_generate_strategy_plan_filters_actionable_assessments() -> None:
    assessments = assess_risk_events_impact(poll_logistics_risk_feed())
    strategy_plan = generate_strategy_plan(assessments)

    assert len(strategy_plan) == 2
    assert {plan["material_id"] for plan in strategy_plan} == {"MAT-330", "MAT-445"}


def test_summarize_strategy_plan() -> None:
    assessments = assess_risk_events_impact(poll_logistics_risk_feed())
    strategy_plan = generate_strategy_plan(assessments)
    summary = summarize_strategy_plan(strategy_plan)

    assert summary["strategy_count"] == 5
    assert summary["materials_with_recommendations"] == ["MAT-330", "MAT-445"]
    assert "Switch to secondary supplier" in summary["recommended_actions"]


def test_run_strategy_workflow() -> None:
    result = run_strategy_workflow()

    assert result["monitor_summary"]["risk_count"] == 2
    assert result["impact_summary"]["highest_production_risk"] == "high"
    assert result["strategy_summary"]["strategy_count"] == 5
    assert result["strategy_plan"][0]["recommended_strategy"]["name"]


def test_strategy_api_run() -> None:
    client = TestClient(app)

    response = client.post("/strategy/run")

    assert response.status_code == 200
    body = response.json()
    assert body["strategy_summary"]["strategy_count"] == 5
    assert body["strategy_plan"][0]["material_id"] == "MAT-445"


def test_strategy_api_event_lookup() -> None:
    client = TestClient(app)

    response = client.get("/strategy/events/MON-SHIP-8821")

    assert response.status_code == 200
    body = response.json()
    assert body["recommended_strategy"]["supplier_id"] == "SUP-207"
