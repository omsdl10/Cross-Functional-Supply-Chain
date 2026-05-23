from __future__ import annotations

from typing import Any

from app.tools.operations import (
    build_material_risk_snapshot,
    calculate_days_of_cover,
    get_material_details,
)


SEVERITY_SCORE = {"none": 0, "low": 1, "medium": 2, "high": 3}
CRITICALITY_SCORE = {"low": 1, "medium": 2, "high": 3}


def calculate_stockout_gap(days_of_cover: float, delay_days: int) -> float:
    return round(delay_days - days_of_cover, 2)


def classify_production_risk(
    criticality: str,
    severity: str,
    days_of_cover: float,
    delay_days: int,
) -> str:
    stockout_gap = calculate_stockout_gap(days_of_cover, delay_days)
    criticality_score = CRITICALITY_SCORE.get(criticality, 1)
    severity_score = SEVERITY_SCORE.get(severity, 0)

    if stockout_gap >= 2 and criticality_score >= 3:
        return "high"
    if stockout_gap > 0 and severity_score >= 2:
        return "high"
    if stockout_gap > 0:
        return "medium"
    if days_of_cover <= 5 and criticality_score >= 3:
        return "medium"
    return "low"


def assess_risk_event_impact(risk_event: dict[str, Any]) -> dict[str, Any]:
    material_id = risk_event["material_id"]
    material = get_material_details(material_id)
    coverage = calculate_days_of_cover(material_id)
    snapshot = build_material_risk_snapshot(material_id)

    if material is None or coverage is None or snapshot is None:
        return {
            "risk_event": risk_event,
            "material_id": material_id,
            "assessment_status": "not_found",
            "production_risk": "unknown",
            "impact_summary": "Material data was not found for impact assessment.",
        }

    delay_days = int(risk_event["delay_days"])
    days_of_cover = float(coverage["days_of_cover"])
    stockout_gap = calculate_stockout_gap(days_of_cover, delay_days)
    production_risk = classify_production_risk(
        material["criticality"],
        risk_event["severity"],
        days_of_cover,
        delay_days,
    )

    if stockout_gap > 0:
        summary = (
            f"{material['name']} has {days_of_cover:g} days of cover against a "
            f"{delay_days}-day delay, creating a projected stockout gap of "
            f"{stockout_gap:g} days."
        )
    else:
        summary = (
            f"{material['name']} has {days_of_cover:g} days of cover against a "
            f"{delay_days}-day delay, so current inventory can absorb this event."
        )

    return {
        "assessment_status": "assessed",
        "event_id": risk_event["event_id"],
        "supplier_id": risk_event["supplier_id"],
        "material_id": material_id,
        "shipment_id": risk_event["shipment_id"],
        "risk_type": risk_event["risk_type"],
        "risk_severity": risk_event["severity"],
        "material_name": material["name"],
        "material_criticality": material["criticality"],
        "current_stock": coverage["current_stock"],
        "daily_usage": coverage["daily_usage"],
        "days_of_cover": days_of_cover,
        "incoming_delay_days": delay_days,
        "projected_stockout_gap_days": stockout_gap,
        "production_risk": production_risk,
        "alternate_supplier_count": len(snapshot["alternate_suppliers"]),
        "open_purchase_order_count": len(snapshot["open_purchase_orders"]),
        "impact_summary": summary,
    }


def assess_risk_events_impact(risk_events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [assess_risk_event_impact(event) for event in risk_events]


def summarize_impact_assessments(assessments: list[dict[str, Any]]) -> dict[str, Any]:
    if not assessments:
        return {
            "assessed_count": 0,
            "highest_production_risk": "none",
            "critical_materials_at_risk": [],
            "stockout_risk_count": 0,
        }

    risk_rank = {"unknown": 0, "low": 1, "medium": 2, "high": 3}
    highest = max(
        (assessment["production_risk"] for assessment in assessments),
        key=lambda risk: risk_rank.get(risk, 0),
    )

    critical_materials = sorted(
        {
            assessment["material_id"]
            for assessment in assessments
            if assessment.get("material_criticality") == "high"
            and assessment["production_risk"] in {"medium", "high"}
        }
    )

    stockout_risk_count = sum(
        1
        for assessment in assessments
        if assessment.get("projected_stockout_gap_days", 0) > 0
    )

    return {
        "assessed_count": len(assessments),
        "highest_production_risk": highest,
        "critical_materials_at_risk": critical_materials,
        "stockout_risk_count": stockout_risk_count,
    }
