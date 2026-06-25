# ✅ Project Setup Verification

This document helps you verify that everything is set up correctly.

## 📋 Checklist

### Prerequisites

- [ ] Node.js is installed (check: `node --version`)
- [ ] npm is installed (check: `npm --version`)
- [ ] Python 3.8+ is installed (check: `python --version`)
- [ ] Git is installed (optional)
- [ ] VS Code is installed (optional but recommended)

### Project Files Created

#### Root Directory
- [ ] README.md
- [ ] QUICKSTART.md
- [ ] GETTING_STARTED.md
- [ ] PROJECT_SUMMARY.md
- [ ] API_DOCUMENTATION.md
- [ ] DEPLOYMENT.md
- [ ] DOCKER_SETUP.md
- [ ] INDEX.md
- [ ] .gitignore
- [ ] start.bat
- [ ] start.sh
- [ ] INSTALL.sh
- [ ] dashboard.code-workspace

#### .vscode/
- [ ] tasks.json
- [ ] settings.json
- [ ] extensions.json

#### frontend/
- [ ] package.json
- [ ] public/index.html
- [ ] src/index.js
- [ ] src/App.js
- [ ] src/App.css
- [ ] src/components/Chat.js
- [ ] src/components/Chat.css
- [ ] src/components/IncidentLookup.js
- [ ] src/components/IncidentLookup.css
- [ ] src/components/Dashboard.js
- [ ] src/components/Dashboard.css

#### backend/
- [ ] app.py
- [ ] config.py
- [ ] requirements.txt
- [ ] .env.example
- [ ] servicenow_client.py
- [ ] agents/__init__.py
- [ ] agents/claim_reprocessing_agent.py

## 🔧 Installation Verification

### Step 1: Backend Setup

```bash
cd backend
python -m venv venv  # Optional but recommended
pip install -r requirements.txt
```

✅ **Verify**: You should see packages being installed without errors

### Step 2: Configuration

```bash
cd backend
copy .env.example .env  # Windows
# OR
cp .env.example .env    # Linux/macOS
```

✅ **Verify**: `.env` file exists in backend directory

### Step 3: Frontend Setup

```bash
cd frontend
npm install
```

✅ **Verify**: You should see `node_modules` folder created (may take a minute)

## 🚀 Running Verification

### Backend Test

```bash
cd backend
python app.py
```

✅ **Success indicators:**
- No error messages
- Shows: `Running on http://0.0.0.0:5000`
- No port conflict errors

**Press Ctrl+C to stop**

### Frontend Test

```bash
cd frontend
npm start
```

✅ **Success indicators:**
- Browser opens at http://localhost:3000
- Dashboard loads without errors
- Purple gradient header visible

**Press Ctrl+C to stop**

### API Test

With backend running, test API endpoints:

```bash
# Health check
curl http://localhost:5000/api/health

# Should return:
# {"status":"healthy","environment":"development","version":"1.0.0"}

# Chat test
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Hello","history":[]}'

# Dashboard test
curl http://localhost:5000/api/dashboard/stats
```

✅ **Success**: All endpoints return valid JSON

## 🌐 Browser Tests

With both backend and frontend running, verify in browser:

1. **Check tabs are visible**
   - [ ] 💬 Chat Agent tab
   - [ ] 🔍 Incident Lookup tab
   - [ ] 📊 Dashboard tab

2. **Test Chat Agent**
   - [ ] Type message in input
   - [ ] Click send or press Enter
   - [ ] Response appears from bot
   - [ ] No error messages

3. **Test Incident Lookup**
   - [ ] Can select search type
   - [ ] Can enter search query
   - [ ] Search button is clickable
   - [ ] Results display properly

4. **Test Dashboard**
   - [ ] Statistics cards display
   - [ ] Refresh button works
   - [ ] Charts display correctly

## 🔍 Troubleshooting Verification

If something doesn't work, check:

### Port Issues

```powershell
# Check if port 3000 is in use
Get-Process | Where-Object {$_.Handles -eq 3000}

# Check if port 5000 is in use
Get-Process | Where-Object {$_.Handles -eq 5000}

# Or use netstat
netstat -ano | findstr :3000
netstat -ano | findstr :5000
```

### Python Issues

```bash
# Check Python version
python --version  # Should be 3.8+

# Check pip is working
pip --version

# Check packages are installed
pip list
```

### Node/npm Issues

```bash
# Check Node version
node --version  # Should be 14+

# Check npm version
npm --version

# Clear npm cache
npm cache clean --force

# Reinstall node_modules
rm -r frontend/node_modules
npm install
```

### API Connectivity

```bash
# Test if backend is running
curl http://localhost:5000/api/health

# Check error message in browser console
# Press F12 in browser
# Go to Console tab
# Look for red error messages
```

## 📊 Verification Test Results

### Frontend

```
✅ React app loads
✅ All tabs are visible
✅ Chat interface works
✅ Buttons are clickable
✅ Styling displays correctly
✅ No console errors
✅ Responsive on mobile
```

### Backend

```
✅ Flask server starts
✅ No port conflicts
✅ API endpoints respond
✅ JSON responses valid
✅ No Python errors
✅ CORS headers present
✅ Environment variables loaded
```

### Integration

```
✅ Frontend connects to backend
✅ Chat messages sent/received
✅ Dashboard data loads
✅ Incident lookup works
✅ No CORS errors
✅ Error handling works
```

## 🚀 Production Verification (Optional)

### Build Frontend

```bash
cd frontend
npm run build
```

✅ **Verify**: `build/` folder created with optimized files

### Test Production Build

```bash
cd frontend
npm install -g serve
serve -s build -l 3000
```

✅ **Verify**: App works from production build

## 📝 Common Verification Issues

| Issue | Check | Solution |
|-------|-------|----------|
| Backend won't start | Port 5000 in use | Change PORT in .env |
| Frontend won't start | Port 3000 in use | Wait or close other app |
| npm not found | Node.js installed? | Install from nodejs.org |
| python not found | Python installed? | Install from python.org |
| Modules not found | npm install run? | Run `npm install` again |
| API doesn't respond | Backend running? | Run `python app.py` |
| CORS errors | Backend CORS set? | Check app.py CORS config |

## 🎯 Verification Summary

**If all checks pass:**
- ✅ Project is correctly installed
- ✅ All dependencies are available
- ✅ Frontend and backend communicate
- ✅ Ready for development or deployment

**If any checks fail:**
1. Review troubleshooting section above
2. Check error messages in console
3. See GETTING_STARTED.md for detailed help
4. Review README.md for comprehensive guide

## 📞 Verification Support

If verification fails, provide:
1. **What command**: Exactly what you ran
2. **Error message**: Full error text
3. **System info**: OS, Python version, Node version
4. **Logs**: Terminal and browser console output

## ✨ Next Steps

Once verification passes:
1. Explore the chat agent with different queries
2. Configure ServiceNow (if available)
3. Try the incident lookup
4. Review dashboard statistics
5. Customize for your needs
6. Plan deployment

---

**All verifications passed? You're ready to go!** 🎉

See [GETTING_STARTED.md](GETTING_STARTED.md) to learn how to use the dashboard.
