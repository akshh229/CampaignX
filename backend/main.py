from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
import json
from datetime import datetime
from dotenv import load_dotenv
from langgraph.types import Command

load_dotenv()

from database import init_db, get_db, Campaign
from graph import campaign_graph, CampaignState

app = FastAPI(title="CampaignX API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()
active_threads: dict = {}  # thread_id -> config
campaign_db_ids: dict = {}  # thread_id -> db campaign id


class BriefRequest(BaseModel):
    brief: str


class ApprovalRequest(BaseModel):
    thread_id: str
    decision: str  # "approved" or "rejected"


@app.post("/api/campaign/start")
async def start_campaign(req: BriefRequest, db: Session = Depends(get_db)):
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
        "campaign_ids": None,
        "metrics": None,
        "iteration": 0,
        "status": "started",
    }
    config = {"configurable": {"thread_id": thread_id}}

    try:
        # Run until HITL interrupt
        result = campaign_graph.invoke(initial_state, config)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")

    active_threads[thread_id] = config

    # Get state (interrupt returns early, so read snapshot)
    snapshot = campaign_graph.get_state(config)
    state = snapshot.values

    # Persist to DB
    campaign = Campaign(
        brief=req.brief,
        strategy=json.dumps(state.get("parsed_brief", {})),
        content_subject=(state.get("content_a") or {}).get("subject", ""),
        content_body=(state.get("content_a") or {}).get("body", ""),
        segments=json.dumps(state.get("segments", {})),
        status=state.get("status", "pending"),
    )
    db.add(campaign)
    db.commit()
    db.refresh(campaign)
    campaign_db_ids[thread_id] = campaign.id

    return {"thread_id": thread_id, "state": state, "status": state.get("status")}


@app.post("/api/campaign/approve")
async def approve_campaign(req: ApprovalRequest, db: Session = Depends(get_db)):
    config = active_threads.get(req.thread_id)
    if not config:
        raise HTTPException(status_code=404, detail="Thread not found")

    try:
        # Resume from interrupt using LangGraph Command
        campaign_graph.invoke(Command(resume=req.decision), config)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")

    # Read final state from snapshot
    snapshot = campaign_graph.get_state(config)
    state = snapshot.values

    # Update DB record with final results
    db_id = campaign_db_ids.get(req.thread_id)
    if db_id:
        campaign = db.query(Campaign).filter(Campaign.id == db_id).first()
        if campaign:
            campaign.status = state.get("status", campaign.status)
            campaign.content_subject = (state.get("content_a") or {}).get("subject", campaign.content_subject)
            campaign.content_body = (state.get("content_a") or {}).get("body", campaign.content_body)
            metrics = state.get("metrics") or {}
            campaign.open_rate = metrics.get("score", None)
            campaign.click_rate = metrics.get("score", None)
            db.commit()

    return {"thread_id": req.thread_id, "state": state, "status": state.get("status")}


@app.get("/api/campaign/status/{thread_id}")
async def get_status(thread_id: str):
    config = active_threads.get(thread_id)
    if not config:
        raise HTTPException(status_code=404, detail="Thread not found")
    snapshot = campaign_graph.get_state(config)
    return {
        "thread_id": thread_id,
        "state": snapshot.values,
        "status": snapshot.values.get("status"),
    }


@app.get("/api/campaigns")
async def list_campaigns(db: Session = Depends(get_db)):
    campaigns = db.query(Campaign).order_by(Campaign.created_at.desc()).all()
    return [
        {
            "id": c.id,
            "brief": c.brief,
            "status": c.status,
            "content_subject": c.content_subject,
            "open_rate": c.open_rate,
            "click_rate": c.click_rate,
            "created_at": c.created_at.isoformat() if c.created_at else None,
        }
        for c in campaigns
    ]


@app.get("/api/health")
async def health():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}
