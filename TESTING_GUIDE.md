# CampaignX - Testing & Verification Guide
**Last Updated:** March 16, 2026 | **Status:** Ready for End-to-End Testing

---

## What's Been Tested ✅

### Backend Infrastructure
- [x] All Python modules import successfully
- [x] Database schema created with 4 tables + relationships
- [x] SQLite databases initialized (main + checkpoints)
- [x] GraphQL checkpointer configured (using MemorySaver)
- [x] All 6 API endpoints defined with proper routing
- [x] CORS middleware enabled for frontend
- [x] Error handling and fallbacks in place

### Frontend Components
- [x] All 7 React components present and properly typed
- [x] State management hooks configured
- [x] Polling loops defined (15s for health, 2.5s for status)
- [x] API calls properly formatted with endpoint URLs
- [x] Form handlers for brief submission and approvals
- [x] Toast notifications for errors

### Integration Points
- [x] Dynamic tool discovery wired into all 3 API-using nodes
- [x] Fallback tools configured for development
- [x] Database relationships properly configured
- [x] Event logging infrastructure in place
- [x] HITL approval with interrupts configured

### Known Fixed Issues
- [x] **SqliteSaver → MemorySaver**: Langgraph v1.0.10 doesn't have SqliteSaver
  - Solution: Using MemorySaver (checkpoints in memory, not persistent across restarts)
  - Impact: For each server restart, active campaigns lose some checkpoint history
  - Workaround: Implement manual checkpoint persistence if needed in production

---

## How to Run End-to-End Test

### Prerequisites
```bash
# Set required environment variables in backend/.env:
GROQ_API_KEY=sk_live_xxxxx              # Get from groq.com
CAMPAIGN_API_BASE=https://api.xxx       # For tool discovery
CAMPAIGN_API_KEY=xxxxx                  # For API auth
```

### Step 1: Start Backend (Terminal 1)
```bash
cd e:\CampaignX\backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Expected output:
# ✓ Using SqliteSaver for checkpoints (or ⚠ using MemorySaver)
# Uvicorn running on http://127.0.0.1:8000
```

### Step 2: Start Frontend (Terminal 2)
```bash
cd e:\CampaignX\frontend
npm run dev

# Expected output:
# VITE v5.x.x ready in 123 ms
# ➜ Local: http://localhost:8081/
```

### Step 3: Test in Browser
```
1. Open http://localhost:8081
2. Scroll down, click "Try Now"
3. Enter campaign brief (use sample or custom)
4. Click "Send"
5. Watch dashboard - should see:
   - Timeline: "Brief Parser" → "In progress"
   - Audit log: Events being logged
   - Status changing: parsing → segmenting → planning → ...
   - Metrics appearing when monitor phase starts
```

### Step 4: Test HITL Approval
```
1. When content is ready (Approval phase), see two variants
2. Click "Approve" button
3. Verify:
   - Timeline shows "HITL Approval" → "Completed"
   - Graph continues to scheduling
4. Back in history, click campaign to see full audit trail
```

### Step 5: Test Campaign History
```
1. After campaign completes (done or failed)
2. Click "History" tab at top
3. Should see campaign with:
   - Status, product name, scores
   - Clicking row shows full audit log, iterations, metrics
```

---

## Verification Checklist

### Backend Endpoints (via curl or Postman)

#### 1. Health Check
```bash
curl http://localhost:8000/api/health

# Expected response:
{
  "status": "ok",
  "timestamp": "2026-03-16T...",
  "active_threads": 0
}
```

#### 2. Campaign List
```bash
curl http://localhost:8000/api/campaigns

# Expected response:
[
  {
    "id": 1,
    "thread_id": "thread_1710...",
    "brief": "Run campaign for...",
    "status": "completed",
    "created_at": "2026-03-16T...",
    ...
  }
]
```

#### 3. Start Campaign
```bash
curl -X POST http://localhost:8000/api/campaign/start \
  -H "Content-Type: application/json" \
  -d '{"brief": "Test campaign brief"}'

# Expected response:
{
  "thread_id": "thread_1710xxx",
  "campaign_id": 1,
  "status": "processing",
  "state": { ... }
}
```

#### 4. Get Status
```bash
curl "http://localhost:8000/api/campaign/status/{thread_id}"

# Expected response:
{
  "thread_id": "...",
  "campaign_id": 1,
  "status": "segmented",
  "state": {
    "parsed_brief": { ... },
    "segments": { ... },
    ...
  }
}
```

#### 5. Get Events
```bash
curl "http://localhost:8000/api/campaign/1/events"

# Expected response:
[
  {
    "id": 1,
    "campaign_id": 1,
    "agent_name": "Brief Parser",
    "event_type": "complete",
    "details": "Parsed product USP...",
    "timestamp": "2026-03-16T..."
  },
  ...
]
```

#### 6. Approve Campaign
```bash
curl -X POST http://localhost:8000/api/campaign/approve \
  -H "Content-Type: application/json" \
  -d '{
    "thread_id": "thread_xxx",
    "decision": "approved",
    "feedback": null
  }'

# Expected response:
{
  "thread_id": "...",
  "campaign_id": 1,
  "status": "processing"
}
```

### Frontend Elements (Browser DevTools)

#### 1. Check Network Requests
Open DevTools → Network tab
```
Expected requests visible:
✓ GET /health (every 15s)
✓ GET /campaigns (on mount)
✓ POST /campaign/start (on submit)
✓ GET /campaign/status/xxx (every 2.5s)
✓ GET /campaign/1/events
✓ GET /campaign/1/approvals
✓ GET /campaign/1/iterations
```

