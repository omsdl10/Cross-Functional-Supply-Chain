from fastapi import APIRouter, HTTPException

from app.agents.execution import (
    create_execution_record,
    get_execution_record,
    list_execution_records,
)


router = APIRouter(prefix="/execution", tags=["execution agent"])


@router.post("/approval/{approval_id}/draft")
def draft_execution(approval_id: str) -> dict[str, object]:
    try:
        return create_execution_record(approval_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.get("/history")
def execution_history() -> dict[str, object]:
    return {
        "executions": list_execution_records(),
    }


@router.get("/history/{execution_id}")
def execution_record(execution_id: str) -> dict[str, object]:
    record = get_execution_record(execution_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Execution record not found")

    return record
