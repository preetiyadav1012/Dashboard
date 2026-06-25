# Quick Start Guide

## ⚡ 5-Minute Setup

### Windows PowerShell

#### 1. Backend Setup (Terminal 1)
```powershell
# Navigate to backend directory
cd backend

# Create virtual environment (optional but recommended)
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Copy and edit .env file
Copy-Item .env.example .env
# Edit .env with your ServiceNow credentials (or skip for demo mode)

# Start the backend server
python app.py
```

You should see:
```
* Running on http://0.0.0.0:5000
```

#### 2. Frontend Setup (Terminal 2)
```powershell
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start the frontend
npm start
```

Your browser will automatically open at `http://localhost:3000`

### Windows Command Prompt

```cmd
REM Backend
cd backend
pip install -r requirements.txt
copy .env.example .env
python app.py

REM Frontend (in new cmd window)
cd frontend
npm install
npm start
```

## 🎯 First Steps

1. **Chat with the Agent**
   - Go to "Chat Agent" tab
   - Type: "What claims need reprocessing today?"
   - See the agent respond with sample claim data

2. **View the Dashboard**
   - Click "Dashboard" tab
   - See real-time statistics
   - Click "Refresh" for updated data

3. **Try Incident Lookup** (requires ServiceNow config)
   - Go to "Incident Lookup" tab
   - Search for an incident
   - View details and export as CSV

## 🔧 Configuration

### For Demo Mode (No ServiceNow)
Skip the .env configuration. The app works with sample data.

### With ServiceNow Integration
1. Edit `backend/.env`:
```
SERVICENOW_INSTANCE=your_instance.service-now.com
SERVICENOW_USERNAME=admin
SERVICENOW_PASSWORD=your_password
```

2. Instance URL format: `instancename.service-now.com` (without https://)

## 🐛 Common Issues

| Issue | Solution |
|-------|----------|
| "Address already in use" | Change PORT in `.env` to 5001 |
| npm: command not found | Install Node.js from nodejs.org |
| python: command not found | Install Python from python.org |
| CORS errors | Restart both backend and frontend |
| ServiceNow connection fails | Check credentials and instance URL |

## 📝 Sample Requests

### Chat Agent Examples
- "Reprocess claim CLM-2024-001"
- "What's the status of all claims?"
- "Generate analytics report"
- "Show me claim CLM-2024-002 details"

## 🚀 Next Steps

1. **Customize Claims**: Edit `backend/agents/claim_reprocessing_agent.py`
2. **Add More Features**: Extend components in `frontend/src/components/`
3. **Connect Real Database**: Replace sample data with actual database
4. **Deploy to Production**: Use Docker or cloud platform

## 📞 Need Help?

Check `README.md` for detailed documentation.

---

**Enjoy your Claims Management Dashboard!** 🎉
