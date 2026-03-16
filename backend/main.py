import json
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from dotenv import load_dotenv
load_dotenv(Path(__file__).with_name(".env"), override=True)

from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from langgraph.types import Command
from sqlalchemy.orm import Session
from sqlalchemy import text
import aiohttp

from database import (
    AgentEvent,
    ApprovalHistory,
    Campaign,
    IterationHistory,
    SessionLocal,
    get_db,
    init_db,
)
from graph import CampaignState, campaign_graph, log_agent_event
from models import ApprovalRequest, BriefRequest

app = FastAPI(title="CampaignX API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()

active_threads: dict[str, dict[str, Any]] = {}
campaign_db_ids: dict[str, int] = {}


def _safe_json_dump(payload: Any) -> Optional[str]:
    if payload is None:
        return None
    return json.dumps(payload)


def _safe_json_load(payload: Optional[str], default: Any):
    if not payload:
        return default
    try:
        return json.loads(payload)
    except json.JSONDecodeError:
        return default


def _derive_status(state: Optional[dict], campaign: Optional[Campaign] = None) -> str:
    if state:
        status = state.get("status")
        if status == "content_ready" and state.get("content_a") and state.get("content_b"):
            if not state.get("campaign_ids"):
                return "awaiting_approval"
        if status:
            return status
    if campaign and campaign.status:
        return campaign.status
    return "unknown"


def _coverage_count(segments: Optional[dict]) -> Optional[int]:
    if not segments:
        return None
    audience = set(segments.get("segment_a", [])) | set(segments.get("segment_b", []))
    return len(audience)


def _build_db_state(campaign: Campaign) -> dict:
    parsed_brief = _safe_json_load(campaign.parsed_brief_json, None)
    segments = _safe_json_load(campaign.segments, None)
    campaign_ids = _safe_json_load(campaign.campaign_ids_json, None)
    metrics = _safe_json_load(campaign.metrics_json, None)

    content_a_parsed = _safe_json_load(campaign.content_a_json, None)
    content_b_parsed = _safe_json_load(campaign.content_b_json, None)

    # fallback for legacy schemas lacking content_a_json
    if content_a_parsed is None and (campaign.content_subject or campaign.content_body):
        content_a_parsed = {"subject": campaign.content_subject, "body": campaign.content_body}

    return {
        "brief": campaign.brief,
        "parsed_brief": parsed_brief,
        "customers": None,
        "segments": segments,
        "strategy_text": campaign.strategy,
        "content_a": content_a_parsed,
        "content_b": content_b_parsed,
        "hitl_decision": None,
        "feedback": None,
        "campaign_ids": campaign_ids,
        "scheduled_time": campaign.scheduled_time,
        "metrics": metrics,
        "iteration": 0,
        "status": campaign.status,
    }


def _persist_campaign_snapshot(db: Session, campaign: Campaign, state: dict):
    parsed_brief = state.get("parsed_brief")
    segments = state.get("segments")
    metrics = state.get("metrics") or {}

    campaign.parsed_brief_json = _safe_json_dump(parsed_brief)
    campaign.strategy = state.get("strategy_text") or campaign.strategy
    
    content_a_state = state.get("content_a") or {}
    content_b_state = state.get("content_b") or {}
    campaign.content_a_json = _safe_json_dump(content_a_state) if content_a_state else campaign.content_a_json
    campaign.content_b_json = _safe_json_dump(content_b_state) if content_b_state else campaign.content_b_json
    
    campaign.content_subject = content_a_state.get("subject", campaign.content_subject)
    campaign.content_body = content_a_state.get("body", campaign.content_body)
    
    campaign.segments = _safe_json_dump(segments)
    campaign.scheduled_time = state.get("scheduled_time") or campaign.scheduled_time
    campaign.campaign_ids_json = _safe_json_dump(state.get("campaign_ids"))
    campaign.metrics_json = _safe_json_dump(metrics)
    campaign.status = _derive_status(state, campaign)
    campaign.open_rate = metrics.get("avg_open_rate", campaign.open_rate)
    campaign.click_rate = metrics.get("avg_click_rate", campaign.click_rate)
    campaign.total_eo = metrics.get("total_eo", campaign.total_eo)
    campaign.total_ec = metrics.get("total_ec", campaign.total_ec)
    campaign.cohort_size = len(state.get("customers") or []) or campaign.cohort_size
    campaign.coverage_count = _coverage_count(segments) or campaign.coverage_count
    campaign.updated_at = datetime.utcnow()


def _get_or_create_config(thread_id: str) -> dict[str, Any]:
    config = active_threads.get(thread_id)
    if config:
        return config

    config = {"configurable": {"thread_id": thread_id}}
    active_threads[thread_id] = config
    return config


def run_graph_background(initial_state: CampaignState, config: dict[str, Any], campaign_id: int):
    db = SessionLocal()
    try:
        campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
        try:
            campaign_graph.invoke(initial_state, config)
        except Exception as exc:
            log_agent_event(config, "Graph Runner", "error", str(exc))
            if campaign:
                campaign.status = "failed"
                campaign.updated_at = datetime.utcnow()
                db.commit()
            return

        snapshot = campaign_graph.get_state(config)
        if campaign and snapshot:
            _persist_campaign_snapshot(db, campaign, snapshot.values)
            db.commit()
    finally:
        db.close()


def resume_graph_background(
    config: dict[str, Any],
    resume_data: dict[str, Any],
    campaign_id: int,
    decision: str,
    feedback: Optional[str],
):
    db = SessionLocal()
    try:
        campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
        if campaign:
            db.add(
                ApprovalHistory(
                    campaign_id=campaign.id,
                    reviewer_notes=feedback,
                    decision=decision,
                )
            )
            campaign.status = "processing"
            campaign.updated_at = datetime.utcnow()
            db.commit()

        try:
            campaign_graph.invoke(Command(resume=resume_data), config)
        except Exception as exc:
            log_agent_event(config, "Graph Runner", "error", str(exc))
            if campaign:
                campaign.status = "failed"
                campaign.updated_at = datetime.utcnow()
                db.commit()
            return

        snapshot = campaign_graph.get_state(config)
        if campaign and snapshot:
            _persist_campaign_snapshot(db, campaign, snapshot.values)
            db.commit()
    finally:
        db.close()


@app.post("/api/campaign/start")
async def start_campaign(
    req: BriefRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    thread_id = f"thread_{datetime.utcnow().timestamp()}"
    initial_state: CampaignState = {
        "brief": req.brief,
        "parsed_brief": None,
        "customers": None,
        "segments": None,
        "strategy_text": None,
        "content_a": None,
        "content_b": None,
        "hitl_decision": None,
        "feedback": None,
        "campaign_ids": None,
        "scheduled_time": None,
        "metrics": None,
        "iteration": 0,
        "status": "started",
    }

    config = _get_or_create_config(thread_id)
    campaign = Campaign(thread_id=thread_id, brief=req.brief, status="processing")
    db.add(campaign)
    db.commit()
    db.refresh(campaign)
    campaign_db_ids[thread_id] = campaign.id

    background_tasks.add_task(run_graph_background, initial_state, config, campaign.id)
    return {
        "thread_id": thread_id,
        "campaign_id": campaign.id,
        "state": initial_state,
        "status": "processing",
    }


@app.post("/api/campaign/approve")
async def approve_campaign(
    req: ApprovalRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    campaign = db.query(Campaign).filter(Campaign.thread_id == req.thread_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Thread not found")

    config = _get_or_create_config(req.thread_id)
    campaign_db_ids[req.thread_id] = campaign.id
    resume_data = {"decision": req.decision, "feedback": req.feedback}
    background_tasks.add_task(
        resume_graph_background,
        config,
        resume_data,
        campaign.id,
        req.decision,
        req.feedback,
    )

    return {
        "thread_id": req.thread_id,
        "campaign_id": campaign.id,
        "status": "processing",
    }


@app.get("/api/campaign/status/{thread_id}")
async def get_status(thread_id: str, db: Session = Depends(get_db)):
    campaign = db.query(Campaign).filter(Campaign.thread_id == thread_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Thread not found")

    config = active_threads.get(thread_id)
    snapshot = campaign_graph.get_state(config) if config else None
    state = snapshot.values if snapshot else _build_db_state(campaign)
    status = _derive_status(state, campaign)

    if snapshot:
        _persist_campaign_snapshot(db, campaign, state)
        db.commit()

    return {
        "thread_id": thread_id,
        "campaign_id": campaign.id,
        "state": state,
        "status": status,
    }


@app.get("/api/campaign/{campaign_id}/events")
async def get_campaign_events(campaign_id: int, db: Session = Depends(get_db)):
    events = (
        db.query(AgentEvent)
        .filter(AgentEvent.campaign_id == campaign_id)
        .order_by(AgentEvent.timestamp.asc())
        .all()
    )
    return [
        {
            "id": event.id,
            "agent_name": event.agent_name,
            "event_type": event.event_type,
            "action": event.event_type.replace("_", " ").title(),
            "details": event.details,
            "timestamp": event.timestamp.isoformat() if event.timestamp else None,
        }
        for event in events
    ]


@app.get("/api/campaign/{campaign_id}/approvals")
async def get_approval_history(campaign_id: int, db: Session = Depends(get_db)):
    approvals = (
        db.query(ApprovalHistory)
        .filter(ApprovalHistory.campaign_id == campaign_id)
        .order_by(ApprovalHistory.timestamp.asc())
        .all()
    )
    return [
        {
            "id": approval.id,
            "campaign_id": approval.campaign_id,
            "reviewer_notes": approval.reviewer_notes,
            "decision": approval.decision,
            "timestamp": approval.timestamp.isoformat() if approval.timestamp else None,
        }
        for approval in approvals
    ]


@app.get("/api/campaign/{campaign_id}/iterations")
async def get_iteration_history(campaign_id: int, db: Session = Depends(get_db)):
    iterations = (
        db.query(IterationHistory)
        .filter(IterationHistory.campaign_id == campaign_id)
        .order_by(IterationHistory.iteration_number.asc(), IterationHistory.variant_name.asc())
        .all()
    )

    grouped: dict[int, dict[str, Any]] = {}
    for row in iterations:
        entry = grouped.setdefault(
            row.iteration_number,
            {
                "iteration_number": row.iteration_number,
                "winner": row.winner,
                "action_taken": row.action_taken,
                "variant_a": None,
                "variant_b": None,
                "timestamp": row.timestamp.isoformat() if row.timestamp else None,
            },
        )
        payload = {
            "campaign_external_id": row.campaign_external_id,
            "subject": row.content_subject,
            "body": row.content_body,
            "open_rate": row.open_rate,
            "click_rate": row.click_rate,
            "score": row.score,
            "total_eo": row.total_eo,
            "total_ec": row.total_ec,
            "metrics_snapshot": _safe_json_load(row.metrics_snapshot, {}),
        }
        if row.variant_name == "A":
            entry["variant_a"] = payload
        else:
            entry["variant_b"] = payload

    return [grouped[key] for key in sorted(grouped)]


@app.get("/api/analytics/trends")
async def get_aggregated_analytics(db: Session = Depends(get_db)):
    campaigns = db.query(Campaign).all()
    total_campaigns = len(campaigns)
    total_eo = sum(c.total_eo or 0 for c in campaigns)
    total_ec = sum(c.total_ec or 0 for c in campaigns)
    avg_open_rate = (
        sum(c.open_rate or 0 for c in campaigns) / total_campaigns if total_campaigns else 0
    )
    avg_click_rate = (
        sum(c.click_rate or 0 for c in campaigns) / total_campaigns if total_campaigns else 0
    )
    avg_coverage = (
        sum(c.coverage_count or 0 for c in campaigns) / total_campaigns if total_campaigns else 0
    )

    return {
        "total_campaigns": total_campaigns,
        "total_eo": total_eo,
        "total_ec": total_ec,
        "avg_open_rate": avg_open_rate,
        "avg_click_rate": avg_click_rate,
        "avg_coverage": avg_coverage,
    }


@app.get("/api/campaigns")
async def list_campaigns(db: Session = Depends(get_db)):
    campaigns = db.query(Campaign).order_by(Campaign.created_at.desc()).all()
    response = []

    for campaign in campaigns:
        grouped_iterations: dict[int, list[IterationHistory]] = {}
        for iteration in campaign.iterations:
            grouped_iterations.setdefault(iteration.iteration_number or 0, []).append(iteration)

        latest_iteration = (
            max(grouped_iterations.keys()) if grouped_iterations else None
        )
        latest_rows = grouped_iterations.get(latest_iteration, []) if latest_iteration is not None else []
        winning_variant = next((row.winner for row in latest_rows if row.winner), None)
        top_score = max((row.score for row in campaign.iterations if row.score is not None), default=None)
        parsed_brief = _safe_json_load(campaign.parsed_brief_json, {})

        response.append(
            {
                "id": campaign.id,
                "thread_id": campaign.thread_id,
                "brief": campaign.brief,
                "product_name": parsed_brief.get("product_name"),
                "status": campaign.status,
                "content_subject": campaign.content_subject,
                "open_rate": campaign.open_rate,
                "click_rate": campaign.click_rate,
                "total_eo": campaign.total_eo,
                "total_ec": campaign.total_ec,
                "coverage_count": campaign.coverage_count,
                "cohort_size": campaign.cohort_size,
                "iteration_count": len(grouped_iterations),
                "winning_variant": winning_variant,
                "top_score": top_score,
                "created_at": campaign.created_at.isoformat() if campaign.created_at else None,
                "updated_at": campaign.updated_at.isoformat() if campaign.updated_at else None,
            }
        )

    return response


@app.get("/api/health")
async def health(db: Session = Depends(get_db)):
    db_status = "ok"
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        db_status = "error"

    api_status = "skipped"
    try:
        import os
        api_base = os.getenv("CAMPAIGN_API_BASE", "http://localhost:5000/api")
        api_key = (os.getenv("CAMPAIGN_API_KEY", "") or "").strip()
        if api_key and api_key not in {"your_campaign_api_key_here", "your_campaign_api_key"}:
            headers = {"Authorization": f"Bearer {api_key}"}
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.get(f"{api_base}/openapi.json", timeout=2) as resp:
                    api_status = "ok" if resp.status == 200 else "error"
    except Exception:
        api_status = "unreachable"

    return {
        "status": "ok" if db_status == "ok" else "degraded",
        "db_status": db_status,
        "api_status": api_status,
        "timestamp": datetime.utcnow().isoformat(),
        "active_threads": len(active_threads),
    }
