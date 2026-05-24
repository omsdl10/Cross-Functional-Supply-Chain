from fastapi.testclient import TestClient

from app.agents.approval import (
    build_approval_queue,
    clear_approval_store,
    decide_approval_request,
    save_approval_queue,
    summarize_approval_queue,
)
from app.agents.impact import assess_risk_events_impact
from app.agents.monitor import poll_logistics_risk_feed
from app.agents.strategy import generate_strategy_plan
from app.main import app
from app.workflows.approval import run_approval_workflow


def _sample_approval_queue() -> list[dict[str, object]]:
    assessments = assess_risk_events_impact(poll_logistics_risk_feed())
    strategy_plan = generate_strategy_plan(assessments)
    return build_approval_queue(strategy_plan)


def test_build_approval_queue() -> None:
    approval_queue = _sample_approval_queue()

    assert len(approval_queue) == 2
    assert approval_queue[0]["approval_id"] == "APR-MON-SHIP-8821"
    assert approval_queue[0]["status"] == "pending"
    assert approval_queue[0]["recommended_strategy"]["strategy_id"] == "switch-supplier-SUP-207"


def test_summarize_approval_queue() -> None:
    approval_queue = _sample_approval_queue()
    summary = summarize_approval_queue(approval_queue)

    assert summary == {
        "approval_count": 2,
        "pending_count": 2,
        "high_risk_approval_count": 1,
        "materials_pending_approval": ["MAT-330", "MAT-445"],
    }


def test_decide_approval_request() -> None:
    clear_approval_store()
    save_approval_queue(_sample_approval_queue())

    decision = decide_approval_request(
        approval_id="APR-MON-SHIP-8821",
        decision="approved",
        selected_strategy_id="switch-supplier-SUP-207",
        comment="Approve secondary supplier activation.",
        decided_by="ops-lead",
    )

    assert decision["status"] == "approved"
    assert decision["selected_strategy"]["supplier_id"] == "SUP-207"
    assert decision["decided_by"] == "ops-lead"


def test_run_approval_workflow() -> None:
    result = run_approval_workflow()

    assert result["strategy_summary"]["strategy_count"] == 5
    assert result["approval_summary"]["approval_count"] == 2
    assert result["approval_queue"][0]["approval_id"] == "APR-MON-SHIP-8821"


def test_approval_api_queue_and_decision() -> None:
    clear_approval_store()
    client = TestClient(app)

    queue_response = client.post("/approval/queue")

    assert queue_response.status_code == 200
    queue_body = queue_response.json()
    assert queue_body["approval_summary"]["approval_count"] == 2

    decision_response = client.post(
        "/approval/queue/APR-MON-SHIP-8821/decision",
        json={
            "decision": "approved",
            "selected_strategy_id": "switch-supplier-SUP-207",
            "comment": "Proceed with approved secondary supplier.",
            "decided_by": "ops-lead",
        },
    )

    assert decision_response.status_code == 200
    decision_body = decision_response.json()
    assert decision_body["status"] == "approved"
    assert decision_body["selected_strategy"]["supplier_id"] == "SUP-207"


def test_approval_api_rejects_invalid_strategy() -> None:
    clear_approval_store()
    save_approval_queue(_sample_approval_queue())
    client = TestClient(app)

    response = client.post(
        "/approval/queue/APR-MON-SHIP-8821/decision",
        json={
            "decision": "approved",
            "selected_strategy_id": "missing-strategy",
        },
    )

    assert response.status_code == 400
