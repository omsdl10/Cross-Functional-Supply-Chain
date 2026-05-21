from app.db.mock_data import (
    get_inventory_record,
    get_open_purchase_orders,
    load_mock_supply_chain_data,
)


def test_load_mock_supply_chain_data() -> None:
    data = load_mock_supply_chain_data()

    assert len(data.suppliers) == 5
    assert len(data.materials) == 4
    assert len(data.inventory) == 4
    assert len(data.purchase_orders) == 4
    assert len(data.shipments) == 3
    assert len(data.risk_events) == 2
    assert len(data.supplier_contracts) == 2


def test_sample_delay_matches_critical_material() -> None:
    data = load_mock_supply_chain_data()

    high_risk_event = next(event for event in data.risk_events if event["event_id"] == "RISK-1001")
    material = next(
        material
        for material in data.materials
        if material["material_id"] == high_risk_event["material_id"]
    )

    assert high_risk_event["supplier_id"] == "SUP-102"
    assert high_risk_event["severity"] == "high"
    assert material["criticality"] == "high"


def test_get_inventory_record_for_lithium_cells() -> None:
    inventory = get_inventory_record("MAT-445")

    assert inventory is not None
    assert inventory["current_stock"] == "1200"
    assert inventory["daily_usage"] == "300"


def test_get_open_purchase_orders_for_material() -> None:
    purchase_orders = get_open_purchase_orders("MAT-445")

    assert len(purchase_orders) == 1
    assert purchase_orders[0]["po_id"] == "PO-9001"
