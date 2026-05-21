from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATA_ROOT = PROJECT_ROOT / "data"


@dataclass(frozen=True)
class MockSupplyChainData:
    suppliers: list[dict[str, Any]]
    materials: list[dict[str, Any]]
    inventory: list[dict[str, Any]]
    purchase_orders: list[dict[str, Any]]
    shipments: list[dict[str, Any]]
    risk_events: list[dict[str, Any]]
    supplier_contracts: list[dict[str, Any]]


def load_csv(path: Path) -> list[dict[str, Any]]:
    with path.open(newline="", encoding="utf-8") as file:
        return [dict(row) for row in csv.DictReader(file)]


def load_json(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, list):
        raise ValueError(f"Expected a list in {path}")

    return data


def load_mock_supply_chain_data(data_root: Path = DATA_ROOT) -> MockSupplyChainData:
    return MockSupplyChainData(
        suppliers=load_csv(data_root / "sample_inventory" / "suppliers.csv"),
        materials=load_csv(data_root / "sample_inventory" / "materials.csv"),
        inventory=load_csv(data_root / "sample_inventory" / "inventory.csv"),
        purchase_orders=load_json(data_root / "sample_inventory" / "purchase_orders.json"),
        shipments=load_json(data_root / "sample_logistics" / "shipments.json"),
        risk_events=load_json(data_root / "sample_logistics" / "risk_events.json"),
        supplier_contracts=load_json(
            data_root / "sample_contracts" / "supplier_contract_summaries.json"
        ),
    )


def get_inventory_record(material_id: str) -> dict[str, Any] | None:
    data = load_mock_supply_chain_data()
    return next(
        (record for record in data.inventory if record["material_id"] == material_id),
        None,
    )


def get_open_purchase_orders(material_id: str) -> list[dict[str, Any]]:
    data = load_mock_supply_chain_data()
    return [
        order
        for order in data.purchase_orders
        if order["material_id"] == material_id
        and order["status"] in {"confirmed", "in_transit"}
    ]
