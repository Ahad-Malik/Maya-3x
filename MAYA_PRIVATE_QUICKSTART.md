# Maya Private - Quick Start Guide

## 🚀 Quick Start (5 minutes)

### Step 1: Install Dependencies
```powershell
# Backend dependencies (required)
pip install flask flask-cors openai

# Optional: For local inference
pip install transformers torch
```

### Step 2: Configure Environment
Create a `.env` file in the project root:
```env
OPENAI_API_KEY=your_openai_api_key_here
PRIVACY_MODE_DEFAULT=local
```

### Step 3: Start Backend
```powershell
python src/config/app2.py
```

Look for:
```
✓ Maya Private mode initialized successfully
```

### Step 4: Start Frontend
Open a new terminal:
```powershell
npm run dev
```

### Step 5: Access Maya Private
1. Open browser to `http://localhost:5173`
2. Click **"🔒 Private"** tab in the navigation
3. Enter a query and click **"Run Securely"**

## 🧪 Testing

Run the test script:
```powershell
python test_maya_private.py
```

Expected output:
```
✅ PASS - Privacy Status
✅ PASS - Local Inference
✅ PASS - Cloud Offload
✅ PASS - Offload Logs
```

## 📝 Example Queries

### Local Inference (< 2000 chars)
```
"Explain what Maya Private mode does"
```
Expected: 🟢 Local Secure Mode Active

### Cloud Offload (> 2000 chars)
```
Paste a long article or document (>2000 chars)
```
Expected: ⚠️ Offloaded to Cloud — Large Context

## 🔧 Troubleshooting

### "Maya Private mode not available"
- Check Python path in `app2.py`
- Verify `src/config/privacy/` directory exists

### "Local inference error"
- Normal if transformers not installed
- Will fallback to mock mode or cloud

### "OPENAI_API_KEY not configured"
- Add key to `.env` file
- Restart backend server

## 📚 Full Documentation
See [MAYA_PRIVATE_GUIDE.md](./MAYA_PRIVATE_GUIDE.md) for complete details.

---

**Ready to protect your privacy! 🔒**
