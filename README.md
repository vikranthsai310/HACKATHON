# 🧠 HRM Decision System
## Hybrid LLM + Hierarchical Reasoning Model for Safe AI Decision-Making

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green.svg)](https://fastapi.tiangolo.com)
[![Status](https://img.shields.io/badge/Phase-1%20Complete-success.svg)](#)

---

## 📖 Overview

A revolutionary **hybrid AI decision system** that combines:
- 🗣️ **LLM (Gemini)** - Natural language understanding and intent extraction
- 🧠 **HRM** - Hierarchical Reasoning Model for safe, explainable decisions
- ✅ **Validation** - Schema validation and safety constraints
- 📊 **Audit Trail** - Complete decision traceability

### Why This Matters

**Traditional LLMs** hallucinate, can't guarantee policy compliance, and lack explainability.  
**Pure rule systems** can't understand natural language and require complex configuration.

**Our Solution:** LLM translates → HRM reasons → Safe execution with full audit trail.

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  USER: "Block suspicious IPs from last 24 hours"            │
└───────────────────────┬─────────────────────────────────────┘
                        ▼
                 ┌──────────────┐
                 │ Preprocessor │ → Normalize, extract keywords
                 └──────┬───────┘
                        ▼
                 ┌──────────────┐
                 │ LLM (Gemini) │ → Convert to structured intent
                 └──────┬───────┘
                        ▼
                 ┌──────────────┐
                 │  HRM Engine  │ → 3-level hierarchical reasoning
                 │  L1: Strategy│   (Strategic → Tactical → Operational)
                 │  L2: Tactics │
                 │  L3: Actions │
                 └──────┬───────┘
                        ▼
                 ┌──────────────┐
                 │   Executor   │ → Execute with safety controls
                 └──────┬───────┘
                        ▼
┌─────────────────────────────────────────────────────────────┐
│  OUTPUT: Decision + Explanation + Audit Trail               │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start (3 Steps)

### Step 1: Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### Step 2: Test the System

```bash
python test_system.py
```

You'll see:
- ✅ Complete pipeline execution
- ✅ Multiple scenario tests
- ✅ Full audit trail generation

### Step 3: Start API Server

```bash
python -m app.main
```

**Open:** http://localhost:8000/docs for interactive API documentation

---

## 💡 Example Usage

### Using the API

```bash
curl -X POST "http://localhost:8000/api/v1/decision" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "admin",
    "message": "Block IP 192.168.1.100"
  }'
```

### Using Python

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/decision",
    json={
        "user_id": "admin",
        "message": "Show me all failed login attempts from yesterday"
    }
)

print(response.json())
```

### Example Input/Output

**Input:**
```json
{
  "user_id": "security-admin",
  "message": "Block all suspicious IP addresses from the last 24 hours"
}
```

**Output:**
```json
{
  "decision_id": "dec-abc123",
  "status": "SUCCESS",
  "summary": "Block malicious network activity - SUCCESS",
  "actions_completed": [
    {
      "action": "BLOCK_IP",
      "status": "SUCCESS",
      "result": {
        "message": "[DRY-RUN] Would block 3 IP addresses",
        "ip_addresses": ["192.168.1.100", "10.0.0.50", "172.16.0.10"]
      }
    }
  ],
  "explanation": "Strategic Level: Approved security action...",
  "confidence": 0.95,
  "audit_trail": { ... }
}
```

---

## 📂 Project Structure

```
HACKATHON/
├── docs/                          # Documentation
│   ├── PROJECT.md                 # Complete project overview
│   ├── PHASE-1.md                 # ✅ Phase 1 (Complete)
│   ├── PHASE-2.md                 # Phase 2 plan
│   ├── PHASE-3.md                 # Phase 3 plan
│   └── PHASE-4.md                 # Phase 4 plan
│
├── backend/                       # ⭐ Python Backend (Phase 1)
│   ├── app/
│   │   ├── main.py               # FastAPI application
│   │   ├── api/                  # API routes
│   │   ├── core/                 # Core components
│   │   │   ├── preprocessor.py   # NLP preprocessing
│   │   │   ├── llm_interpreter.py # Gemini integration
│   │   │   ├── hrm_engine.py     # HRM reasoning
│   │   │   ├── action_executor.py # Action execution
│   │   │   └── schema_validator.py
│   │   ├── schemas/              # Pydantic models
│   │   └── utils/                # Utilities
│   ├── requirements.txt          # Dependencies
│   ├── test_system.py            # Full system test
│   ├── test_phase1.py            # Unit tests
│   └── README.md                 # Backend docs
│
├── frontend/                      # React UI (Phase 2)
│   └── (Coming soon)
│
├── HRM-main/                      # HRM Model (existing)
│   └── (Hierarchical Reasoning Model code)
│
├── ARCHITECTURE.md                # Architecture diagrams
├── PHASE-1-COMPLETE.md           # ✅ Phase 1 guide
└── README.md                      # This file
```

---

## 🎯 Features

### ✅ Phase 1 (Complete)

- ✅ **Natural Language Processing** - Understand user requests
- ✅ **LLM Integration** - Gemini API + Mock mode fallback
- ✅ **3-Level Reasoning** - Strategic → Tactical → Operational
- ✅ **20+ Action Handlers** - Security, access, compliance, query actions
- ✅ **Schema Validation** - Pydantic models for type safety
- ✅ **Dry-Run Mode** - Safe testing without real changes
- ✅ **Complete Audit Trail** - Every decision is traceable
- ✅ **REST API** - FastAPI with Swagger documentation
- ✅ **Unit Tests** - Comprehensive test coverage

### 🔜 Upcoming Phases

- **Phase 2** - React chatbot frontend with real-time interaction
- **Phase 3** - Full HRM model integration with GPU support
- **Phase 4** - Production features (database, auth, monitoring)

---

## 🎛️ Configuration

### Default Modes (Safe for Testing)

- **LLM Mode**: MOCK (works without API key)
- **HRM Mode**: SIMULATION (works without model weights)
- **Executor**: DRY-RUN (no real changes)

### Enable Gemini LLM

1. Get API key: https://makersuite.google.com/app/apikey
2. Create `.env` file:
   ```bash
   cd backend
   cp .env.example .env
   ```
3. Add your key:
   ```
   GEMINI_API_KEY=your_actual_key_here
   ```
4. Restart server (automatically switches to Gemini mode)

---

## 📊 API Endpoints

### Main Pipeline
- `POST /api/v1/decision` - Complete decision pipeline

### Component Testing
- `POST /api/v1/preprocess` - Test preprocessor
- `POST /api/v1/interpret` - Test LLM interpretation
- `POST /api/v1/hrm-input` - Generate HRM input
- `POST /api/v1/reason` - Test HRM reasoning

### Monitoring
- `GET /health` - Health check
- `GET /api/v1/audit-logs` - View audit logs
- `GET /api/v1/examples` - Get example requests

### Configuration
- `GET /api/v1/config/llm-mode` - Check LLM mode
- `POST /api/v1/config/executor-mode` - Set dry-run mode

**Full API Docs:** http://localhost:8000/docs

---

## 🧪 Testing

### Run Unit Tests
```bash
cd backend
pytest test_phase1.py -v
```

### Run Full System Test
```bash
python test_system.py
```

### Test Multiple Scenarios
The system includes 4 built-in test scenarios:
1. **Security** - Block suspicious IPs
2. **Access** - Grant/revoke permissions
3. **Query** - Fetch logs and data
4. **Compliance** - Generate audit reports

---

## 🛡️ Safety Features

1. **Dry-Run Mode** - Test without real execution
2. **Schema Validation** - Type-safe data processing
3. **Risk Assessment** - Automatic risk level evaluation
4. **Authorization Checks** - Configurable authorization requirements
5. **Audit Logging** - Complete decision traceability
6. **Fallback Actions** - Graceful error handling
7. **Constraint Validation** - Policy compliance checks

---

## 📚 Documentation

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture and data flow
- **[PHASE-1-COMPLETE.md](PHASE-1-COMPLETE.md)** - Phase 1 quick start
- **[backend/README.md](backend/README.md)** - Backend API documentation
- **[docs/PROJECT.md](docs/PROJECT.md)** - Complete project overview
- **API Docs** - http://localhost:8000/docs (when server is running)

---

## 🤝 Contributing

This is a hackathon project. For development:

1. Clone the repository
2. Install dependencies: `pip install -r backend/requirements.txt`
3. Run tests: `pytest backend/test_phase1.py -v`
4. Start server: `python -m backend.app.main`

---

## 📄 License

See LICENSE file for details.

---

## 🎉 Quick Commands

### PowerShell (Windows)
```powershell
cd backend
. .\commands.ps1    # Load helper commands
Show-Help           # See available commands
Test-System         # Run full test
Start-Server        # Start API
```

### Bash/Linux
```bash
cd backend
make help          # See available commands
make test          # Run tests
make test-full     # Run full system test
make run           # Start API server
```

---

## 📞 Support

- Check documentation in `docs/` folder
- View API documentation at `/docs` endpoint
- Run `python test_system.py` for diagnostics

---

**Status:** Phase 1 Complete ✅ | Ready for Phase 2 Development

**Last Updated:** January 2026
