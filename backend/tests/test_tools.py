from fastapi.testclient import TestClient

from app.main import app
from app.tools.operations import (
    build_material_risk_snapshot,
    calculate_days_of_cover,
    get_alternate_suppliers,
    get_inventory_for_material,
    get_open_purchase_orders,
    get_supplier_details,
)


def test_get_supplier_details_normalizes_values() -> None:
    supplier = get_supplier_details("SUP-102")

    assert supplier is not None
    assert supplier["supplier_id"] == "SUP-102"
    assert supplier["materials"] == ["MAT-445"]
    assert supplier["standard_lead_time_days"] == 12
    assert supplier["is_primary"] is True


def test_calculate_days_of_cover() -> None:
    coverage = calculate_days_of_cover("MAT-445")

    assert coverage is not None
    assert coverage["current_stock"] == 1200
    assert coverage["daily_usage"] == 300
    assert coverage["days_of_cover"] == 4.0
    assert coverage["below_reorder_point"] is False


def test_get_inventory_for_material_includes_material_details() -> None:
    inventory = get_inventory_for_material("MAT-445")

    assert inventory is not None
    assert inventory["material"]["name"] == "Lithium Battery Cells"
    assert inventory["material"]["criticality"] == "high"


def test_get_open_purchase_orders_filters_by_material() -> None:
    orders = get_open_purchase_orders(material_id="MAT-445")

    assert len(orders) == 1
    assert orders[0]["po_id"] == "PO-9001"
    assert orders[0]["quantity"] == 3000
    assert orders[0]["unit_cost"] == 42.5


def test_get_alternate_suppliers_for_material() -> None:
    suppliers = get_alternate_suppliers("MAT-445")

    assert len(suppliers) == 1
    assert suppliers[0]["supplier_id"] == "SUP-207"
    assert suppliers[0]["is_primary"] is False


def test_build_material_risk_snapshot() -> None:
    snapshot = build_material_risk_snapshot("MAT-445")

    assert snapshot is not None
    assert snapshot["inventory"]["days_of_cover"] == 4.0
    assert snapshot["primary_suppliers"][0]["supplier_id"] == "SUP-102"
    assert snapshot["alternate_suppliers"][0]["supplier_id"] == "SUP-207"
    assert snapshot["active_risk_events"][0]["event_id"] == "RISK-1001"


def test_operational_tools_api() -> None:
    client = TestClient(app)

    response = client.get("/tools/materials/MAT-445/risk-snapshot")

    assert response.status_code == 200
    body = response.json()
    assert body["material"]["material_id"] == "MAT-445"
    assert body["inventory"]["days_of_cover"] == 4.0
    assert body["alternate_suppliers"][0]["supplier_id"] == "SUP-207"
