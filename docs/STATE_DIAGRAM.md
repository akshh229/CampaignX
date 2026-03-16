# CampaignX Agent Lifecycle State Diagram

```mermaid
stateDiagram-v2
    [*] --> ParseBrief: API /campaign/start
    
    ParseBrief --> FetchCustomers: brief_parsed
    FetchCustomers --> Segment: customers_fetched
    Segment --> Strategy: segmented
    Strategy --> GenerateContent: strategy_planned
    GenerateContent --> HITL_Approval: content_ready
    
    state HITL_Approval {
        [*] --> Pending
        Pending --> Approved: API /campaign/approve (decision="approved")
        Pending --> Rejected: API /campaign/approve (decision="rejected")
    }
    
    HITL_Approval --> Schedule: approved
    HITL_Approval --> GenerateContent: rejected (with feedback)
    
    Schedule --> Monitor: scheduled (campaign_ids generated)
    Monitor --> Optimize: monitored (metrics calculated)
    
    Optimize --> Schedule: optimizing (regenerate loser and relaunch automatically)
    Optimize --> [*]: done (max iterations reached or clear winner)
```

## Description
- **ParseBrief**: Extracts product names, USPs, and offers from raw text.
- **FetchCustomers**: Gathers customer cohorts from DB/API.
- **Segment**: Slices customers into A and B groups for testing.
- **Strategy**: Determines overarching communication plan.
- **GenerateContent**: Uses LLM to draft Email A and B incorporating any provided rejection feedback.
- **HITL_Approval**: Execution pauses. Waits for human reviewer to submit decision and optional feedback.
- **Schedule**: Triggers external email sender API.
- **Monitor**: Gathers open/click rates.
- **Optimize**: Chooses the winning variant using live report metrics, regenerates the losing content, relaunches automatically, or finishes after the max iteration count.
