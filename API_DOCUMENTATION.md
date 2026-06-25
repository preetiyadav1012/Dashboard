# API Documentation

Complete API reference for the Claims Management Dashboard backend.

## Base URL

```
http://localhost:5000
```

## Authentication

The current API uses no authentication for development. For production, add JWT or API keys.

## Endpoints

### 1. Chat Endpoint

**Send a message to the claim processing agent**

```
POST /api/chat
```

#### Request
```json
{
  "message": "Reprocess claim CLM-2024-001",
  "history": []
}
```

#### Parameters
- `message` (string, required): User message
- `history` (array, optional): Previous conversation history

#### Response (200 OK)
```json
{
  "response": "✅ Reprocessing initiated for claim CLM-2024-001\n\nClaim Details:\n• ID: CLM-2024-001\n• Amount: $5000.00\n• Description: Medical claim for surgery\n• Status: Reprocessing",
  "details": {
    "action": "reprocess",
    "claim_id": "CLM-2024-001",
    "status": "Reprocessing",
    "timestamp": "2024-04-30T10:30:00.000Z"
  }
}
```

#### Examples

**Example 1: Reprocess a claim**
```javascript
const response = await fetch('http://localhost:5000/api/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    message: 'Reprocess claim CLM-2024-001',
    history: []
  })
});
const data = await response.json();
```

**Example 2: Check claim status**
```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is the status of claim CLM-2024-002?",
    "history": []
  }'
```

---

### 2. Incident Search Endpoint

**Search for incidents in ServiceNow**

```
POST /api/incidents/search
```

#### Request
```json
{
  "query": "INC0000001",
  "search_type": "incident_number"
}
```

#### Parameters
- `query` (string, required): Search query string
- `search_type` (string, required): Type of search
  - `incident_number`: Search by incident number
  - `short_description`: Search by description
  - `state`: Search by status
  - `priority`: Search by priority

#### Response (200 OK)
```json
{
  "incidents": [
    {
      "sys_id": "12345678abcdef",
      "number": "INC0000001",
      "short_description": "System down",
      "description": "The production system is completely down",
      "state": "In Progress",
      "priority": "1 - Critical",
      "assignment_group": "L2 Support",
      "assigned_to": "John Doe",
      "created_on": "2024-04-28T10:00:00.000Z",
      "updated_on": "2024-04-30T15:30:00.000Z"
    }
  ],
  "count": 1
}
```

#### Error Response (200 with no results)
```json
{
  "incidents": [],
  "message": "No incidents found. Please check your ServiceNow credentials and configuration."
}
```

#### Examples

**Example 1: Search by incident number**
```javascript
const response = await fetch('http://localhost:5000/api/incidents/search', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    query: 'INC0000001',
    search_type: 'incident_number'
  })
});
const data = await response.json();
console.log(data.incidents);
```

**Example 2: Search by description**
```bash
curl -X POST http://localhost:5000/api/incidents/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "database error",
    "search_type": "short_description"
  }'
```

**Example 3: Search by status**
```bash
curl -X POST http://localhost:5000/api/incidents/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "In Progress",
    "search_type": "state"
  }'
```

---

### 3. Dashboard Stats Endpoint

**Get dashboard statistics and chart data**

```
GET /api/dashboard/stats
```

#### Response (200 OK)
```json
{
  "stats": {
    "total_claims": 3,
    "processed_today": 1,
    "pending_reprocessing": 2,
    "success_rate": 33.3,
    "avg_processing_time": "2.5 hours",
    "claims_last_24h": 2,
    "active_incidents": 3
  },
  "chart_data": [
    {
      "status": "Approved",
      "count": 1,
      "percentage": 33.3
    },
    {
      "status": "Pending",
      "count": 1,
      "percentage": 33.3
    },
    {
      "status": "Processing",
      "count": 1,
      "percentage": 33.3
    }
  ]
}
```

#### Examples

