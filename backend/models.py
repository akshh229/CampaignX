from pydantic import BaseModel
from typing import Optional, List


class BriefRequest(BaseModel):
    brief: str


class ApprovalRequest(BaseModel):
    thread_id: str
    decision: str  # "approved" or "rejected"


class CampaignResponse(BaseModel):
    thread_id: str
    state: dict
    status: str
