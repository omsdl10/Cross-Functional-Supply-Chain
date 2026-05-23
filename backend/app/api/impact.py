from fastapi import APIRouter, HTTPException

from app.agents.impact import assess_risk_event_impact
from app.agents.monitor import poll_logistics_risk_feed
from app.workflows.impact import run_impact_workflow


router = APIRouter(prefix="/impact", tags=["impact assessment agent"])


@router.get("/events/{event_id}")
def assess_event(event_id: str) -> dict[str, object]:
    event = next(
        (risk_event for risk_event in poll_logistics_risk_feed() if risk_event["event_id"] == event_id),
        None,
    )
    if event is None:
        raise HTTPException(status_code=404, detail="Risk event not found")

    return assess_risk_event_impact(event)


@router.post("/run")
def run_impact_assessment() -> dict[str, object]:
    return run_impact_workflow()
