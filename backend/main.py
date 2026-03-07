from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
import json
from datetime import datetime
from dotenv import load_dotenv

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
        "content_a": None,
        "content_b": None,
        "hitl_decision": None,
        "campaign_ids": None,
        "metrics": None,
        "iteration": 0,
        "status": "started",
    }
    config = {"configurable": {"thread_id": thread_id}}

    # Run until HITL interrupt
    result = campaign_graph.invoke(initial_state, config)
    active_threads[thread_id] = config

    # Persist to DB
    campaign = Campaign(
        brief=req.brief,
        strategy=json.dumps(result.get("parsed_brief", {})),
        content_subject=result.get("content_a", {}).get("subject", ""),
        content_body=result.get("content_a", {}).get("body", ""),
        segments=json.dumps(result.get("segments", {})),
        status=result.get("status", "pending"),
    )
    db.add(campaign)
    db.commit()

    return {"thread_id": thread_id, "state": result, "status": result.get("status")}


@app.post("/api/campaign/approve")
async def approve_campaign(req: ApprovalRequest):
    config = active_threads.get(req.thread_id)
    if not config:
        raise HTTPException(status_code=404, detail="Thread not found")

    # Resume from interrupt with approval decision
    result = campaign_graph.invoke(None, config, input=req.decision)
    return {"thread_id": req.thread_id, "state": result, "status": result.get("status")}


@app.get("/api/campaign/status/{thread_id}")
async def get_status(thread_id: str):
    config = active_threads.get(thread_id)
    if not config:
        raise HTTPException(status_code=404, detail="Thread not found")
    state = campaign_graph.get_state(config)
    return {
        "thread_id": thread_id,
        "state": state.values,
        "status": state.values.get("status"),
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
