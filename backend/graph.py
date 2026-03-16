import json
import sqlite3
from datetime import datetime, timedelta
from typing import Any, Optional, TypedDict

from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph
from langgraph.types import interrupt

from agents.brief_parser import parse_brief
from agents.content_gen import generate_content
from agents.monitor import compute_metrics
from agents.segmentation import segment_customers
from agents.strategy import generate_strategy
from database import AgentEvent, Campaign, IterationHistory, SessionLocal
from tools.dynamic_tools import get_tools, load_openapi_spec


class CampaignState(TypedDict):
    brief: str
    parsed_brief: Optional[dict]
    customers: Optional[list]
    segments: Optional[dict]
    strategy_text: Optional[str]
    content_a: Optional[dict]
    content_b: Optional[dict]
    hitl_decision: Optional[str]
    feedback: Optional[str]
    campaign_ids: Optional[list]
    scheduled_time: Optional[str]
    metrics: Optional[dict]
    iteration: int
    status: str


def _json_dump(payload: Any) -> str:
    return json.dumps(payload) if payload is not None else "{}"


def _normalize_rate(value: Any) -> float:
    try:
        rate = float(value or 0)
    except (TypeError, ValueError):
        return 0.0
    return rate / 100 if rate > 1 else rate


def _get_first_numeric_value(report: dict, keys: tuple[str, ...]) -> Optional[float]:
    normalized = {str(key).lower(): value for key, value in report.items()}
    for key in keys:
        if key in normalized:
            try:
                return float(normalized[key])
            except (TypeError, ValueError):
                continue
    return None


def _extract_flag_count(report: dict, flag: str) -> int:
    normalized = {str(key).lower(): value for key, value in report.items()}
    direct_keys = {
        "EO": ("eo_y_count", "total_eo", "opened_count", "email_opened_count", "open_count"),
        "EC": ("ec_y_count", "total_ec", "clicked_count", "email_clicked_count", "click_count"),
    }
    for key in direct_keys[flag]:
        value = normalized.get(key)
        if value is None:
            continue
        try:
            return int(value)
        except (TypeError, ValueError):
            continue

    for collection_key in ("results", "records", "customers", "items", "data", "report"):
        items = report.get(collection_key)
        if not isinstance(items, list):
            continue
        count = 0
        for item in items:
            if not isinstance(item, dict):
                continue
            if flag == "EO":
                opened = item.get("EO", item.get("eo", item.get("email_opened")))
                if str(opened).upper() == "Y":
                    count += 1
            if flag == "EC":
                clicked = item.get("EC", item.get("ec", item.get("email_clicked")))
                if str(clicked).upper() == "Y":
                    count += 1
        if count:
            return count

    return 0


def _normalize_campaign_report(
    report: Any,
    campaign_id: str,
    variant: str,
    audience_size: int,
) -> dict:
    if not isinstance(report, dict):
        report = {}

    open_rate = _get_first_numeric_value(
        report,
        ("open_rate", "openrate", "eo_rate", "email_open_rate"),
    )
    click_rate = _get_first_numeric_value(
        report,
        ("click_rate", "clickrate", "ec_rate", "email_click_rate"),
    )
    open_rate = _normalize_rate(open_rate)
    click_rate = _normalize_rate(click_rate)

    eo_count = _extract_flag_count(report, "EO")
    ec_count = _extract_flag_count(report, "EC")

    if not eo_count and audience_size and open_rate:
        eo_count = round(open_rate * audience_size)
    if not ec_count and audience_size and click_rate:
        ec_count = round(click_rate * audience_size)

    return {
        "campaign_id": str(campaign_id),
        "variant": variant,
        "open_rate": open_rate,
        "click_rate": click_rate,
        "eo_count": eo_count,
        "ec_count": ec_count,
        "audience_size": audience_size,
        "raw_report": report,
    }


def _extract_campaign_id(result: dict) -> Optional[str]:
    for key in ("campaign_id", "campaignId", "id"):
        value = result.get(key)
        if value:
            return str(value)
    return None


