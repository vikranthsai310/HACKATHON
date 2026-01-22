# 🚀 PHASE 1 - QUICK START GUIDE

## ✅ Phase 1 Complete!

All core components have been built and are ready for testing.

---

## 📦 What Was Built

### Backend Components

| Component | File | Status |
|-----------|------|--------|
| **Schemas** | `app/schemas/request_schema.py` | ✅ Complete |
| **NLP Preprocessor** | `app/core/preprocessor.py` | ✅ Complete |
| **LLM Interpreter** | `app/core/llm_interpreter.py` | ✅ Complete (Gemini + Mock) |
| **HRM Engine** | `app/core/hrm_engine.py` | ✅ Complete (Simulation) |
| **Action Executor** | `app/core/action_executor.py` | ✅ Complete (Dry-run) |
| **API Routes** | `app/api/routes.py` | ✅ Complete |
| **Main App** | `app/main.py` | ✅ Complete |

### Documentation
- ✅ Backend README with full API documentation
- ✅ requirements.txt with all dependencies
- ✅ .env.example with configuration template
- ✅ test_system.py for component testing

---

## 🎯 Quick Start (3 Steps)

### Step 1: Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### Step 2: Test the System

Run the test script to verify everything works:

```bash
python test_system.py
```

You should see:
- ✅ All components initialized
- ✅ Complete pipeline execution
- ✅ Multiple scenario tests
- ✅ Audit trail generation

### Step 3: Start the API Server

```bash
python -m app.main
```

Or:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Visit: **http://localhost:8000/docs** for interactive API documentation

---

## 🧪 Testing the API

### Option 1: Using Swagger UI

1. Open http://localhost:8000/docs
2. Try the `/api/v1/decision` endpoint
3. Use this example request:

```json
{
  "user_id": "admin-001",
  "message": "Block all suspicious IP addresses from the last 24 hours",
  "context": {
    "user_role": "security_admin"
  }
}
```

### Option 2: Using cURL

```bash
curl -X POST "http://localhost:8000/api/v1/decision" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test-user",
    "message": "Block IP 192.168.1.100"
  }'
```

### Option 3: Using Python

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/decision",
    json={
        "user_id": "admin-001",
        "message": "Show me all login attempts from yesterday"
    }
)

print(response.json())
```

---

## 🔄 Complete Flow Example

**Input (Natural Language):**
```
"Block all suspicious IP addresses from the last 24 hours"
```

**Pipeline Processing:**

1. **NLP Preprocessor** → Normalizes text, extracts keywords
2. **LLM Interpreter** → Converts to structured intent (using Gemini or Mock)
3. **HRM Input Generator** → Creates 3-level hierarchy:
   - L1 Strategic: Goal, risk assessment, authorization
   - L2 Tactical: Strategy, policy, subsystem selection
   - L3 Operational: Specific actions with parameters
4. **HRM Engine** → Reasons over hierarchy, makes decision
5. **Action Executor** → Executes approved actions (dry-run mode)

**Output (Structured Decision):**
```json
{
  "decision_id": "dec-12345",
  "status": "SUCCESS",
  "summary": "Block malicious IP addresses - SUCCESS",
  "actions_completed": [
    {
      "action": "BLOCK_IP",
      "status": "SUCCESS",
      "result": {
        "message": "[DRY-RUN] Would block 1 IP addresses",
        "ip_addresses": ["192.168.1.100"]
      }
    }
  ],
  "explanation": "Strategic goal approved, actions executed",
  "confidence": 0.95,
  "audit_trail": { ... }
}
```

---

## 🎛️ Configuration Modes

### Current Defaults (Safe for Testing)

- ✅ **LLM Mode**: MOCK (no API key needed)
- ✅ **HRM Mode**: SIMULATION (no model weights needed)
- ✅ **Executor Mode**: DRY-RUN (no actual execution)

### Enable Gemini LLM

1. Get API key from https://makersuite.google.com/app/apikey
2. Create `.env` file:
   ```bash
   cp .env.example .env
   ```
3. Add your key:
   ```
   GEMINI_API_KEY=your_actual_key_here
   ```
4. Restart server

The system will automatically switch from MOCK to GEMINI mode!

---

## 📊 Available API Endpoints

### Main Endpoint
- `POST /api/v1/decision` - Complete decision pipeline

### Component Testing
- `POST /api/v1/preprocess` - Test NLP preprocessor
- `POST /api/v1/interpret` - Test LLM interpretation  
- `POST /api/v1/hrm-input` - Generate HRM input
- `POST /api/v1/reason` - Test HRM reasoning

### Monitoring
- `GET /health` - Health check
- `GET /api/v1/audit-logs` - View audit logs
- `GET /api/v1/examples` - Get example requests

### Configuration
- `GET /api/v1/config/llm-mode` - Check LLM mode
- `GET /api/v1/config/hrm-mode` - Check HRM mode
- `POST /api/v1/config/executor-mode` - Set dry-run mode

---

## 🧪 Example Test Scenarios

The system comes with 4 built-in test scenarios:

### 1. Security: Block IPs
```json
{
  "message": "Block all suspicious IP addresses from the last 24 hours"
}
```

### 2. Access Management
```json
{
  "message": "Grant user john.doe access to the analytics dashboard"
}
```

### 3. Query Logs
```json
{
  "message": "Show me all login attempts from yesterday"
}
```

### 4. Compliance Report
```json
{
  "message": "Generate an audit report for the last month"
}
```

---

## 🐛 Troubleshooting

### Issue: Import errors
**Solution:**
```bash
# Make sure you're in backend directory
cd backend
python -m app.main
```

### Issue: Port 8000 already in use
**Solution:**
```bash
uvicorn app.main:app --reload --port 8001
```

### Issue: Missing dependencies
**Solution:**
```bash
pip install -r requirements.txt
```

### Issue: Gemini API not working
**Solution:** 
- Check API key in `.env`
- System automatically falls back to MOCK mode
- No functionality is lost in MOCK mode for testing

---

## ✨ Key Features Working

✅ Natural language input processing  
✅ LLM interpretation (Gemini + Mock fallback)  
✅ 3-level hierarchical reasoning (L1, L2, L3)  
✅ Risk assessment and authorization  
✅ Action execution with dry-run mode  
✅ Complete audit trail  
✅ Explainable decisions  
✅ RESTful API with Swagger docs  
✅ Error handling and logging  
✅ Multiple intent types (Security, Access, Query, Compliance, System)

---

## 📈 Next Steps (Phase 2)

Phase 1 is complete! Next phases will add:

- **Phase 2**: Frontend UI (React chatbot)
- **Phase 3**: Real HRM model integration
- **Phase 4**: Production features (database, authentication, monitoring)

---

## 🎉 You're Ready!

The system is fully functional and ready for testing. Start with:

```bash
# Test components
python test_system.py

# Start API server
python -m app.main
```

Then visit **http://localhost:8000/docs** and start making requests!

---

**Need Help?**
- Check `backend/README.md` for detailed API documentation
- View interactive API docs at `/docs`
- All components have extensive inline documentation
