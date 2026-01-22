# 📋 PHASE 1: Foundation & Core Architecture

## 🎯 Phase Overview

**Duration:** Week 1-2  
**Goal:** Set up project foundation, define schemas, and create basic system structure

---

## ✅ Deliverables

### 1.1 Project Setup
- [x] Initialize project repository
- [x] Set up folder structure
- [x] Configure development environment
- [x] Install core dependencies

### 1.2 Schema Definitions
- [x] Define input schema (user request format)
- [x] Define LLM output schema (structured intent)
- [x] Define HRM input schema (hierarchical levels)
- [x] Define output schema (decision + explanation)
- [x] Define audit log schema

### 1.3 Basic Components
- [x] Create schema validator
- [x] Create basic NLP preprocessor
- [x] Create mock LLM interpreter (+ Gemini integration)
- [x] Create placeholder HRM engine (+ simulation mode)
- [x] Create action executor
- [x] Create FastAPI endpoints

---

## 📁 Folder Structure

```
HACKATHON/
├── docs/                    # Documentation
│   ├── PROJECT.md
│   ├── PHASE-1.md
│   ├── PHASE-2.md
│   ├── PHASE-3.md
│   └── PHASE-4.md
│
├── frontend/                # React.js Chatbot UI
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   ├── services/
│   │   ├── styles/
│   │   └── App.jsx
│   └── package.json
│
├── backend/                 # Python Backend
│   ├── app/
│   │   ├── api/            # API endpoints
│   │   ├── core/           # Core logic
│   │   │   ├── preprocessor.py
│   │   │   ├── llm_interpreter.py
│   │   │   ├── schema_validator.py
│   │   │   ├── hrm_engine.py
│   │   │   └── action_executor.py
│   │   ├── schemas/        # Pydantic schemas
│   │   └── utils/
│   ├── config/
│   └── requirements.txt
│
└── HRM-main/               # HRM Model (existing)
```

---

## 📝 Schema Definitions

### Input Schema (User Request)

```json
{
  "request_id": "string",
  "user_id": "string",
  "timestamp": "ISO8601",
  "message": "string (natural language)",
  "context": {
    "session_id": "string",
    "previous_requests": []
  }
}
```

### LLM Output Schema (Structured Intent)

```json
{
  "intent_type": "ENUM[SECURITY, COMPLIANCE, ACCESS, SYSTEM, QUERY]",
  "goal": "string",
  "constraints": {
    "time_window": {},
    "filters": {},
    "thresholds": {}
  },
  "entities": {
    "targets": [],
    "subjects": [],
    "objects": []
  },
  "requested_actions": ["ACTION_1", "ACTION_2"],
  "confidence": 0.0-1.0
}
```

### HRM Input Schema (Hierarchical)

```json
{
  "L1_strategic": {
    "goal": "string",
    "authorization_required": boolean,
    "risk_level": "LOW|MEDIUM|HIGH"
  },
  "L2_tactical": {
    "strategy": "string",
    "policy": "string",
    "subsystem": "string"
  },
  "L3_operational": {
    "actions": [
      {
        "action": "string",
        "params": {},
        "conditions": []
      }
    ]
  }
}
```

### Output Schema (Decision)

```json
{
  "decision_id": "string",
  "status": "SUCCESS|DENIED|PARTIAL|CONDITIONAL",
  "summary": "string",
  "actions_completed": [],
  "explanation": "string",
  "audit_trail": {}
}
```

---

## 🔧 Implementation Tasks

### Task 1.1: Initialize Backend

```bash
# Create backend structure
mkdir -p backend/app/{api,core,schemas,utils}
mkdir -p backend/config

# Create requirements.txt
cd backend
pip install fastapi uvicorn pydantic python-dotenv
pip freeze > requirements.txt
```

### Task 1.2: Create Base Schemas

**File: `backend/app/schemas/request_schema.py`**

```python
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum

class IntentType(str, Enum):
    SECURITY = "SECURITY"
    COMPLIANCE = "COMPLIANCE"
    ACCESS = "ACCESS"
    SYSTEM = "SYSTEM"
    QUERY = "QUERY"

class UserRequest(BaseModel):
    request_id: str
    user_id: str
    timestamp: datetime
    message: str
    context: Optional[Dict] = None

class LLMOutput(BaseModel):
    intent_type: IntentType
    goal: str
    constraints: Dict
    entities: Dict
    requested_actions: List[str]
    confidence: float

class HRMInput(BaseModel):
    L1_strategic: Dict
    L2_tactical: Dict
    L3_operational: Dict

class DecisionOutput(BaseModel):
    decision_id: str
    status: str
    summary: str
    actions_completed: List[Dict]
    explanation: str
    audit_trail: Dict
```

### Task 1.3: Create Schema Validator

**File: `backend/app/core/schema_validator.py`**

