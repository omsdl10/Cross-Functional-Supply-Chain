from __future__ import annotations

from typing import Any, TypedDict

from langgraph.graph import END, StateGraph

from app.agents.monitor import poll_logistics_risk_feed, summarize_risk_events


class MonitorState(TypedDict, total=False):
    risk_events: list[dict[str, Any]]
    summary: dict[str, Any]


def monitor_node(state: MonitorState) -> MonitorState:
    risk_events = poll_logistics_risk_feed()
    return {
        **state,
        "risk_events": risk_events,
        "summary": summarize_risk_events(risk_events),
    }


def build_monitor_workflow():
    workflow = StateGraph(MonitorState)
    workflow.add_node("monitor", monitor_node)
    workflow.set_entry_point("monitor")
    workflow.add_edge("monitor", END)
    return workflow.compile()


def run_monitor_workflow() -> MonitorState:
    workflow = build_monitor_workflow()
    return workflow.invoke({"risk_events": [], "summary": {}})
