# Claims Management Dashboard

A comprehensive dashboard application with chat-based claim reprocessing agent, incident lookup from ServiceNow, and analytics.

## Features

✨ **Key Features:**
- **💬 Chat Interface**: Interactive chat with an AI-powered claim reprocessing agent
- **🔍 ServiceNow Integration**: Real-time incident lookup and search
- **📊 Dashboard**: Analytics and claims statistics
- **⚡ Real-time Processing**: Process claims and track status
- **📱 Responsive Design**: Works on desktop and mobile devices
- **🔐 Secure**: Basic auth for ServiceNow API

## Project Structure

```
dashboard/
├── frontend/                 # React frontend
│   ├── src/
│   │   ├── components/      # React components
│   │   │   ├── Chat.js      # Chat component
│   │   │   ├── IncidentLookup.js  # Incident lookup
│   │   │   └── Dashboard.js       # Dashboard stats
│   │   ├── App.js           # Main app component
│   │   └── index.js         # React entry point
│   └── package.json
├── backend/                 # Python Flask backend
│   ├── agents/
│   │   └── claim_reprocessing_agent.py  # Main agent logic
│   ├── servicenow_client.py  # ServiceNow API client
│   ├── config.py            # Configuration
│   ├── app.py              # Flask app
│   ├── requirements.txt    # Python dependencies
│   └── .env.example        # Environment variables template
└── README.md
```

## Prerequisites

- **Node.js** (v14 or higher)
- **Python** (v3.8 or higher)
- **npm** or **yarn**
- **ServiceNow Instance** (optional, for incident lookup)

## Setup Instructions

### 1. Clone or Extract the Project

Navigate to the project directory:
```bash
cd dashboard
```

### 2. Backend Setup

#### Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

#### Configure Environment Variables

Copy `.env.example` to `.env`:

**Windows (PowerShell):**
```powershell
Copy-Item .env.example .env
```

**Windows (Command Prompt):**
```cmd
copy .env.example .env
```

Edit `.env` file with your ServiceNow credentials:

```
SERVICENOW_INSTANCE=your_instance.service-now.com
SERVICENOW_USERNAME=your_username
SERVICENOW_PASSWORD=your_password
FLASK_ENV=development
FLASK_DEBUG=True
PORT=5000
```

**Note**: If you don't have ServiceNow credentials yet, the app will still work with sample data. The incident lookup will just show mock data or fail gracefully.

#### Start the Backend Server

**Windows (PowerShell):**
```powershell
python app.py
```

**Windows (Command Prompt):**
```cmd
python app.py
```

The server will start at `http://localhost:5000`

### 3. Frontend Setup

In a new terminal, navigate to the frontend directory:

```bash
cd frontend
```

#### Install Dependencies

```bash
npm install
```

#### Start the Frontend Development Server

```bash
npm start
```

The application will open at `http://localhost:3000`

## Usage

### Chat Agent

1. Navigate to the **Chat Agent** tab
2. Type your message about claims, e.g.:
   - "What claims need reprocessing today?"
   - "Reprocess claim #CLM-2024-001"
   - "Generate claim analytics report"
   - "Check the status of all claims"

### Incident Lookup

1. Go to the **Incident Lookup** tab
2. Select a search type (Incident Number, Description, Status, Priority)
3. Enter your search query
4. Click Search
5. Click on an incident to view details
6. Use Export CSV to download results

### Dashboard

1. Navigate to the **Dashboard** tab
2. View real-time statistics:
   - Total Claims
   - Claims Processed Today
   - Pending Reprocessing
   - Success Rate
3. See claim status distribution
4. View system information
5. Click Refresh to update stats

## API Endpoints

### Chat
```
POST /api/chat
Content-Type: application/json

Request:
{
  "message": "Your message here",
  "history": []
}

Response:
{
  "response": "Agent response",
  "details": { ... }
}
```

### Incident Search
```
POST /api/incidents/search
Content-Type: application/json

Request:
{
  "query": "INC0000001",
  "search_type": "incident_number"
}

Response:
{
  "incidents": [ ... ],
  "count": 1
}
```

### Dashboard Stats
```
GET /api/dashboard/stats

Response:
{
  "stats": { ... },
  "chart_data": [ ... ]
}
```

### Health Check
```
GET /api/health

Response:
{
  "status": "healthy",
  "environment": "development",
  "version": "1.0.0"
}
```

## ServiceNow Configuration

### Getting Your Instance URL

1. Log in to your ServiceNow account
2. Look at the URL: `https://yourinstance.service-now.com`
3. Your instance is `yourinstance`

### Creating a ServiceNow API User

1. Navigate to **System Security** → **Users**
2. Create a new user or use an existing one
3. Grant permissions for **Table API** access
4. Copy the username and password

### Enabling the Table API

1. Go to **System Web Services** → **Outbound**
2. Ensure REST API is enabled
3. Configure CORS if needed

## Sample Claims Data

The app comes with sample claims for testing:

- **CLM-2024-001**: Medical claim for surgery ($5,000)
- **CLM-2024-002**: Dental treatment claim ($2,500)
- **CLM-2024-003**: Vision care claim ($1,500)

You can add more claims by editing the `_initialize_claims_db()` method in `backend/agents/claim_reprocessing_agent.py`

## Troubleshooting

### Backend Connection Issues

**Error: "Failed to send message. Make sure the backend is running."**

Solution:
1. Check if the backend is running: `python app.py`
2. Ensure port 5000 is not in use
3. Check for firewall issues
4. Verify CORS is properly configured

### ServiceNow Connection Issues

**Error: "Failed to search incidents"**

Solution:
1. Verify instance URL in `.env` file (should not include `https://` or trailing `/`)
2. Check username and password
3. Ensure the user has API access permissions
4. Verify the instance is accessible from your network

### Port Already in Use

**Error: "Address already in use"**

Solution:
```bash
# Change the port in .env file
PORT=5001
```

Then restart the backend.

### CORS Issues

If you get CORS errors, the backend CORS configuration might need adjustment. Check that `flask-cors` is properly configured in `app.py`.

## Development

### Extending the Chat Agent

Edit `backend/agents/claim_reprocessing_agent.py` to add new functionality:

```python
def _handle_custom_intent(self, message):
    """Handle custom intent"""
    return {
        'response': 'Your response',
        'details': {...}
    }
```

### Adding New Frontend Components

Create new components in `frontend/src/components/` and add navigation in `frontend/src/App.js`

### Styling

All CSS files are in `frontend/src/` and `frontend/src/components/`. The design uses a purple gradient theme (`#667eea` to `#764ba2`).

## Performance Tips

1. **Backend Caching**: Consider caching ServiceNow results
2. **Frontend Optimization**: Use React.memo for components
3. **Database**: Implement proper indexing for claims
4. **API Rate Limiting**: Add rate limiting for production use

## Security Considerations

⚠️ **Important for Production:**

1. Never commit `.env` file with real credentials
2. Use environment variables or a secrets manager
3. Implement proper authentication (JWT, OAuth)
4. Add input validation and sanitization
5. Use HTTPS for all API calls
6. Implement request rate limiting
7. Add logging and monitoring

## Contributing

Feel free to submit issues and enhancement requests!

## License

MIT License - feel free to use this project for your needs.

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review the API documentation
3. Check the console logs (F12) for errors
4. Verify all environment variables are set correctly

## Changelog

### Version 1.0.0
- Initial release
- Chat interface with claim processing
- ServiceNow incident lookup
- Dashboard with analytics
- Responsive design
- Multi-tab interface

---

Built with ❤️ for claims management automation
