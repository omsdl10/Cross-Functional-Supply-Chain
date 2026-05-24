from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any

from app.agents.approval import get_approval_request
from app.tools.operations import get_open_purchase_orders, get_supplier_details


@dataclass(frozen=True)
class ExecutionRecord:
    execution_id: str
    approval_id: str
    event_id: str
    material_id: str
    selected_strategy_id: str
    status: str
    supplier_inquiry_email: dict[str, str]
    po_change_request: dict[str, Any]
    internal_alert: dict[str, str]
    created_at: str


EXECUTION_STORE: dict[str, dict[str, Any]] = {}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _require_approved_request(approval_id: str) -> dict[str, Any]:
    approval_request = get_approval_request(approval_id)
    if approval_request is None:
        raise KeyError(f"Approval request {approval_id} was not found")
    if approval_request["status"] != "approved":
        raise ValueError(f"Approval request {approval_id} is not approved")
    if not approval_request.get("selected_strategy"):
        raise ValueError(f"Approval request {approval_id} has no selected strategy")
    return approval_request


def draft_supplier_inquiry_email(approval_request: dict[str, Any]) -> dict[str, str]:
    strategy = approval_request["selected_strategy"]
    supplier = get_supplier_details(strategy["supplier_id"])
    supplier_name = supplier["name"] if supplier else strategy["supplier_id"]

    return {
        "to": f"supply-continuity-{strategy['supplier_id'].lower()}@example.com",
        "subject": (
            f"Urgent supply continuity request for {approval_request['material_id']}"
        ),
        "body": (
            f"Hello {supplier_name} team,\n\n"
            f"We approved the mitigation strategy '{strategy['name']}' for "
            f"{approval_request['material_name']} ({approval_request['material_id']}).\n\n"
            f"Requested action: {strategy['action']}\n"
            f"Target execution window: {strategy['execution_days']} day(s).\n"
            f"Approval reference: {approval_request['approval_id']}.\n\n"
            "Please confirm available capacity, earliest ship date, and any cost "
            "impact today.\n\n"
            "Regards,\nSupply Chain Concierge"
        ),
    }


def draft_po_change_request(approval_request: dict[str, Any]) -> dict[str, Any]:
    strategy = approval_request["selected_strategy"]
    open_orders = get_open_purchase_orders(material_id=approval_request["material_id"])
    source_order = open_orders[0] if open_orders else {}

    return {
        "request_type": "purchase_order_change",
        "approval_id": approval_request["approval_id"],
        "source_po_id": source_order.get("po_id"),
        "material_id": approval_request["material_id"],
        "current_supplier_id": approval_request.get("recommended_strategy", {}).get(
            "supplier_id"
        ),
        "requested_supplier_id": strategy["supplier_id"],
        "requested_action": strategy["action"],
        "estimated_cost_impact_percent": strategy["estimated_cost_impact_percent"],
        "reason": (
            f"Approved mitigation for {approval_request['production_risk']} production "
            f"risk on event {approval_request['event_id']}."
        ),
    }


def draft_internal_alert(approval_request: dict[str, Any]) -> dict[str, str]:
    strategy = approval_request["selected_strategy"]

    return {
        "channel": "production-planning",
        "title": f"Approved mitigation for {approval_request['material_id']}",
        "message": (
            f"{approval_request['material_name']} has an approved mitigation: "
            f"{strategy['name']}. Expected execution window is "
            f"{strategy['execution_days']} day(s)."
        ),
    }


def create_execution_record(approval_id: str) -> dict[str, Any]:
    approval_request = _require_approved_request(approval_id)
    strategy = approval_request["selected_strategy"]
    execution_id = f"EXEC-{approval_request['approval_id']}"

    record = ExecutionRecord(
        execution_id=execution_id,
        approval_id=approval_request["approval_id"],
        event_id=approval_request["event_id"],
        material_id=approval_request["material_id"],
        selected_strategy_id=strategy["strategy_id"],
        status="drafted",
        supplier_inquiry_email=draft_supplier_inquiry_email(approval_request),
        po_change_request=draft_po_change_request(approval_request),
        internal_alert=draft_internal_alert(approval_request),
        created_at=_now_iso(),
    )
    EXECUTION_STORE[execution_id] = asdict(record)
    return EXECUTION_STORE[execution_id]


def list_execution_records() -> list[dict[str, Any]]:
    return sorted(EXECUTION_STORE.values(), key=lambda record: record["execution_id"])


def get_execution_record(execution_id: str) -> dict[str, Any] | None:
    return EXECUTION_STORE.get(execution_id)


def clear_execution_store() -> None:
    EXECUTION_STORE.clear()
