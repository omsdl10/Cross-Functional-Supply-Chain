from __future__ import annotations

from typing import Any

from app.tools.operations import (
    build_material_risk_snapshot,
    get_alternate_suppliers,
    get_open_purchase_orders,
)


RISK_SCORE = {"low": 1, "medium": 2, "high": 3, "unknown": 0}


def _strategy_score(
    production_risk: str,
    execution_days: int,
    cost_impact_percent: float,
    residual_risk: str,
) -> float:
    urgency = RISK_SCORE.get(production_risk, 0) * 10
    residual_penalty = RISK_SCORE.get(residual_risk, 0) * 4
    return round(urgency - execution_days - cost_impact_percent - residual_penalty, 2)


def _supplier_switch_strategy(assessment: dict[str, Any]) -> dict[str, Any] | None:
    alternate_suppliers = get_alternate_suppliers(assessment["material_id"])
    if not alternate_suppliers:
        return None

    supplier = sorted(
        alternate_suppliers,
        key=lambda item: (item["standard_lead_time_days"], item["risk_rating"]),
    )[0]
    execution_days = supplier["standard_lead_time_days"]
    residual_risk = "medium" if execution_days > assessment["days_of_cover"] else "low"
    cost_impact_percent = 8.0

    return {
        "strategy_id": f"switch-supplier-{supplier['supplier_id']}",
        "name": "Switch to secondary supplier",
        "action": (
            f"Activate secondary supplier {supplier['supplier_id']} for "
            f"{assessment['material_id']}."
        ),
        "supplier_id": supplier["supplier_id"],
        "estimated_cost_impact_percent": cost_impact_percent,
        "execution_days": execution_days,
        "residual_risk": residual_risk,
        "score": _strategy_score(
            assessment["production_risk"],
            execution_days,
            cost_impact_percent,
            residual_risk,
        )
        + 10,
    }


def _buffer_stock_strategy(assessment: dict[str, Any]) -> dict[str, Any]:
    stockout_gap = max(float(assessment["projected_stockout_gap_days"]), 0.0)
    execution_days = 1
    cost_impact_percent = 3.0 if stockout_gap <= 2 else 6.0
    residual_risk = "high" if stockout_gap > 2 else "low"

    return {
        "strategy_id": "buffer-existing-stock",
        "name": "Buffer existing stock",
        "action": (
            f"Reserve available {assessment['material_id']} stock for critical production "
            "and pause non-critical consumption."
        ),
        "supplier_id": assessment["supplier_id"],
        "estimated_cost_impact_percent": cost_impact_percent,
        "execution_days": execution_days,
        "residual_risk": residual_risk,
        "score": _strategy_score(
            assessment["production_risk"],
            execution_days,
            cost_impact_percent,
            residual_risk,
        ),
    }


def _delay_production_strategy(assessment: dict[str, Any]) -> dict[str, Any]:
    stockout_gap = max(float(assessment["projected_stockout_gap_days"]), 0.0)
    execution_days = 2
    cost_impact_percent = 12.0 if stockout_gap > 0 else 4.0
    residual_risk = "low"

    return {
        "strategy_id": "delay-production-start",
        "name": "Delay production start",
        "action": (
            f"Delay or resequence production that consumes {assessment['material_id']} "
            f"by {int(stockout_gap) or 1} day(s)."
        ),
        "supplier_id": assessment["supplier_id"],
        "estimated_cost_impact_percent": cost_impact_percent,
        "execution_days": execution_days,
        "residual_risk": residual_risk,
        "score": _strategy_score(
            assessment["production_risk"],
            execution_days,
            cost_impact_percent,
            residual_risk,
        ),
    }


def generate_mitigation_strategies(assessment: dict[str, Any]) -> dict[str, Any]:
    strategies = [
        strategy
        for strategy in [
            _supplier_switch_strategy(assessment),
            _buffer_stock_strategy(assessment),
            _delay_production_strategy(assessment),
        ]
        if strategy is not None
    ]
    recommended = max(strategies, key=lambda strategy: strategy["score"])
    snapshot = build_material_risk_snapshot(assessment["material_id"])

    return {
        "event_id": assessment["event_id"],
        "material_id": assessment["material_id"],
        "material_name": assessment["material_name"],
        "production_risk": assessment["production_risk"],
        "strategies": strategies,
        "recommended_strategy": recommended,
        "open_purchase_orders": get_open_purchase_orders(
            material_id=assessment["material_id"]
        ),
        "inventory_context": snapshot["inventory"] if snapshot else {},
    }


def generate_strategy_plan(
    impact_assessments: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    actionable = [
        assessment
        for assessment in impact_assessments
        if assessment.get("assessment_status") == "assessed"
        and assessment.get("production_risk") in {"medium", "high"}
    ]
    return [generate_mitigation_strategies(assessment) for assessment in actionable]


def summarize_strategy_plan(strategy_plan: list[dict[str, Any]]) -> dict[str, Any]:
    if not strategy_plan:
        return {
            "strategy_count": 0,
            "recommended_actions": [],
            "materials_with_recommendations": [],
        }

    return {
        "strategy_count": sum(len(plan["strategies"]) for plan in strategy_plan),
        "recommended_actions": [
            plan["recommended_strategy"]["name"] for plan in strategy_plan
        ],
        "materials_with_recommendations": sorted(
            {plan["material_id"] for plan in strategy_plan}
        ),
    }