**Example 1: Using JavaScript/Fetch**
```javascript
const response = await fetch('http://localhost:5000/api/dashboard/stats');
const data = await response.json();
console.log(data.stats);
console.log(data.chart_data);
```

**Example 2: Using cURL**
```bash
curl http://localhost:5000/api/dashboard/stats
```

**Example 3: Using Python**
```python
import requests

response = requests.get('http://localhost:5000/api/dashboard/stats')
data = response.json()
print(data['stats'])
```

---

### 4. Health Check Endpoint

**Check if the API is running**

```
GET /api/health
```

#### Response (200 OK)
```json
{
  "status": "healthy",
  "environment": "development",
  "version": "1.0.0"
}
```

#### Examples

```bash
curl http://localhost:5000/api/health
```

---

### 5. Root Endpoint

**Get API information**

```
GET /
```

#### Response (200 OK)
```json
{
  "message": "Claims Management API",
  "version": "1.0.0",
  "endpoints": {
    "chat": "/api/chat",
    "incidents": "/api/incidents/search",
    "dashboard": "/api/dashboard/stats",
    "health": "/api/health"
  }
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "error": "Message is required"
}
```

### 404 Not Found
```json
{
  "error": "Endpoint not found"
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal server error"
}
```

---

## Chat Agent Intent Examples

The chat agent recognizes these intents:

### Reprocessing Intent
Triggered by: "reprocess", "reprocessing", "process"
```
User: "Reprocess claim CLM-2024-001"
Agent: Initiates reprocessing and returns status
```

### Status Check Intent
Triggered by: "status", "check", "pending"
```
User: "What claims need reprocessing?"
Agent: Returns list of all claims with status
```

### Claim Query Intent
Triggered by: "claim", "claims", "clm"
```
User: "Show me claim CLM-2024-002"
Agent: Returns detailed claim information
```

### Analytics Intent
Triggered by: "analytics", "report", "summary"
```
User: "Generate claim analytics report"
Agent: Returns statistics and analysis
```

### General Inquiry
Any other message
```
User: "Hello"
Agent: Returns help information with available commands
```

---

## Response Time

Typical response times:
- Chat API: 50-200ms
- Incident Search: 100-500ms (depends on ServiceNow)
- Dashboard Stats: 50-100ms
- Health Check: <10ms

---

## Rate Limiting

Currently no rate limiting is implemented. For production, add:
```python
from flask_limiter import Limiter
limiter = Limiter(app, key_func=get_remote_address)

@app.route('/api/chat', methods=['POST'])
@limiter.limit("10 per minute")
def chat():
    ...
```

---

## CORS Headers

The API allows CORS requests from all origins (`*`). For production, configure specific origins:

```python
CORS(app, resources={r"/api/*": {"origins": ["http://localhost:3000", "https://yourdomain.com"]}})
```

---

## Testing with cURL

### Test Chat
```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"What claims need reprocessing?","history":[]}'
```

### Test Incident Search
```bash
curl -X POST http://localhost:5000/api/incidents/search \
  -H "Content-Type: application/json" \
  -d '{"query":"INC","search_type":"incident_number"}'
```

### Test Dashboard
```bash
curl http://localhost:5000/api/dashboard/stats
```

### Test Health
```bash
curl http://localhost:5000/api/health
```

---

## Testing with Postman

1. Import the API URLs into Postman
2. Create POST requests for chat and incident search
3. Add JSON bodies as shown in examples
4. Send and view responses
5. Save collections for reuse

---

## Webhooks (Future)

Plan to add webhooks for:
- Claim status changes
- New incidents
- Analytics updates

```python
@app.route('/api/webhooks/claim-status', methods=['POST'])
def claim_status_webhook():
    # Handle webhook payload
    pass
```

---

## Versioning

Current version: `1.0.0`

Future versions will support:
```
GET /api/v1/...
GET /api/v2/...
```

---

## Deprecation

None at this time.

---

## Support

For API issues or questions:
1. Check this documentation
2. Review error messages
3. Check backend logs
4. See README.md for troubleshooting

---

Last Updated: April 30, 2026