#### 2. Check Console for Errors
```
Expected: No red errors in console
If errors appear: Check API_BASE URL and CORS settings
```

#### 3. Check Component Rendering
```
✓ BriefInput component shows form
✓ MetricsDashboard visible after scheduling
✓ ApprovalWorkspace shows when content_ready
✓ AuditLog updates with events
✓ CampaignHistory lists previous campaigns
✓ OptimizationHistory shows iterations if available
```

---

## Testing Scenarios

### Scenario 1: Happy Path (Full Campaign)
```
Input: Campaign brief
Expected Flow:
  1. Brief parsed
  2. Customers segmented
  3. Strategy planned
  4. Content generated
  5. User approves
  6. Campaign scheduled
  7. Metrics monitored
  8. Optimization happens (maybe)
  9. Campaign marked done

Verify:
- All 9 nodes appear in timeline
- Events logged for each step
- Final metrics displayed
- Campaign appears in history
```

### Scenario 2: Rejected Content
```
Input: Campaign brief (as above)
At step 5 (approval): Click "Regenerate"
Expected Flow:
  1. Content generation triggered again
  2. New variants generated
  3. Back to approval
  4. Can approve new content or reject again

Verify:
- Timeline shows loop: generate → approval → generate...
- Original content lost in history
- New metrics after approval
```

### Scenario 3: Sequential Campaigns
```
Input: Multiple campaign briefs (run in sequence)
Expected Flow:
  1. Campaign A submitted
  2. Before Campaign A ends: Campaign B submitted
  3. Both run in parallel
  4. Both appear in history

Verify:
- Active threads count > 1
- Separate timeline for each
- History shows both with different IDs
- No state contamination between campaigns
```

---

## Expected Test Results

### On Successful Run
```
✓ Backend starts without errors
✓ Frontend loads and shows dashboard
✓ Campaign submission triggers processing
✓ Timeline shows progress through all nodes
✓ Events logged to audit trail
✓ Metrics dashboard shows data when available
✓ Campaign appears in history after completion
✓ Can view full campaign details
✓ HITL approval works (approve/reject)
✓ Option to reject and regenerate works
```

### Common Issues & Solutions

#### Issue: "GROQ_API_KEY not set"
```
Solution: Set in backend/.env
GROQ_API_KEY=sk_live_xxxxx

Then restart backend:
cd backend
uvicorn main:app --reload
```

#### Issue: "Failed to fetch" in frontend
```
Solution: Check CORS and port
- Verify backend running on port 8000
- Check DevTools Network tab for actual error
- Verify API_BASE in Index.tsx = "http://localhost:8000/api"
- Check FirewallAllowing localhost:8000
```

#### Issue: Campaign stuck in "processing"
```
Solution:
1. Check backend logs for errors
2. Verify GROQ_API_KEY is valid
3. Check if LLM is responding (timeout issue)
4. Restart backend if needed
Backend might be hanging on LLM call
```

#### Issue: No metrics showing
```
Cause: CAMPAIGN_API_BASE unreachable
Solution:
1. Verify CAMPAIGN_API_BASE in backend/.env is correct
2. Verify CAMPAIGN_API_KEY is valid
3. Dynamic tools fallback should work
4. Check network connectivity to external API
```

---

## Performance Expectations

- **Brief parsing:** 3-10 seconds (LLM call)
- **Segmentation:** 1-2 seconds (list operations)
- **Strategy generation:** 3-10 seconds (LLM call)
- **Content generation:** 5-15 seconds (LLM calls × 2 variants)
- **Total workflow:** 20-60 seconds end-to-end
- **Polling latency:** <500ms for status endpoint
- **Database queries:** <100ms

---

## Database Inspection

### View Campaign Records
```sql
-- In SQLite browser or terminal:
sqlite3 backend/campaignx.db

-- List campaigns:
SELECT id, thread_id, brief, status, created_at FROM campaigns;

-- View events for campaign 1:
SELECT agent_name, event_type, details, timestamp 
FROM agent_events WHERE campaign_id = 1;

-- View approvals:
SELECT decision, reviewer_notes, timestamp 
FROM approval_history WHERE campaign_id = 1;

-- View iterations:
SELECT iteration_number, variant_name, open_rate, click_rate, score, winner
FROM iteration_history WHERE campaign_id = 1;
```

---

## Files to Review Before Testing

1. **backend/.env**
   - Ensure GROQ_API_KEY is set

2. **backend/graph.py** (line ~500)
   - Verify checkpointer initialization (should print ✓ or ⚠)

3. **frontend/src/pages/Index.tsx** (line ~25)
   - Check API_BASE = "http://localhost:8000/api"

4. **backend/database.py**
   - Verify all 4 tables defined

---

## Next Steps After Testing

### If All Tests Pass ✅
Move to final submission:
1. Record 3-minute screen demo
2. Create 5-slide presentation
3. Verify GitHub is public
4. Send submission email before March 14, 11:59:59 PM

### If Issues Found ❌
1. Check this guide for solutions
2. Review provided error messages
3. Check GitHub issues or documentation
4. Reach out for debugging assistance

---

## Submission Readiness

Once end-to-end testing is complete and all components work together:

- [x] Backend infrastructure ready
- [x] Frontend components ready  
- [x] API integrations complete
- [x] Database schema finalized
- [x] Dynamic tool discovery implemented
- [ ] Screen recording created (next)
- [ ] Slide deck created (next)
- [ ] Final submission (next)

**Current Status:** Infrastructure Ready → Move to Presentation Phase

---

*For support, check INTEGRATION_TEST_REPORT.md and SUBMISSION_CHECKLIST.md*
