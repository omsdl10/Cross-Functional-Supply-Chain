from fastapi.testclient import TestClient

from app.agents.approval import (
    clear_approval_store,
    decide_approval_request,
    save_approval_queue,
)
from app.agents.execution import (
    clear_execution_store,
    create_execution_record,
    draft_po_change_request,
    draft_supplier_inquiry_email,
    list_execution_records,
)
from app.main import app
from app.workflows.approval import run_approval_workflow


def _approved_request() -> dict[str, object]:
    clear_approval_store()
    clear_execution_store()
    workflow_result = run_approval_workflow()
    save_approval_queue(workflow_result["approval_queue"])
    return decide_approval_request(
        approval_id="APR-MON-SHIP-8821",
        decision="approved",
        selected_strategy_id="switch-supplier-SUP-207",
        comment="Proceed with supplier switch.",
        decided_by="ops-lead",
    )


def test_draft_supplier_inquiry_email() -> None:
    approval_request = _approved_request()
    email = draft_supplier_inquiry_email(approval_request)

    assert email["to"] == "supply-continuity-sup-207@example.com"
    assert "MAT-445" in email["subject"]
    assert "Atlas Energy Materials" in email["body"]
    assert "switch-supplier-SUP-207" not in email["body"]


def test_draft_po_change_request() -> None:
    approval_request = _approved_request()
    po_change = draft_po_change_request(approval_request)

    assert po_change["request_type"] == "purchase_order_change"
    assert po_change["source_po_id"] == "PO-9001"
    assert po_change["requested_supplier_id"] == "SUP-207"
    assert po_change["material_id"] == "MAT-445"


def test_create_execution_record_requires_approval() -> None:
    approval_request = _approved_request()

    execution = create_execution_record(approval_request["approval_id"])

    assert execution["execution_id"] == "EXEC-APR-MON-SHIP-8821"
    assert execution["status"] == "drafted"
    assert execution["selected_strategy_id"] == "switch-supplier-SUP-207"
    assert execution["po_change_request"]["requested_supplier_id"] == "SUP-207"
    assert len(list_execution_records()) == 1


def test_create_execution_record_rejects_pending_request() -> None:
    clear_approval_store()
    clear_execution_store()
    workflow_result = run_approval_workflow()
    save_approval_queue(workflow_result["approval_queue"])

    try:
        create_execution_record("APR-MON-SHIP-8821")
    except ValueError as exc:
        assert "is not approved" in str(exc)
    else:
        raise AssertionError("Expected pending approval to be rejected")


def test_execution_api_draft_and_history() -> None:
    _approved_request()
    client = TestClient(app)

    draft_response = client.post("/execution/approval/APR-MON-SHIP-8821/draft")

    assert draft_response.status_code == 200
    draft_body = draft_response.json()
    assert draft_body["execution_id"] == "EXEC-APR-MON-SHIP-8821"

    history_response = client.get("/execution/history")

    assert history_response.status_code == 200
    history_body = history_response.json()
    assert len(history_body["executions"]) == 1


def test_execution_api_rejects_unapproved_request() -> None:
    clear_approval_store()
    clear_execution_store()
    workflow_result = run_approval_workflow()
    save_approval_queue(workflow_result["approval_queue"])
    client = TestClient(app)

    response = client.post("/execution/approval/APR-MON-SHIP-8821/draft")

    assert response.status_code == 409
