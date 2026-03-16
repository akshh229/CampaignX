import sys
with open('e:/CampaignX/backend/main.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_start = '''@app.post("/api/campaign/start")
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

    return {"thread_id": thread_id, "state": state, "status": state.get("status")}'''

new_start = '''def run_graph_background(initial_state, config, req_brief, campaign_id):
    try:
        campaign_graph.invoke(initial_state, config)
    except Exception as e:
        print(f"Background Agent error: {e}")
    # After the graph hits HITL interrupt, update DB
    snapshot = campaign_graph.get_state(config)
    if not snapshot:
        return
    state = snapshot.values
    from database import SessionLocal
    db = SessionLocal()
    try:
        campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
        if campaign:
            campaign.strategy = json.dumps(state.get("parsed_brief", {}))
            campaign.content_subject = (state.get("content_a") or {}).get("subject", "")
            campaign.content_body = (state.get("content_a") or {}).get("body", "")
            campaign.segments = json.dumps(state.get("segments", {}))
            campaign.status = state.get("status", "pending")
            db.commit()
    finally:
        db.close()


@app.post("/api/campaign/start")
async def start_campaign(req: BriefRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
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
    active_threads[thread_id] = config

    # Persist to DB initially
    campaign = Campaign(
        thread_id=thread_id,
        brief=req.brief,
        status="processing",
    )
    db.add(campaign)
    db.commit()
    db.refresh(campaign)
    campaign_db_ids[thread_id] = campaign.id

    background_tasks.add_task(run_graph_background, initial_state, config, req.brief, campaign.id)

    return {"thread_id": thread_id, "state": initial_state, "status": "processing"}'''


content = content.replace(old_start, new_start)

old_approve = '''@app.post("/api/campaign/approve")
async def approve_campaign(req: ApprovalRequest, db: Session = Depends(get_db)):
    config = active_threads.get(req.thread_id)
    if not config:
        raise HTTPException(status_code=404, detail="Thread not found")

    try:
        # Resume from interrupt using LangGraph Command
        # If there's feedback (e.g., rejected), pass it down so the content generator can retry
        resume_data = {"decision": req.decision, "feedback": req.feedback}
        campaign_graph.invoke(Command(resume=resume_data), config)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")

    # Read final state from snapshot
    snapshot = campaign_graph.get_state(config)
    state = snapshot.values

    # Update DB record with final results & approval record
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
            
            # Log approval history
            approval_entry = ApprovalHistory(
                campaign_id=campaign.id,
                reviewer_notes=req.feedback,
                decision=req.decision
            )
            db.add(approval_entry)
            db.commit()

    return {"thread_id": req.thread_id, "state": state, "status": state.get("status")}'''


new_approve = '''def resume_graph_background(config, resume_data, req, campaign_id):
    try:
        campaign_graph.invoke(Command(resume=resume_data), config)
    except Exception as e:
        print(f"Background Agent error: {e}")
    
    snapshot = campaign_graph.get_state(config)
    if not snapshot:
        return
    state = snapshot.values

    from database import SessionLocal
    db = SessionLocal()
    try:
        campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
        if campaign:
            campaign.status = state.get("status", campaign.status)
            campaign.content_subject = (state.get("content_a") or {}).get("subject", campaign.content_subject)
            campaign.content_body = (state.get("content_a") or {}).get("body", campaign.content_body)
            metrics = state.get("metrics") or {}
            campaign.open_rate = metrics.get("score", None)
            campaign.click_rate = metrics.get("score", None)
            
            # Log approval history
            approval_entry = ApprovalHistory(
                campaign_id=campaign.id,
                reviewer_notes=req.feedback,
                decision=req.decision
            )
            db.add(approval_entry)
            db.commit()
    finally:
        db.close()

@app.post("/api/campaign/approve")
async def approve_campaign(req: ApprovalRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    config = active_threads.get(req.thread_id)
    if not config:
        # try checking db and generating config
        campaign = db.query(Campaign).filter(Campaign.thread_id == req.thread_id).first()
        if not campaign:
            raise HTTPException(status_code=404, detail="Thread not found")
        config = {"configurable": {"thread_id": req.thread_id}}
        active_threads[req.thread_id] = config
    
    db_id = campaign_db_ids.get(req.thread_id)
    if not db_id:
        campaign = db.query(Campaign).filter(Campaign.thread_id == req.thread_id).first()
        db_id = campaign.id if campaign else None

    if db_id:
        campaign = db.query(Campaign).filter(Campaign.id == db_id).first()
        if campaign:
            campaign.status = "processing"
            db.commit()

    resume_data = {"decision": req.decision, "feedback": req.feedback}
    background_tasks.add_task(resume_graph_background, config, resume_data, req, db_id)

    return {"thread_id": req.thread_id, "status": "processing"}'''


content = content.replace(old_approve, new_approve)

with open('e:/CampaignX/backend/main.py', 'w', encoding='utf-8') as f:
    f.write(content)