def _build_optimization_feedback(winner_report: dict, loser_report: dict) -> str:
    return (
        f"Previous run results: Variant {loser_report['variant']} underperformed. "
        f"It achieved open rate {loser_report['open_rate']:.2%}, click rate "
        f"{loser_report['click_rate']:.2%}, EO count {loser_report['eo_count']}, and EC count "
        f"{loser_report['ec_count']}. Variant {winner_report['variant']} performed better with "
        f"open rate {winner_report['open_rate']:.2%} and click rate {winner_report['click_rate']:.2%}. "
        "Regenerate the losing variant with a stronger subject line, clearer CTA, and tighter value proposition."
    )


def log_agent_event(config: RunnableConfig, agent_name: str, event_type: str, details: str):
    thread_id = config.get("configurable", {}).get("thread_id")
    if not thread_id:
        return

    db = SessionLocal()
    try:
        campaign = db.query(Campaign).filter(Campaign.thread_id == thread_id).first()
        if campaign:
            campaign.updated_at = datetime.utcnow()
            db.add(
                AgentEvent(
                    campaign_id=campaign.id,
                    agent_name=agent_name,
                    event_type=event_type,
                    details=details,
                )
            )
            db.commit()
    finally:
        db.close()


def _record_iteration_history(
    config: RunnableConfig,
    state: CampaignState,
    iteration_number: int,
    winner: Optional[str],
    action_taken: str,
):
    thread_id = config.get("configurable", {}).get("thread_id")
    if not thread_id:
        return

    metrics = state.get("metrics") or {}
    campaigns = metrics.get("campaigns") or []
    if not campaigns:
        return

    db = SessionLocal()
    try:
        campaign = db.query(Campaign).filter(Campaign.thread_id == thread_id).first()
        if not campaign:
            return

        for report in campaigns:
            variant = report.get("variant")
            content = state.get("content_a") if variant == "A" else state.get("content_b")
            db.add(
                IterationHistory(
                    campaign_id=campaign.id,
                    iteration_number=iteration_number,
                    variant_name=variant,
                    content_subject=(content or {}).get("subject"),
                    content_body=(content or {}).get("body"),
                    open_rate=report.get("open_rate"),
                    click_rate=report.get("click_rate"),
                    score=report.get("score"),
                    winner=winner,
                    action_taken=action_taken,
                    total_eo=report.get("eo_count"),
                    total_ec=report.get("ec_count"),
                    campaign_external_id=report.get("campaign_id"),
                    metrics_snapshot=_json_dump(report),
                )
            )

        campaign.updated_at = datetime.utcnow()
        db.commit()
    finally:
        db.close()


def node_parse_brief(state: CampaignState, config: RunnableConfig) -> dict:
    parsed = parse_brief(state["brief"])
    log_agent_event(config, "Brief Parser", "complete", "Parsed product, USP, offer, CTA, and tone.")
    return {"parsed_brief": parsed, "status": "brief_parsed"}


def node_fetch_customers(state: CampaignState, config: RunnableConfig) -> dict:
    """Fetch customers using dynamically discovered API tool."""
    tools = get_tools()
    get_customer_cohort_tool = tools.get("get_customer_cohort")
    
    if not get_customer_cohort_tool:
        log_agent_event(
            config,
            "Customer Fetcher",
            "error",
            "get_customer_cohort tool not available in dynamic API discovery.",
        )
        raise RuntimeError("get_customer_cohort tool not available.")
    
    customers = get_customer_cohort_tool.invoke({})
    if isinstance(customers, dict):
        customers = customers.get("customers") or customers.get("data") or []
    if not customers:
        log_agent_event(
            config,
            "Customer Fetcher",
            "error",
            "CampaignX get_customer_cohort returned no customers.",
        )
        raise RuntimeError("CampaignX get_customer_cohort returned no customers.")

    log_agent_event(
        config,
        "Customer Fetcher",
        "complete",
        f"Fetched {len(customers)} customers from CampaignX API (dynamically discovered).",
    )
    return {"customers": customers, "status": "customers_fetched"}


