import httpx
import os
from langchain_core.tools import tool

CAMPAIGN_API_BASE = os.getenv(
    "CAMPAIGN_API_BASE", "https://api.superbfsi-campaignx.inxiteout.ai"
)
API_KEY = os.getenv("CAMPAIGN_API_KEY", "")

headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}


def load_openapi_spec() -> dict:
    """Load OpenAPI spec dynamically from the campaign API."""
    try:
        response = httpx.get(
            f"{CAMPAIGN_API_BASE}/openapi.json", headers=headers, timeout=10
        )
        return response.json()
    except Exception:
        return {}


@tool
def get_customer_cohort() -> list:
    """Fetch all customers from SuperBFSI Campaign API"""
    try:
        response = httpx.get(
            f"{CAMPAIGN_API_BASE}/customers", headers=headers, timeout=30
        )
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass
    return []


@tool
def schedule_campaign(
    customer_ids: list, subject: str, body: str, scheduled_time: str
) -> dict:
    """Schedule an email campaign via SuperBFSI Campaign API"""
    payload = {
        "customer_ids": customer_ids,
        "subject": subject,
        "body": body,
        "scheduled_time": scheduled_time,
    }
    try:
        response = httpx.post(
            f"{CAMPAIGN_API_BASE}/campaigns/schedule",
            json=payload,
            headers=headers,
            timeout=30,
        )
        if response.status_code in (200, 201):
            return response.json()
        return {"error": response.text, "status_code": response.status_code}
    except Exception as e:
        return {"error": str(e), "status_code": 0}


@tool
def get_campaign_report(campaign_id: str) -> dict:
    """Fetch open rate and click rate for a campaign"""
    try:
        response = httpx.get(
            f"{CAMPAIGN_API_BASE}/campaigns/{campaign_id}/report",
            headers=headers,
            timeout=30,
        )
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass
    return {"open_rate": 0, "click_rate": 0}
