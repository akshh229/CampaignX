<div align="center">

# 🚀 CampaignX — AI Multi-Agent Email Campaign Automation

**An autonomous AI agent system that plans, generates, approves, schedules, monitors, and self-optimizes email campaigns — all in a continuous loop.**

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=black)](https://react.dev)
[![LangGraph](https://img.shields.io/badge/LangGraph-Agent_Framework-1C3C3C?logo=langchain&logoColor=white)](https://langchain-ai.github.io/langgraph/)
[![Groq](https://img.shields.io/badge/Groq-LLaMA3--8B-F55036?logo=groq&logoColor=white)](https://groq.com)
[![SQLite](https://img.shields.io/badge/SQLite-003B57?logo=sqlite&logoColor=white)](https://sqlite.org)

*Built for **FrostHack @ XPECTO 2026** | IIT Mandi | Powered by InXiteOut*

</div>

---

## 🧠 Problem

Campaign managers at **SuperBFSI** waste 70%+ of their time on repetitive tasks — segmentation, email drafting, scheduling, reporting — instead of strategy. Manual campaigns see ~15% open rates and ~2% click rates. CampaignX replaces this entire workflow with an **autonomous AI agent loop**.

## 💡 Solution

A **LangGraph-powered multi-agent system** with 7 specialized agents working in a cyclic graph:

| # | Agent | Role |
|---|-------|------|
| 1 | 📋 **Brief Parser** | Extracts product, USP, special offers, CTA from natural language |
| 2 | 👥 **Segmentation** | Fetches cohort from SuperBFSI API, creates A/B segments |
| 3 | 🎯 **Strategy Planner** | Decides send time, targeting, A/B strategy |
| 4 | ✍️ **Content Generator** | Groq LLaMA3 generates 2 email variants (formal + friendly) |
| 5 | ⏸️ **HITL Approval** | LangGraph `interrupt()` pauses for human review on UI |
| 6 | 📤 **Scheduler** | Calls SuperBFSI API dynamically via OpenAPI spec discovery |
| 7 | 📊 **Monitor + Optimizer** | Computes weighted score, regenerates loser, auto-loops ×3 |

## 🏗️ Architecture

```
[Natural Language Brief Input]
         ↓
[Brief Parser Agent] → extracts product, USP, offers, CTA
         ↓
[Customer Segmentation] → fetches cohort, creates A/B segments
         ↓
[Strategy Planner] → send time, targeting, A/B plan
         ↓
[Content Generator] → Variant A (formal) + Variant B (friendly)
         ↓
[⏸ HITL Approval Node] → Human reviews on UI → Approve / Reject
         ↓ (approved)
[Campaign Scheduler] → Calls SuperBFSI API dynamically
         ↓
[Performance Monitor] → Fetches open rate + click rate per variant
         ↓
[Optimizer] → Weighted score → regenerates loser variant
         ↑_____________↓ (auto-loops up to 3 iterations)
```

**Scoring Formula:** `score = (click_rate × 0.7) + (open_rate × 0.3)`

## ⚡ Key Innovations

- **🔌 Dynamic OpenAPI Tool Calling** — Agent reads the SuperBFSI OpenAPI spec at runtime and discovers endpoints. Not hardcoded.
- **⏸️ LangGraph `interrupt()` for HITL** — Graph execution pauses at approval and resumes after human decision. Not a simple if-else.
- **🔄 A/B Auto-Optimization Loop** — Two variants → two segments → weighted scoring → loser regenerated → relaunched automatically.
- **👵 Demographic Personalization** — Female senior citizens receive special messaging about 0.25% bonus interest rate.

## 🛠️ Tech Stack

| Layer | Technologies |
|-------|-------------|
| **Backend** | Python · FastAPI · LangGraph · LangChain · SQLAlchemy · httpx |
| **LLM** | Groq API — `llama3-8b-8192` (free tier, <100ms inference) |
| **Frontend** | React 19 · TypeScript · Vite |
| **Database** | SQLite (campaigns, metrics, agent logs) |
| **APIs** | SuperBFSI Campaign Management (dynamic OpenAPI discovery) |

## 🚀 Quick Start

**Prerequisites:** Python 3.10+, Node.js 18+, [free Groq API key](https://console.groq.com)

```bash
# 1️⃣ Backend
cd backend
pip install -r requirements.txt
cp .env.example .env          # Add GROQ_API_KEY + CAMPAIGN_API_KEY
uvicorn main:app --reload     # → http://localhost:8000/docs

# 2️⃣ Frontend (new terminal)
cd frontend
npm install
npm run dev                   # → http://localhost:5173
```

**Environment Variables** (`backend/.env`):
```env
GROQ_API_KEY=your_groq_api_key
CAMPAIGN_API_BASE=https://api.superbfsi-campaignx.inxiteout.ai
CAMPAIGN_API_KEY=your_campaign_api_key
```

## 🧪 Sample Brief (paste in UI)

> Run email campaign for launching XDeposit, a flagship term deposit product from SuperBFSI, that gives 1 percentage point higher returns than its competitors. Announce an additional 0.25 percentage point higher returns for female senior citizens. Optimise for open rate and click rate. Don't skip emails to customers marked 'inactive'. Include the call to action: https://superbfsi.com/xdeposit/explore/.

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/campaign/start` | Submit brief → runs agents until HITL pause |
| `POST` | `/api/campaign/approve` | Approve or reject → resumes graph |
| `GET` | `/api/campaign/status/{id}` | Poll current campaign state |
| `GET` | `/api/campaigns` | List all campaigns with metrics |
| `GET` | `/api/health` | Health check |

## 🏆 Evaluation Alignment

| Criteria | How We Address It |
|----------|-------------------|
| Campaign performance | A/B testing + weighted score auto-optimization loop |
| AI agent system logic | 7-node LangGraph cyclic graph, not a chatbot |
| Human-in-the-loop | `interrupt()` pause/resume at approval node |
| Dynamic API discovery | OpenAPI spec-based tool calling at runtime |
| Code modularity | Each agent in its own file, clean separation of concerns |
| Innovation | Auto-optimization loop with demographic personalization |

---

<div align="center">
<sub>Built with ☕ and 🤖 at FrostHack, XPECTO 2026 — IIT Mandi</sub>
</div>