def node_segment(state: CampaignState, config: RunnableConfig) -> dict:
    segments = segment_customers(state["customers"], state["parsed_brief"])
    log_agent_event(
        config,
        "Segmentation Agent",
        "complete",
        f"Created two segments covering {segments.get('total', 0)} customers.",
    )
    return {"segments": segments, "status": "segmented"}


def node_strategy(state: CampaignState, config: RunnableConfig) -> dict:
    strategy_text = generate_strategy(state["parsed_brief"])
    log_agent_event(config, "Strategy Planner", "complete", "Generated targeting and A/B strategy.")
    return {"strategy_text": strategy_text, "status": "strategy_planned"}


def node_generate_content(state: CampaignState, config: RunnableConfig) -> dict:
    feedback = state.get("feedback")
    content_a = generate_content(state["parsed_brief"], "A", feedback)
    content_b = generate_content(state["parsed_brief"], "B", feedback)
    log_agent_event(config, "Content Generator", "complete", "Generated both email variants.")
    return {
        "content_a": content_a,
        "content_b": content_b,
        "feedback": None,
        "hitl_decision": None,
        "status": "content_ready",
    }


def node_hitl_approval(state: CampaignState, config: RunnableConfig) -> dict:
    log_agent_event(config, "HITL Node", "wait", "Execution paused for human approval.")
    resume_data = interrupt(
        {
            "message": "Campaign ready for approval",
            "content_a": state["content_a"],
            "content_b": state["content_b"],
            "segments": state["segments"],
            "scheduled_time": (datetime.utcnow() + timedelta(hours=1)).isoformat(),
        }
    )

    if isinstance(resume_data, dict):
        decision = resume_data.get("decision", "rejected")
        feedback = resume_data.get("feedback")
    else:
        decision = resume_data
        feedback = None

    return {"hitl_decision": decision, "feedback": feedback, "status": f"hitl_{decision}"}


def node_schedule(state: CampaignState, config: RunnableConfig) -> dict:
    """Schedule campaigns using dynamically discovered API tool."""
    tools = get_tools()
    schedule_campaign_tool = tools.get("schedule_campaign")
    
    if not schedule_campaign_tool:
        log_agent_event(
            config,
            "Scheduler",
            "error",
            "schedule_campaign tool not available in dynamic API discovery.",
        )
        raise RuntimeError("schedule_campaign tool not available.")
    
    segments = state.get("segments") or {}
    scheduled_time = (datetime.utcnow() + timedelta(hours=1)).isoformat()
    campaign_ids = []

    variant_payloads = [
        ("A", segments.get("segment_a", []), state.get("content_a")),
        ("B", segments.get("segment_b", []), state.get("content_b")),
    ]

    for variant, customer_ids, content in variant_payloads:
        result = schedule_campaign_tool.invoke(
            {
                "customer_ids": customer_ids,
                "subject": (content or {}).get("subject", ""),
                "body": (content or {}).get("body", ""),
                "scheduled_time": scheduled_time,
            }
        )
        campaign_id = _extract_campaign_id(result if isinstance(result, dict) else {})
        if not campaign_id:
            error_message = (
                result.get("error", "CampaignX schedule API did not return a campaign_id.")
                if isinstance(result, dict)
                else "CampaignX schedule API returned an invalid response."
            )
            log_agent_event(config, "Scheduler", "error", error_message)
            raise RuntimeError(error_message)
        campaign_ids.append(campaign_id)

    log_agent_event(
        config,
        "Scheduler",
        "complete",
        f"Scheduled campaigns {', '.join(campaign_ids)} through CampaignX API (dynamically discovered).",
    )
    return {"campaign_ids": campaign_ids, "scheduled_time": scheduled_time, "status": "scheduled"}


