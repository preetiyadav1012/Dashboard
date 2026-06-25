# 🚀 Getting Started - Step by Step

## Option 1: Quick Start (Recommended for Windows)

### Step 1: Open the Project
```powershell
cd c:\Preeti\GenAIPOC\VSworkspace\dashboard
code .
```

### Step 2: Open Two Terminals
In VS Code:
- Click **Terminal** → **New Terminal**
- Split the terminal (click split icon or press `Ctrl+Shift+5`)

### Step 3: Terminal 1 - Backend
```powershell
cd backend
pip install -r requirements.txt
python app.py
```

Wait for:
```
WARNING in app.factory (app.py:xxxxx)
 * Running on http://0.0.0.0:5000
```

### Step 4: Terminal 2 - Frontend
```powershell
cd frontend
npm install
npm start
```

The browser will open automatically at `http://localhost:3000` ✅

## Option 2: Using VS Code Tasks

### Step 1: Install Dependencies
- Press `Ctrl+Shift+B`
- Select `Backend: Install Dependencies`
- Wait for completion

### Step 2: Start Backend
- Press `Ctrl+Shift+B`
- Select `Backend: Run Flask Server`

### Step 3: Start Frontend
- Press `Ctrl+Shift+B`
- Select `Frontend: Start React App`

## Option 3: Batch Script (Windows)
```powershell
.\start.bat
```

This opens two command windows automatically.

## Option 4: Manual - Two Command Prompts

**Command Prompt 1:**
```cmd
cd backend
pip install -r requirements.txt
python app.py
```

**Command Prompt 2:**
```cmd
cd frontend
npm install
npm start
```

## First Time Usage

### 1️⃣ Chat with the Agent
- Go to **Chat Agent** tab
- Type: `"What claims need reprocessing today?"`
- See the AI respond!

### 2️⃣ View Dashboard
- Click **Dashboard** tab
- See real-time statistics
- Click **Refresh** for updates

### 3️⃣ Try Incident Lookup
- Click **Incident Lookup** tab
- Note: Without ServiceNow config, this will show demo data
- To configure: See "ServiceNow Setup" below

## 🔧 ServiceNow Setup (Optional)

### If You Have ServiceNow:

1. Get your credentials:
   - Instance: `https://your-instance.service-now.com`
   - Username: Your ServiceNow user
   - Password: Your ServiceNow password

2. Configure the backend:
   - Open `backend/.env`
   - Add your credentials:
   ```
   SERVICENOW_INSTANCE=your-instance.service-now.com
   SERVICENOW_USERNAME=your_username
   SERVICENOW_PASSWORD=your_password
   ```
   - Save the file

3. Restart the backend:
   - Press `Ctrl+C` in the backend terminal
   - Run `python app.py` again

4. Try incident lookup in the app

### If You Don't Have ServiceNow:

The app works fine in demo mode! It will use sample data.

## 📱 Using the Dashboard

### 💬 Chat Agent
Send messages to ask the agent:
- `"Reprocess claim CLM-2024-001"`
- `"Show me status of all claims"`
- `"Generate analytics report"`

### 🔍 Incident Lookup
1. Choose search type (Number, Description, Status, Priority)
2. Enter search term
3. Click Search
4. Click incident to see details
5. Export to CSV if needed

### 📊 Dashboard
- View statistics in real-time
- See charts and breakdowns
- Click Refresh to update

## 🆘 Troubleshooting

### Backend Won't Start

**Error: `Address already in use`**
```powershell
# Find and kill process on port 5000
Get-Process | Where-Object {$_.Handles -eq 5000}
# Or change port in backend/.env
# PORT=5001
```

**Error: `pip: command not found`**
- Install Python from python.org
- Make sure to check "Add Python to PATH"
- Restart your terminal

### Frontend Won't Start

**Error: `npm: command not found`**
- Install Node.js from nodejs.org
- Restart your terminal

**Error: `Port 3000 already in use`**
```powershell
# Kill process on port 3000
Get-Process | Where-Object {$_.Handles -eq 3000}
# Or wait for other React app to close
```

### Can't Connect to Backend

**Error in console: "Failed to send message"**
- Make sure backend is running (`python app.py`)
- Check that port 5000 is open
- Try clicking Chat → Clear Chat
- Refresh the page

### ServiceNow Search Fails

**Error: "Failed to search incidents"**
- Check .env file is correctly filled
- Verify credentials are correct
- Ensure your ServiceNow instance allows API access
- Check network connectivity to ServiceNow

## 📁 Project Layout

```
dashboard/
├── frontend/          ← React app (port 3000)
├── backend/          ← Python API (port 5000)
├── .vscode/          ← VS Code configuration
├── README.md         ← Full documentation
├── QUICKSTART.md     ← This file
└── More guides...
```

## 💡 Tips

1. **Keep Both Running**: Backend and frontend should both be running
2. **Check Ports**: Backend on 5000, Frontend on 3000
3. **Logs Help**: Check browser console (F12) and terminal logs
4. **Restart When Stuck**: Stop (Ctrl+C) and run again
5. **Clear Cache**: Sometimes `npm cache clean --force` helps

## 🎯 Success Indicators

✅ Backend terminal shows: `Running on http://0.0.0.0:5000`  
✅ Frontend opens browser at `http://localhost:3000`  
✅ You see the purple dashboard  
✅ Chat Agent responds to messages  
✅ Dashboard shows statistics  

## 🚀 Next Steps

1. **Explore** - Try different chat queries
2. **Configure** - Add ServiceNow credentials if available
3. **Customize** - Edit sample claims in backend code
4. **Deploy** - See DEPLOYMENT.md for production setup
5. **Extend** - Add new features as needed

## 📞 Quick Reference

| What | Where | Command |
|------|-------|---------|
| Backend Code | `backend/app.py` | `python app.py` |
| Frontend Code | `frontend/src/` | `npm start` |
| Config | `backend/.env` | Edit with text editor |
| Documentation | `README.md` | Open in editor |
| Deployment | `DEPLOYMENT.md` | See for prod setup |

---

**You're all set! Enjoy your Claims Management Dashboard!** 🎉
