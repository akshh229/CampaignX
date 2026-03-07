from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt
from typing import TypedDict, Optional
from datetime import datetime, timedelta

from agents.brief_parser import parse_brief
from agents.segmentation import segment_customers
from agents.strategy import generate_strategy
from agents.content_gen import generate_content
from agents.monitor import compute_metrics
from tools.api_tools import get_customer_cohort, schedule_campaign, get_campaign_report


class CampaignState(TypedDict):
    brief: str
    parsed_brief: Optional[dict]
    customers: Optional[list]
    segments: Optional[dict]
    strategy_text: Optional[str]
    content_a: Optional[dict]
    content_b: Optional[dict]
    hitl_decision: Optional[str]
    campaign_ids: Optional[list]
    metrics: Optional[dict]
    iteration: int
    status: str


def node_parse_brief(state: CampaignState) -> dict:
    parsed = parse_brief(state["brief"])
    return {"parsed_brief": parsed, "status": "brief_parsed"}


def node_fetch_customers(state: CampaignState) -> dict:
    customers = get_customer_cohort.invoke({})
    if not customers:
        # Fallback mock data when API is unavailable
        customers = [
            {"customer_id": f"CUST_{i:04d}", "status": "active"}
            for i in range(1, 51)
        ]
    return {"customers": customers, "status": "customers_fetched"}


def node_segment(state: CampaignState) -> dict:
    segments = segment_customers(state["customers"], state["parsed_brief"])
    return {"segments": segments, "status": "segmented"}


def node_strategy(state: CampaignState) -> dict:
    strategy_text = generate_strategy(state["parsed_brief"])
    return {"strategy_text": strategy_text, "status": "strategy_planned"}


def node_generate_content(state: CampaignState) -> dict:
    content_a = generate_content(state["parsed_brief"], "A")
    content_b = generate_content(state["parsed_brief"], "B")
    return {"content_a": content_a, "content_b": content_b, "status": "content_ready"}


def node_hitl_approval(state: CampaignState) -> dict:
    """Pause for human approval via LangGraph interrupt."""
    decision = interrupt({
        "message": "Campaign ready for approval",
        "content_a": state["content_a"],
        "content_b": state["content_b"],
        "segments": state["segments"],
        "scheduled_time": (datetime.utcnow() + timedelta(hours=1)).isoformat(),
    })
    return {"hitl_decision": decision, "status": f"hitl_{decision}"}


def node_schedule(state: CampaignState) -> dict:
    scheduled_time = (datetime.utcnow() + timedelta(hours=1)).isoformat()
    campaign_ids = []

    result_a = schedule_campaign.invoke({
        "customer_ids": state["segments"]["segment_a"],
        "subject": state["content_a"]["subject"],
        "body": state["content_a"]["body"],
        "scheduled_time": scheduled_time,
    })
    if "campaign_id" in result_a:
        campaign_ids.append(result_a["campaign_id"])

    result_b = schedule_campaign.invoke({
        "customer_ids": state["segments"]["segment_b"],
        "subject": state["content_b"]["subject"],
        "body": state["content_b"]["body"],
        "scheduled_time": scheduled_time,
    })
    if "campaign_id" in result_b:
        campaign_ids.append(result_b["campaign_id"])

    return {"campaign_ids": campaign_ids, "status": "scheduled"}


def node_monitor(state: CampaignState) -> dict:
    reports = []
    for cid in (state.get("campaign_ids") or []):
        report = get_campaign_report.invoke({"campaign_id": cid})
        reports.append({"campaign_id": cid, **report})
    metrics = compute_metrics(reports)
    return {"metrics": metrics, "status": "monitored"}


def node_optimize(state: CampaignState) -> dict:
    iteration = state.get("iteration", 0) + 1
    if iteration >= 3:
        return {"iteration": iteration, "status": "done"}

    campaigns = state.get("metrics", {}).get("campaigns", [])
    if len(campaigns) >= 2:
        if campaigns[0].get("click_rate", 0) > campaigns[1].get("click_rate", 0):
            new_content = generate_content(state["parsed_brief"], "B")
            return {"content_b": new_content, "iteration": iteration, "status": "optimizing"}
        else:
            new_content = generate_content(state["parsed_brief"], "A")
            return {"content_a": new_content, "iteration": iteration, "status": "optimizing"}

    return {"iteration": iteration, "status": "done"}


def should_continue(state: CampaignState) -> str:
    if state.get("hitl_decision") == "rejected":
        return "generate_content"
    return "schedule"


def should_optimize(state: CampaignState) -> str:
    if state.get("status") == "done":
        return END
    return "segment"


# Build graph
def build_graph():
    graph = StateGraph(CampaignState)
    graph.add_node("parse_brief", node_parse_brief)
    graph.add_node("fetch_customers", node_fetch_customers)
    graph.add_node("segment", node_segment)
    graph.add_node("strategy", node_strategy)
    graph.add_node("generate_content", node_generate_content)
    graph.add_node("hitl_approval", node_hitl_approval)
    graph.add_node("schedule", node_schedule)
    graph.add_node("monitor", node_monitor)
    graph.add_node("optimize", node_optimize)

    graph.set_entry_point("parse_brief")
    graph.add_edge("parse_brief", "fetch_customers")
    graph.add_edge("fetch_customers", "segment")
    graph.add_edge("segment", "strategy")
    graph.add_edge("strategy", "generate_content")
    graph.add_edge("generate_content", "hitl_approval")
    graph.add_conditional_edges(
        "hitl_approval",
        should_continue,
        {"generate_content": "generate_content", "schedule": "schedule"},
    )
    graph.add_edge("schedule", "monitor")
    graph.add_edge("monitor", "optimize")
    graph.add_conditional_edges(
        "optimize",
        should_optimize,
        {"segment": "segment", END: END},
    )

    checkpointer = MemorySaver()
    return graph.compile(checkpointer=checkpointer)


campaign_graph = build_graph()