def node_monitor(state: CampaignState, config: RunnableConfig) -> dict:
    """Monitor campaigns using dynamically discovered API tool."""
    tools = get_tools()
    get_campaign_report_tool = tools.get("get_campaign_report")
    
    if not get_campaign_report_tool:
        log_agent_event(
            config,
            "Monitor",
            "error",
            "get_campaign_report tool not available in dynamic API discovery.",
        )
        raise RuntimeError("get_campaign_report tool not available.")
    
    campaign_ids = state.get("campaign_ids") or []
    segments = state.get("segments") or {}
    if not campaign_ids:
        log_agent_event(config, "Monitor", "error", "No campaign IDs were available for reporting.")
        raise RuntimeError("No CampaignX campaign IDs were available for reporting.")

    audience_sizes = {
        "A": len(segments.get("segment_a", [])),
        "B": len(segments.get("segment_b", [])),
    }
    reports = []

    for index, campaign_id in enumerate(campaign_ids):
        variant = "A" if index == 0 else "B"
        report = get_campaign_report_tool.invoke({"campaign_id": campaign_id})
        reports.append(
            _normalize_campaign_report(report, campaign_id, variant, audience_sizes.get(variant, 0))
        )

    metrics = compute_metrics(reports)
    log_agent_event(
        config,
        "Monitor",
        "complete",
        f"Collected report data via dynamically discovered API. Total EO={metrics.get('total_eo', 0)}, EC={metrics.get('total_ec', 0)}.",
    )
    return {"metrics": metrics, "status": "monitored"}


def node_optimize(state: CampaignState, config: RunnableConfig) -> dict:
    iteration = state.get("iteration", 0) + 1
    metrics = state.get("metrics") or {}
    campaigns = metrics.get("campaigns") or []

    if not campaigns:
        log_agent_event(config, "Optimizer", "complete", "No report data available; ending optimization.")
        return {"iteration": iteration, "status": "done"}

    ranked_campaigns = sorted(campaigns, key=lambda report: report.get("score", 0), reverse=True)
    winner_report = ranked_campaigns[0]
    loser_report = ranked_campaigns[-1]
    winner = winner_report.get("variant")

    if iteration >= 3 or len(ranked_campaigns) < 2:
        action_taken = "Reached final optimization iteration."
        _record_iteration_history(config, state, iteration, winner, action_taken)
        log_agent_event(config, "Optimizer", "complete", action_taken)
        return {"iteration": iteration, "status": "done"}

    action_taken = (
        f"Variant {winner_report['variant']} led with score {winner_report['score']:.3f}. "
        f"Regenerating Variant {loser_report['variant']}."
    )
    _record_iteration_history(config, state, iteration, winner, action_taken)

    feedback = _build_optimization_feedback(winner_report, loser_report)
    if loser_report["variant"] == "A":
        new_content = generate_content(state["parsed_brief"], "A", feedback)
        log_agent_event(config, "Optimizer", "complete", "Refined Variant A from report insights.")
        return {"content_a": new_content, "iteration": iteration, "status": "optimizing"}

    new_content = generate_content(state["parsed_brief"], "B", feedback)
    log_agent_event(config, "Optimizer", "complete", "Refined Variant B from report insights.")
    return {"content_b": new_content, "iteration": iteration, "status": "optimizing"}


def should_continue(state: CampaignState) -> str:
    if state.get("hitl_decision") == "rejected":
        return "generate_content"
    return "schedule"


def should_optimize(state: CampaignState) -> str:
    if state.get("status") == "optimizing":
        return "schedule"
    return END


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
        {"schedule": "schedule", END: END},
    )

    try:
        # Try to use SqliteSaver if available, otherwise fall back to MemorySaver
        try:
            from langgraph.checkpoint.sqlite import SqliteSaver
            conn = sqlite3.connect("campaignx_checkpoints.sqlite", check_same_thread=False)
            checkpointer = SqliteSaver(conn)
            checkpointer.setup()
            print("✓ Using SqliteSaver for checkpoints")
        except (ImportError, ModuleNotFoundError):
            # SqliteSaver not available in this langgraph version, use MemorySaver
            checkpointer = MemorySaver()
            print("⚠ SqliteSaver not available, using MemorySaver for checkpoints")
    except Exception as e:
        # Final fallback
        print(f"⚠ Error initializing checkpointer: {e}, using MemorySaver")
        checkpointer = MemorySaver()

    return graph.compile(checkpointer=checkpointer)


campaign_graph = build_graph()
