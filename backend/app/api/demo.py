from fastapi import APIRouter, HTTPException

from app.agents.demo import run_end_to_end_demo


router = APIRouter(prefix="/demo", tags=["end-to-end demo"])


@router.post("/run")
def run_demo(event_id: str = "MON-SHIP-8821") -> dict[str, object]:
    try:
        return run_end_to_end_demo(event_id=event_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
