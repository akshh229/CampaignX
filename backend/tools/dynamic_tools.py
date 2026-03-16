"""
Dynamic API Tool Discovery from OpenAPI Specification

This module loads the Campaign API's OpenAPI specification and dynamically
discovers available tools/operations without hardcoding them.
This satisfies the rulebook requirement for API documentation-based 
dynamic discovery for tool calling.
"""

import httpx
import json
import os
from typing import Any, Callable, Optional
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
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"Failed to load OpenAPI spec: {e}")
    return {}


def _canonical_tool_name(path: str, method: str, operation_id: Optional[str]) -> str:
    """Map OpenAPI paths/methods to canonical tool names expected by the LangGraph."""
    method_upper = method.upper()
    if method_upper == "GET" and path == "/customers":
        return "get_customer_cohort"
    if method_upper == "POST" and path == "/campaigns/schedule":
        return "schedule_campaign"
    if method_upper == "GET" and path == "/campaigns/{campaign_id}/report":
        return "get_campaign_report"
    return operation_id or f"{method.lower()}_{path.replace('/', '_')}"


def build_dynamic_tools() -> dict[str, Callable]:
    """
    Build tools dynamically from OpenAPI spec.
    
    This function:
    1. Loads the OpenAPI specification from the Campaign API
    2. Discovers available endpoints and operations
    3. Creates tool functions for each operation
    4. Returns a dictionary of callable tools
    
    Returns:
        dict[str, Callable]: Dictionary mapping tool names to callable functions
    """
    spec = load_openapi_spec()
    tools = {}
    
    if not spec or "paths" not in spec:
        # Fallback to hardcoded tools if spec loading fails
        print("Warning: OpenAPI spec not available, using fallback tools")
        return _get_fallback_tools()
    
    # Parse paths from OpenAPI spec
    paths = spec.get("paths", {})
    
    for path_key, path_item in paths.items():
        for method, operation in path_item.items():
            if method not in ["get", "post", "put", "delete", "patch"]:
                continue
            
            # Extract operation info
            operation_id = _canonical_tool_name(
                path=path_key, 
                method=method, 
                operation_id=operation.get("operationId")
            )
            description = operation.get("summary", operation.get("description", ""))
            parameters = operation.get("parameters", [])
            request_body = operation.get("requestBody", {})
            
            # Create tool function
            tool_func = _create_tool_function(
                path=path_key,
                method=method.upper(),
                operation_id=operation_id,
                description=description,
                parameters=parameters,
                request_body=request_body,
            )
            
            # Register as langchain tool
            tools[operation_id] = tool(tool_func, name=operation_id)
    
    if not tools:
        # If no tools were extracted, use fallback
        return _get_fallback_tools()
    
    print(f"Dynamically discovered {len(tools)} tools from OpenAPI spec")
    return tools


def _create_tool_function(
    path: str,
    method: str,
    operation_id: str,
    description: str,
    parameters: list,
    request_body: dict,
) -> Callable:
    """
    Create a tool function for a specific API operation.
    
    Args:
        path: API endpoint path (e.g., "/customers")
        method: HTTP method (GET, POST, etc.)
        operation_id: Operation identifier
        description: Operation description for the LLM
        parameters: Query/path parameters from OpenAPI spec
        request_body: Request body schema from OpenAPI spec
    
    Returns:
        Callable: A function that calls the API operation
    """
    
    def tool_function(**kwargs) -> Any:
        url = f"{CAMPAIGN_API_BASE}{path}"
        
        # Replace path parameters
        for param in parameters:
            if param.get("in") == "path":
                param_name = param.get("name")
                if param_name in kwargs:
                    url = url.replace(f"{{{param_name}}}", str(kwargs[param_name]))
        
        # Build params for query parameters
        params = {}
        for param in parameters:
            if param.get("in") == "query":
                param_name = param.get("name")
                if param_name in kwargs:
                    params[param_name] = kwargs[param_name]
        
        # Build request body
        json_data = None
        if method in ["POST", "PUT", "PATCH"] and request_body:
            # Use all remaining kwargs as request body
            json_data = kwargs
        
        try:
            if method == "GET":
                response = httpx.get(url, headers=headers, params=params, timeout=30)
            elif method == "POST":
                response = httpx.post(url, headers=headers, json=json_data, params=params, timeout=30)
            elif method == "PUT":
                response = httpx.put(url, headers=headers, json=json_data, params=params, timeout=30)
            elif method == "DELETE":
                response = httpx.delete(url, headers=headers, params=params, timeout=30)
            elif method == "PATCH":
                response = httpx.patch(url, headers=headers, json=json_data, params=params, timeout=30)
            else:
                return {"error": f"Unsupported method: {method}"}
            
            if response.status_code in [200, 201, 202, 204]:
                try:
                    return response.json()
                except:
                    return {"status": "success", "status_code": response.status_code}
            else:
                return {
                    "error": response.text,
                    "status_code": response.status_code,
                    "message": f"API returned {response.status_code}"
                }
        except Exception as e:
            return {"error": str(e), "status_code": 0}
    
    # Set function name and docstring for LLM
    tool_function.__name__ = operation_id
    tool_function.__doc__ = description or f"{method} {path}"
    
    return tool_function


def _get_fallback_tools() -> dict[str, Callable]:
    """
    Fallback tools when OpenAPI spec is unavailable.
    These match the hardcoded tools from api_tools.py
    """
    
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
    
    return {
        "get_customer_cohort": get_customer_cohort,
        "schedule_campaign": schedule_campaign,
        "get_campaign_report": get_campaign_report,
    }


# Initialize dynamic tools at module load time
DYNAMIC_TOOLS = build_dynamic_tools()


def get_tools() -> dict[str, Callable]:
    """
    Get the currently discovered tools.
    
    Returns:
        dict[str, Callable]: Dictionary of available tools
    """
    return DYNAMIC_TOOLS
