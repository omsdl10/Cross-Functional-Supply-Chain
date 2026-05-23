from fastapi import APIRouter, HTTPException

from app.tools.operations import (
    build_material_risk_snapshot,
    get_alternate_suppliers,
    get_inventory_for_material,
    get_open_purchase_orders,
    get_supplier_details,
)


router = APIRouter(prefix="/tools", tags=["operational tools"])


@router.get("/suppliers/{supplier_id}")
def supplier_details(supplier_id: str) -> dict[str, object]:
    supplier = get_supplier_details(supplier_id)
    if supplier is None:
        raise HTTPException(status_code=404, detail="Supplier not found")

    return supplier


@router.get("/materials/{material_id}/inventory")
def material_inventory(material_id: str) -> dict[str, object]:
    inventory = get_inventory_for_material(material_id)
    if inventory is None:
        raise HTTPException(status_code=404, detail="Material inventory not found")

    return inventory


@router.get("/materials/{material_id}/purchase-orders")
def material_purchase_orders(material_id: str) -> list[dict[str, object]]:
    return get_open_purchase_orders(material_id=material_id)


@router.get("/materials/{material_id}/alternate-suppliers")
def material_alternate_suppliers(material_id: str) -> list[dict[str, object]]:
    return get_alternate_suppliers(material_id)


@router.get("/materials/{material_id}/risk-snapshot")
def material_risk_snapshot(material_id: str) -> dict[str, object]:
    snapshot = build_material_risk_snapshot(material_id)
    if snapshot is None:
        raise HTTPException(status_code=404, detail="Material not found")

    return snapshot
