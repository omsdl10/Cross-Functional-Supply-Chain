from fastapi import APIRouter, HTTPException

from app.agents.impact import assess_risk_event_impact
from app.agents.monitor import poll_logistics_risk_feed
from app.agents.strategy import generate_mitigation_strategies
from app.workflows.strategy import run_strategy_workflow


router = APIRouter(prefix="/strategy", tags=["strategy agent"])


@router.get("/events/{event_id}")
def event_strategies(event_id: str) -> dict[str, object]:
    risk_event = next(
        (event for event in poll_logistics_risk_feed() if event["event_id"] == event_id),
        None,
    )
    if risk_event is None:
        raise HTTPException(status_code=404, detail="Risk event not found")

    assessment = assess_risk_event_impact(risk_event)
    if assessment["production_risk"] not in {"medium", "high"}:
        raise HTTPException(
            status_code=409,
            detail="Risk event does not require mitigation strategy",
        )

    return generate_mitigation_strategies(assessment)


@router.post("/run")
def run_strategy() -> dict[str, object]:
    return run_strategy_workflow()
