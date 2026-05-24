from __future__ import annotations

from typing import Any

from app.agents.approval import (
    clear_approval_store,
    decide_approval_request,
    save_approval_queue,
)
from app.agents.execution import clear_execution_store, create_execution_record
from app.workflows.approval import run_approval_workflow


DEFAULT_DEMO_EVENT_ID = "MON-SHIP-8821"


def _find_approval_for_event(
    approval_queue: list[dict[str, Any]],
    event_id: str,
) -> dict[str, Any]:
    approval_request = next(
        (request for request in approval_queue if request["event_id"] == event_id),
        None,
    )
    if approval_request is None:
        raise ValueError(f"No approval request found for event {event_id}")
    return approval_request


def run_end_to_end_demo(event_id: str = DEFAULT_DEMO_EVENT_ID) -> dict[str, Any]:
    clear_approval_store()
    clear_execution_store()

    workflow_result = run_approval_workflow()
    saved_approval_queue = save_approval_queue(workflow_result["approval_queue"])
    approval_request = _find_approval_for_event(saved_approval_queue, event_id)
    selected_strategy = approval_request["recommended_strategy"]

    approval_decision = decide_approval_request(
        approval_id=approval_request["approval_id"],
        decision="approved",
        selected_strategy_id=selected_strategy["strategy_id"],
        comment="Auto-approved by Stage 10 demo runner.",
        decided_by="demo-runner",
    )
    execution_record = create_execution_record(approval_decision["approval_id"])

    return {
        "demo_name": "supplier-delay-to-approved-execution-draft",
        "event_id": event_id,
        "monitor_summary": workflow_result["monitor_summary"],
        "impact_summary": workflow_result["impact_summary"],
        "strategy_summary": workflow_result["strategy_summary"],
        "approval_summary": workflow_result["approval_summary"],
        "approval_decision": approval_decision,
        "execution_record": execution_record,
        "narrative": (
            "Detected a supplier logistics risk, assessed inventory impact, selected "
            "a mitigation strategy, captured approval, and drafted execution artifacts."
        ),
    }