```python
from typing import Dict, Any, Tuple
from app.schemas.request_schema import LLMOutput
import json

class SchemaValidator:
    """Validates LLM output against expected schema"""
    
    VALID_INTENTS = ["SECURITY", "COMPLIANCE", "ACCESS", "SYSTEM", "QUERY"]
    VALID_ACTIONS = [
        "BLOCK_IP", "ALLOW_IP", "NOTIFY", "ALERT",
        "GRANT_ACCESS", "REVOKE_ACCESS",
        "SCAN", "FILTER", "ANALYZE",
        "SCHEDULE", "EXECUTE", "LOG"
    ]
    
    def validate(self, llm_output: Dict[str, Any]) -> Tuple[bool, str, Dict]:
        """
        Validate LLM output
        Returns: (is_valid, error_message, validated_output)
        """
        errors = []
        
        # Check required fields
        required = ["intent_type", "goal", "requested_actions"]
        for field in required:
            if field not in llm_output:
                errors.append(f"Missing required field: {field}")
        
        if errors:
            return False, "; ".join(errors), {}
        
        # Validate intent type
        if llm_output["intent_type"] not in self.VALID_INTENTS:
            errors.append(f"Invalid intent_type: {llm_output['intent_type']}")
        
        # Validate actions
        for action in llm_output.get("requested_actions", []):
            action_name = action.split(":")[0]  # Handle ACTION:param format
            if action_name not in self.VALID_ACTIONS:
                errors.append(f"Unknown action: {action_name}")
        
        # Validate confidence
        conf = llm_output.get("confidence", 0)
        if not (0 <= conf <= 1):
            errors.append(f"Confidence must be 0-1, got: {conf}")
        
        if errors:
            return False, "; ".join(errors), {}
        
        return True, "", llm_output
```

### Task 1.4: Create Basic Preprocessor

**File: `backend/app/core/preprocessor.py`**

```python
import re
from datetime import datetime, timedelta
from typing import Dict, List

class NLPPreprocessor:
    """Preprocesses natural language input"""
    
    TIME_PATTERNS = {
        "yesterday": lambda: (datetime.now() - timedelta(days=1)).date(),
        "today": lambda: datetime.now().date(),
        "last hour": lambda: datetime.now() - timedelta(hours=1),
        "last 24 hours": lambda: datetime.now() - timedelta(hours=24),
        "this week": lambda: datetime.now() - timedelta(days=7),
    }
    
    KEYWORD_TAGS = {
        "security": ["suspicious", "attack", "threat", "block", "breach"],
        "compliance": ["policy", "audit", "regulation", "compliance"],
        "access": ["access", "permission", "grant", "revoke", "user"],
        "system": ["backup", "schedule", "maintenance", "restart"],
    }
    
    def preprocess(self, text: str) -> Dict:
        """
        Preprocess natural language text
        Returns structured preprocessing result
        """
        # Lowercase
        normalized = text.lower().strip()
        
        # Resolve time references
        time_refs = self._resolve_time_references(normalized)
        
        # Extract tags
        tags = self._extract_tags(normalized)
        
        # Clean text
        cleaned = self._clean_text(normalized)
        
        return {
            "original": text,
            "normalized": normalized,
            "cleaned": cleaned,
            "time_references": time_refs,
            "tags": tags
        }
    
    def _resolve_time_references(self, text: str) -> Dict:
        resolved = {}
        for pattern, resolver in self.TIME_PATTERNS.items():
            if pattern in text:
                resolved[pattern] = str(resolver())
        return resolved
    
    def _extract_tags(self, text: str) -> List[str]:
        tags = []
        for category, keywords in self.KEYWORD_TAGS.items():
            if any(kw in text for kw in keywords):
                tags.append(category.upper())
        return tags
    
    def _clean_text(self, text: str) -> str:
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
```

---

## ✅ Phase 1 Checklist

| Task | Status | Notes |
|------|--------|-------|
| Project structure created | ✅ | Complete folder structure with all packages |
| Schema definitions complete | ✅ | All schemas defined in request_schema.py |
| Schema validator implemented | ✅ | Full validation with error handling |
| NLP preprocessor implemented | ✅ | Time resolution, tagging, normalization |
| LLM interpreter created | ✅ | Gemini API integration + Mock mode |
| HRM engine implemented | ✅ | 3-level hierarchical reasoning |
| Action executor created | ✅ | 20+ actions with dry-run mode |
| Basic API endpoints created | ✅ | FastAPI with 10+ endpoints |
| Unit tests written | ✅ | test_phase1.py with full coverage |
| Configuration setup | ✅ | config.py, .env.example |
| Utilities created | ✅ | helpers.py with common functions |
| Documentation updated | ✅ | README.md, ARCHITECTURE.md, guides |

## 🎉 PHASE 1 COMPLETE!

All deliverables have been implemented and tested. The system is ready for Phase 2.

**Quick Start:**
```bash
cd backend
pip install -r requirements.txt
python test_system.py
python -m app.main
```

Visit: http://localhost:8000/docs for interactive API documentation

---

## 🚀 Next Phase

After completing Phase 1, proceed to **[PHASE-2.md](./PHASE-2.md)** for LLM Integration.
