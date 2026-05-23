from fastapi import APIRouter

from app.agents.monitor import poll_logistics_risk_feed
from app.workflows.monitor import run_monitor_workflow


router = APIRouter(prefix="/monitor", tags=["monitor agent"])


@router.get("/risks")
def detected_risks() -> dict[str, object]:
    risk_events = poll_logistics_risk_feed()
    return {
        "risk_detected": bool(risk_events),
        "risk_events": risk_events,
    }


@router.post("/run")
def run_monitor() -> dict[str, object]:
    return run_monitor_workflow()
