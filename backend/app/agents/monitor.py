from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from app.db.mock_data import load_mock_supply_chain_data


RISK_STATUSES = {"delayed", "at_risk"}


@dataclass(frozen=True)
class SupplierRiskEvent:
    event_id: str
    supplier_id: str
    material_id: str
    shipment_id: str
    risk_type: str
    severity: str
    description: str
    delay_days: int
    location: str
    detected_at: str


def _matching_risk_description(
    shipment_id: str,
    fallback: str,
) -> tuple[str, str]:
    data = load_mock_supply_chain_data()
    risk_event = next(
        (event for event in data.risk_events if event["shipment_id"] == shipment_id),
        None,
    )
    if risk_event is None:
        return fallback, ""

    return risk_event["description"], risk_event["detected_at"]


def poll_logistics_risk_feed() -> list[dict[str, Any]]:
    data = load_mock_supply_chain_data()
    events: list[SupplierRiskEvent] = []

    for shipment in data.shipments:
        delay_days = int(shipment["delay_days"])
        status = shipment["status"]
        if status not in RISK_STATUSES and delay_days <= 0:
            continue

        fallback_description = (
            f"{shipment['risk_type']} risk detected for shipment "
            f"{shipment['shipment_id']} with {delay_days} delayed days."
        )
        description, detected_at = _matching_risk_description(
            shipment["shipment_id"],
            fallback_description,
        )

        events.append(
            SupplierRiskEvent(
                event_id=f"MON-{shipment['shipment_id']}",
                supplier_id=shipment["supplier_id"],
                material_id=shipment["material_id"],
                shipment_id=shipment["shipment_id"],
                risk_type=shipment["risk_type"],
                severity=shipment["severity"],
                description=description,
                delay_days=delay_days,
                location=shipment["origin"],
                detected_at=detected_at or shipment["last_updated"],
            )
        )

    return [asdict(event) for event in events]


def summarize_risk_events(events: list[dict[str, Any]]) -> dict[str, Any]:
    severity_order = {"none": 0, "low": 1, "medium": 2, "high": 3}
    highest_severity = "none"

    for event in events:
        if severity_order[event["severity"]] > severity_order[highest_severity]:
            highest_severity = event["severity"]

    return {
        "risk_detected": bool(events),
        "risk_count": len(events),
        "highest_severity": highest_severity,
        "affected_suppliers": sorted({event["supplier_id"] for event in events}),
        "affected_materials": sorted({event["material_id"] for event in events}),
    }
