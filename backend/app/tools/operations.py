from __future__ import annotations

from typing import Any

from app.db.mock_data import load_mock_supply_chain_data


OPEN_ORDER_STATUSES = {"confirmed", "in_transit"}


def _to_bool(value: str) -> bool:
    return value.strip().lower() == "true"


def _to_float(value: str | int | float) -> float:
    return float(value)


def _to_int(value: str | int) -> int:
    return int(value)


def _material_ids(value: str) -> list[str]:
    return [material_id.strip() for material_id in value.split(",") if material_id.strip()]


def get_supplier_details(supplier_id: str) -> dict[str, Any] | None:
    data = load_mock_supply_chain_data()

    supplier = next(
        (record for record in data.suppliers if record["supplier_id"] == supplier_id),
        None,
    )
    if supplier is None:
        return None

    return {
        **supplier,
        "materials": _material_ids(supplier["materials"]),
        "standard_lead_time_days": _to_int(supplier["standard_lead_time_days"]),
        "is_primary": _to_bool(supplier["is_primary"]),
    }


def get_material_details(material_id: str) -> dict[str, Any] | None:
    data = load_mock_supply_chain_data()
    return next(
        (record for record in data.materials if record["material_id"] == material_id),
        None,
    )


def calculate_days_of_cover(material_id: str) -> dict[str, Any] | None:
    data = load_mock_supply_chain_data()
    inventory = next(
        (record for record in data.inventory if record["material_id"] == material_id),
        None,
    )
    if inventory is None:
        return None

    current_stock = _to_float(inventory["current_stock"])
    daily_usage = _to_float(inventory["daily_usage"])
    days_of_cover = current_stock / daily_usage if daily_usage else 0.0

    return {
        "material_id": material_id,
        "current_stock": _to_int(inventory["current_stock"]),
        "daily_usage": _to_int(inventory["daily_usage"]),
        "days_of_cover": round(days_of_cover, 2),
        "reorder_point": _to_int(inventory["reorder_point"]),
        "safety_stock": _to_int(inventory["safety_stock"]),
        "next_required_date": inventory["next_required_date"],
        "below_reorder_point": current_stock <= _to_float(inventory["reorder_point"]),
        "below_safety_stock": current_stock <= _to_float(inventory["safety_stock"]),
    }


def get_inventory_for_material(material_id: str) -> dict[str, Any] | None:
    material = get_material_details(material_id)
    coverage = calculate_days_of_cover(material_id)
    if material is None or coverage is None:
        return None

    return {
        "material": material,
        "inventory": coverage,
    }


def get_open_purchase_orders(
    material_id: str | None = None,
    supplier_id: str | None = None,
) -> list[dict[str, Any]]:
    data = load_mock_supply_chain_data()

    orders = [
        order
        for order in data.purchase_orders
        if order["status"] in OPEN_ORDER_STATUSES
    ]

    if material_id is not None:
        orders = [order for order in orders if order["material_id"] == material_id]

    if supplier_id is not None:
        orders = [order for order in orders if order["supplier_id"] == supplier_id]

    return [
        {
            **order,
            "quantity": _to_int(order["quantity"]),
            "unit_cost": _to_float(order["unit_cost"]),
        }
        for order in orders
    ]


def get_alternate_suppliers(material_id: str) -> list[dict[str, Any]]:
    data = load_mock_supply_chain_data()

    return [
        get_supplier_details(supplier["supplier_id"])
        for supplier in data.suppliers
        if material_id in _material_ids(supplier["materials"])
        and not _to_bool(supplier["is_primary"])
    ]


def get_primary_suppliers(material_id: str) -> list[dict[str, Any]]:
    data = load_mock_supply_chain_data()

    return [
        get_supplier_details(supplier["supplier_id"])
        for supplier in data.suppliers
        if material_id in _material_ids(supplier["materials"])
        and _to_bool(supplier["is_primary"])
    ]


def get_active_risk_events(material_id: str | None = None) -> list[dict[str, Any]]:
    data = load_mock_supply_chain_data()
    events = data.risk_events

    if material_id is not None:
        events = [event for event in events if event["material_id"] == material_id]

    return events


def get_shipments_for_material(material_id: str) -> list[dict[str, Any]]:
    data = load_mock_supply_chain_data()

    return [
        {
            **shipment,
            "delay_days": _to_int(shipment["delay_days"]),
        }
        for shipment in data.shipments
        if shipment["material_id"] == material_id
    ]


def build_material_risk_snapshot(material_id: str) -> dict[str, Any] | None:
    inventory = get_inventory_for_material(material_id)
    if inventory is None:
        return None

    return {
        **inventory,
        "primary_suppliers": get_primary_suppliers(material_id),
        "alternate_suppliers": get_alternate_suppliers(material_id),
        "open_purchase_orders": get_open_purchase_orders(material_id=material_id),
        "shipments": get_shipments_for_material(material_id),
        "active_risk_events": get_active_risk_events(material_id=material_id),
    }
