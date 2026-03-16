# CampaignX API Contract

## Base URL
`/api`

## Endpoints

### 1. Start Campaign
*   **Method**: `POST`
*   **Path**: `/campaign/start`
*   **Body**:
    ```json
    {
      "brief": "String describing the campaign"
    }
    ```
*   **Response**:
    ```json
    {
      "thread_id": "thread_123456",
      "campaign_id": 12,
      "state": { /* Initial LangGraph state */ },
      "status": "processing"
    }
    ```

### 2. Approve/Reject Campaign
*   **Method**: `POST`
*   **Path**: `/campaign/approve`
*   **Body**:
    ```json
    {
      "thread_id": "thread_123456",
      "decision": "approved", // or "rejected"
      "feedback": "Optional feedback for rejection"
    }
    ```
*   **Response**: Same as Start Campaign.

### 3. Get Campaign Status
*   **Method**: `GET`
*   **Path**: `/campaign/status/{thread_id}`
*   **Response**:
    ```json
    {
      "thread_id": "thread_123456",
      "campaign_id": 12,
      "state": { /* Current state of the pipeline */ },
      "status": "processing | awaiting_approval | monitored | optimizing | done | failed"
    }
    ```

### 4. List Campaigns
*   **Method**: `GET`
*   **Path**: `/campaigns`
*   **Response**: Array of campaign objects with real metrics, iteration count, winning variant, EO/EC totals, and coverage summary.

### 5. Get Campaign Events (Agent Progress Logs)
*   **Method**: `GET`
*   **Path**: `/campaign/{campaign_id}/events`
*   **Response**: Chronological agent events with `agent_name`, `event_type`, `action`, `details`, and `timestamp`.

### 6. Get Approval History
*   **Method**: `GET`
*   **Path**: `/campaign/{campaign_id}/approvals`
*   **Response**: Array of `ApprovalHistory` events showing when reviewers accepted/rejected and their feedback.

### 7. Get Iteration History
*   **Method**: `GET`
*   **Path**: `/campaign/{campaign_id}/iterations`
*   **Response**: Grouped iteration records that include Variant A and Variant B metrics, winner, and optimization action per round.

### 8. Analytics Trends
*   **Method**: `GET`
*   **Path**: `/analytics/trends`
*   **Response**: Aggregated metrics across all campaigns including total EO, total EC, average rates, and average cohort coverage.
