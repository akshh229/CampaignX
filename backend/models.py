from pydantic import BaseModel
from typing import Optional, List, Any


class BriefRequest(BaseModel):
    brief: str


class ApprovalRequest(BaseModel):
    thread_id: str
    decision: str  # "approved" or "rejected"
    feedback: Optional[str] = None  # Reason for rejection or notes


class CampaignResponse(BaseModel):
    thread_id: str
    state: dict
    status: str

class AgentEventResponse(BaseModel):
    id: int
    campaign_id: int
    agent_name: str
    event_type: str
    details: str
    timestamp: str

class IterationHistoryResponse(BaseModel):
    id: int
    campaign_id: int
    iteration_number: int
    variant_name: str
    content_subject: str
    content_body: str
    open_rate: Optional[float]
    click_rate: Optional[float]
    timestamp: str
