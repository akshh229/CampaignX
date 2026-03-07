# CampaignX — AI Multi-Agent Email Campaign Manager

An AI-powered multi-agent system that automates email marketing campaigns for SuperBFSI (BFSI company). Built with LangGraph for agent orchestration, Groq LLM for fast inference, and a React dashboard for human-in-the-loop approval.

## Architecture

```
User Brief → Brief Parser → Customer Fetch → Segmentation → Content Gen (A/B)
   → Human Approval (HITL) → Schedule Campaigns → Monitor Metrics → Optimize → Loop
```

### Agents
| Agent | Role |
|-------|------|
| **Brief Parser** | Extracts structured data from natural language campaign brief |
| **Segmentation** | Splits customers into A/B test segments |
| **Content Generator** | Creates two email variants (professional + friendly) |
| **Scheduler** | Schedules campaigns via SuperBFSI API |
| **Monitor** | Fetches open/click rates, computes weighted score |
| **Optimizer** | Regenerates losing variant, loops up to 3 iterations |

### Scoring Formula
```
weighted_score = (click_rate × 0.7) + (open_rate × 0.3)
```

## Tech Stack
- **Backend**: Python, FastAPI, LangGraph, LangChain
- **LLM**: Groq API (llama3-8b-8192)
- **Frontend**: React + TypeScript (Vite)
- **Database**: SQLite + SQLAlchemy

## Quick Start

### 1. Get API Keys
- Groq: https://console.groq.com (free tier)
- Campaign API key from SuperBFSI

### 2. Configure
```bash
cd backend
# Edit .env with your keys
```

### 3. Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### 4. Frontend (new terminal)
```bash
cd frontend
npm install
npm run dev
```

### 5. Open
Navigate to http://localhost:5173 and submit a campaign brief.

## API Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/campaign/start` | Start a new campaign workflow |
| POST | `/api/campaign/approve` | Approve or reject campaign content |
| GET | `/api/campaign/status/{id}` | Get current campaign state |
| GET | `/api/campaigns` | List all campaigns |
| GET | `/api/health` | Health check |
