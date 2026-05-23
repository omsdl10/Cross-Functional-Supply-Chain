from __future__ import annotations

from typing import Any, TypedDict

from langgraph.graph import END, StateGraph

from app.agents.impact import assess_risk_events_impact, summarize_impact_assessments
from app.agents.monitor import poll_logistics_risk_feed, summarize_risk_events
from app.agents.strategy import generate_strategy_plan, summarize_strategy_plan


class StrategyState(TypedDict, total=False):
    risk_events: list[dict[str, Any]]
    monitor_summary: dict[str, Any]
    impact_assessments: list[dict[str, Any]]
    impact_summary: dict[str, Any]
    strategy_plan: list[dict[str, Any]]
    strategy_summary: dict[str, Any]


def monitor_node(state: StrategyState) -> StrategyState:
    risk_events = state.get("risk_events") or poll_logistics_risk_feed()
    return {
        **state,
        "risk_events": risk_events,
        "monitor_summary": summarize_risk_events(risk_events),
    }


def impact_assessment_node(state: StrategyState) -> StrategyState:
    assessments = assess_risk_events_impact(state.get("risk_events", []))
    return {
        **state,
        "impact_assessments": assessments,
        "impact_summary": summarize_impact_assessments(assessments),
    }


def strategy_node(state: StrategyState) -> StrategyState:
    strategy_plan = generate_strategy_plan(state.get("impact_assessments", []))
    return {
        **state,
        "strategy_plan": strategy_plan,
        "strategy_summary": summarize_strategy_plan(strategy_plan),
    }


def build_strategy_workflow():
    workflow = StateGraph(StrategyState)
    workflow.add_node("monitor", monitor_node)
    workflow.add_node("impact_assessment", impact_assessment_node)
    workflow.add_node("strategy", strategy_node)
    workflow.set_entry_point("monitor")
    workflow.add_edge("monitor", "impact_assessment")
    workflow.add_edge("impact_assessment", "strategy")
    workflow.add_edge("strategy", END)
    return workflow.compile()


def run_strategy_workflow(
    risk_events: list[dict[str, Any]] | None = None,
) -> StrategyState:
    workflow = build_strategy_workflow()
    initial_state: StrategyState = {
        "risk_events": risk_events or [],
        "monitor_summary": {},
        "impact_assessments": [],
        "impact_summary": {},
        "strategy_plan": [],
        "strategy_summary": {},
    }
    return workflow.invoke(initial_state)
