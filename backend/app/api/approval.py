from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, Query

from app.agents.approval import (
    decide_approval_request,
    get_approval_request,
    list_approval_requests,
    save_approval_queue,
)
from app.workflows.approval import run_approval_workflow


router = APIRouter(prefix="/approval", tags=["human approval"])


class ApprovalDecisionRequest(BaseModel):
    decision: str
    selected_strategy_id: str | None = None
    comment: str = ""
    decided_by: str = "human-approver"


@router.post("/queue")
def create_approval_queue() -> dict[str, object]:
    workflow_result = run_approval_workflow()
    saved_queue = save_approval_queue(workflow_result["approval_queue"])
    return {
        **workflow_result,
        "approval_queue": saved_queue,
    }


@router.get("/queue")
def approval_queue(
    status: str | None = Query(None),
) -> dict[str, object]:
    return {
        "approval_queue": list_approval_requests(status=status),
    }


@router.get("/queue/{approval_id}")
def approval_request(approval_id: str) -> dict[str, object]:
    request = get_approval_request(approval_id)
    if request is None:
        raise HTTPException(status_code=404, detail="Approval request not found")

    return request


@router.post("/queue/{approval_id}/decision")
def decide_approval(
    approval_id: str,
    decision_request: ApprovalDecisionRequest,
) -> dict[str, object]:
    try:
        return decide_approval_request(
            approval_id=approval_id,
            decision=decision_request.decision,
            selected_strategy_id=decision_request.selected_strategy_id,
            comment=decision_request.comment,
            decided_by=decision_request.decided_by,
        )
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
