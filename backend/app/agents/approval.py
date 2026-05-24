from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any


VALID_APPROVAL_DECISIONS = {"approved", "rejected", "needs_more_info"}


@dataclass(frozen=True)
class ApprovalRequest:
    approval_id: str
    event_id: str
    material_id: str
    material_name: str
    production_risk: str
    recommended_strategy: dict[str, Any]
    available_strategies: list[dict[str, Any]]
    status: str
    created_at: str


APPROVAL_STORE: dict[str, dict[str, Any]] = {}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_approval_request(strategy_plan: dict[str, Any]) -> dict[str, Any]:
    request = ApprovalRequest(
        approval_id=f"APR-{strategy_plan['event_id']}",
        event_id=strategy_plan["event_id"],
        material_id=strategy_plan["material_id"],
        material_name=strategy_plan["material_name"],
        production_risk=strategy_plan["production_risk"],
        recommended_strategy=strategy_plan["recommended_strategy"],
        available_strategies=strategy_plan["strategies"],
        status="pending",
        created_at=_now_iso(),
    )
    return asdict(request)


def build_approval_queue(strategy_plan: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [build_approval_request(plan) for plan in strategy_plan]


def save_approval_queue(approval_queue: list[dict[str, Any]]) -> list[dict[str, Any]]:
    for approval_request in approval_queue:
        existing = APPROVAL_STORE.get(approval_request["approval_id"])
        if existing and existing["status"] != "pending":
            continue
        APPROVAL_STORE[approval_request["approval_id"]] = approval_request

    return list(APPROVAL_STORE.values())


def list_approval_requests(status: str | None = None) -> list[dict[str, Any]]:
    requests = list(APPROVAL_STORE.values())
    if status is not None:
        requests = [request for request in requests if request["status"] == status]
    return sorted(requests, key=lambda request: request["approval_id"])


def get_approval_request(approval_id: str) -> dict[str, Any] | None:
    return APPROVAL_STORE.get(approval_id)


def clear_approval_store() -> None:
    APPROVAL_STORE.clear()


def decide_approval_request(
    approval_id: str,
    decision: str,
    selected_strategy_id: str | None = None,
    comment: str = "",
    decided_by: str = "human-approver",
) -> dict[str, Any]:
    if decision not in VALID_APPROVAL_DECISIONS:
        raise ValueError(f"Decision must be one of {sorted(VALID_APPROVAL_DECISIONS)}")

    approval_request = get_approval_request(approval_id)
    if approval_request is None:
        raise KeyError(f"Approval request {approval_id} was not found")

    selected_strategy = approval_request["recommended_strategy"]
    if selected_strategy_id is not None:
        selected_strategy = next(
            (
                strategy
                for strategy in approval_request["available_strategies"]
                if strategy["strategy_id"] == selected_strategy_id
            ),
            None,
        )
        if selected_strategy is None:
            raise ValueError(
                f"Strategy {selected_strategy_id} is not available for {approval_id}"
            )

    updated = {
        **approval_request,
        "status": decision,
        "selected_strategy": selected_strategy if decision == "approved" else None,
        "decision_comment": comment,
        "decided_by": decided_by,
        "decided_at": _now_iso(),
    }
    APPROVAL_STORE[approval_id] = updated
    return updated


def summarize_approval_queue(approval_queue: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "approval_count": len(approval_queue),
        "pending_count": sum(
            1 for approval_request in approval_queue if approval_request["status"] == "pending"
        ),
        "high_risk_approval_count": sum(
            1
            for approval_request in approval_queue
            if approval_request["production_risk"] == "high"
        ),
        "materials_pending_approval": sorted(
            {
                approval_request["material_id"]
                for approval_request in approval_queue
                if approval_request["status"] == "pending"
            }
        ),
    }
