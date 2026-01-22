# 📋 PHASE 2: LLM Integration & Intent Parsing

## 🎯 Phase Overview

**Duration:** Week 2-3  
**Goal:** Integrate LLM for natural language understanding and intent extraction

---

## ✅ Deliverables

### 2.1 LLM Integration
- [ ] Set up LLM API connection (Gemini/OpenAI)
- [ ] Create prompt templates
- [ ] Implement intent extraction
- [ ] Handle LLM errors and fallbacks

### 2.2 Intent Parsing
- [ ] Parse structured intents from LLM output
- [ ] Extract entities (users, IPs, resources)
- [ ] Resolve action mappings
- [ ] Validate parsed output against schema

### 2.3 Testing
- [ ] Create test cases for various inputs
- [ ] Validate accuracy of intent extraction
- [ ] Test error handling

---

## 🔧 Implementation

### Task 2.1: LLM Interpreter

**File: `backend/app/core/llm_interpreter.py`**

```python
import os
import json
from typing import Dict, Any, Optional
from datetime import datetime

class LLMInterpreter:
    """
    Interprets natural language using LLM
    Outputs structured intent JSON
    """
    
    SYSTEM_PROMPT = """You are a semantic intent parser for a Hybrid Decision-Making System.
Your role is to extract structured intent from natural language requests.

IMPORTANT RULES:
1. You are NOT a decision maker - only extract intent
2. Output MUST be valid JSON matching the schema exactly
3. Use temperature=0 for deterministic output
4. If intent is unclear, set confidence < 0.5

VALID INTENT TYPES:
- SECURITY: Threat detection, blocking, security monitoring
- COMPLIANCE: Policy checks, audit, regulatory
- ACCESS: Permission management, user access
- SYSTEM: Maintenance, backups, scheduling
- QUERY: Information retrieval, status checks

VALID ACTIONS:
- BLOCK_IP, ALLOW_IP, NOTIFY, ALERT
- GRANT_ACCESS, REVOKE_ACCESS
- SCAN, FILTER, ANALYZE
- SCHEDULE, EXECUTE, LOG

OUTPUT SCHEMA:
{
  "intent_type": "SECURITY|COMPLIANCE|ACCESS|SYSTEM|QUERY",
  "goal": "string describing the goal",
  "constraints": {
    "time_window": {"start": "ISO8601", "end": "ISO8601"},
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
"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("LLM_API_KEY")
        self.model = os.getenv("LLM_MODEL", "gemini-pro")
    
    def interpret(self, preprocessed: Dict[str, Any]) -> Dict[str, Any]:
        """
        Interpret preprocessed text and extract structured intent
        """
        user_message = self._build_user_prompt(preprocessed)
        
        # For demo/testing, use mock response
        if os.getenv("USE_MOCK_LLM", "true").lower() == "true":
            return self._mock_interpret(preprocessed)
        
        # Real LLM call
        return self._call_llm(user_message)
    
    def _build_user_prompt(self, preprocessed: Dict) -> str:
        return f"""Parse the following user request into structured intent:

REQUEST: "{preprocessed['original']}"

PREPROCESSED INFO:
- Normalized: {preprocessed['normalized']}
- Time References: {preprocessed.get('time_references', {})}
- Tags: {preprocessed.get('tags', [])}

Output the structured intent JSON:"""

    def _mock_interpret(self, preprocessed: Dict) -> Dict[str, Any]:
        """Mock LLM response for testing"""
        text = preprocessed['normalized']
        tags = preprocessed.get('tags', [])
        
        # Determine intent type from tags
        intent_type = "QUERY"
        if "SECURITY" in tags:
            intent_type = "SECURITY"
        elif "COMPLIANCE" in tags:
            intent_type = "COMPLIANCE"
        elif "ACCESS" in tags:
            intent_type = "ACCESS"
        elif "SYSTEM" in tags:
            intent_type = "SYSTEM"
        
        # Extract basic actions
        actions = []
        if "block" in text:
            actions.append("BLOCK_IP")
        if "notify" in text or "alert" in text:
            actions.append("NOTIFY")
        if "scan" in text or "check" in text or "find" in text:
            actions.append("SCAN")
        if "grant" in text or "give" in text:
            actions.append("GRANT_ACCESS")
        if "revoke" in text or "remove" in text:
            actions.append("REVOKE_ACCESS")
        if not actions:
            actions.append("ANALYZE")
        
        # Build time constraints
        time_refs = preprocessed.get('time_references', {})
        time_window = {}
        if time_refs:
            first_ref = list(time_refs.values())[0]
            time_window = {
                "start": first_ref,
                "end": str(datetime.now())
            }
        
        return {
            "intent_type": intent_type,
            "goal": f"Process {intent_type.lower()} request",
            "constraints": {
                "time_window": time_window,
                "filters": {},
                "thresholds": {}
            },
            "entities": {
                "targets": self._extract_entities(text),
                "subjects": [],
                "objects": []
            },
            "requested_actions": actions,
            "confidence": 0.85
        }
    
    def _extract_entities(self, text: str) -> list:
        """Extract basic entities from text"""
        entities = []
        
        # IP pattern
        import re
        ips = re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', text)
        entities.extend([{"type": "ip", "value": ip} for ip in ips])
        
        # Email pattern
        emails = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', text)
        entities.extend([{"type": "email", "value": email} for email in emails])
        
        return entities
    
    def _call_llm(self, prompt: str) -> Dict[str, Any]:
        """Call actual LLM API"""
        try:
            import google.generativeai as genai
            
            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel(self.model)
            
            response = model.generate_content(
                f"{self.SYSTEM_PROMPT}\n\n{prompt}",
                generation_config={
                    "temperature": 0,
                    "response_mime_type": "application/json"
                }
            )
            
            return json.loads(response.text)
            
        except Exception as e:
            return {
                "error": str(e),
                "intent_type": "QUERY",
                "goal": "Error processing request",
                "constraints": {},
                "entities": {},
                "requested_actions": [],
                "confidence": 0.0
            }
```

### Task 2.2: API Endpoint

**File: `backend/app/api/chat.py`**

```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime
import uuid

from app.core.preprocessor import NLPPreprocessor
from app.core.llm_interpreter import LLMInterpreter
from app.core.schema_validator import SchemaValidator

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    user_id: Optional[str] = "anonymous"
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    request_id: str
    status: str
    intent: Optional[Dict] = None
    message: str
    timestamp: str

# Initialize components
preprocessor = NLPPreprocessor()
llm_interpreter = LLMInterpreter()
schema_validator = SchemaValidator()

@router.post("/chat", response_model=ChatResponse)
async def process_chat(request: ChatRequest):
    """
    Process natural language chat request
    
    Flow:
    1. Preprocess input
    2. Send to LLM interpreter
    3. Validate output schema
    4. Return structured intent
    """
    request_id = str(uuid.uuid4())[:8]
    timestamp = datetime.now().isoformat()
    
    try:
        # Step 1: Preprocess
        preprocessed = preprocessor.preprocess(request.message)
        
        # Step 2: LLM Interpretation
        llm_output = llm_interpreter.interpret(preprocessed)
        
        # Step 3: Schema Validation
        is_valid, error, validated = schema_validator.validate(llm_output)
        
        if not is_valid:
            return ChatResponse(
                request_id=request_id,
                status="VALIDATION_FAILED",
                intent=None,
                message=f"Could not parse request: {error}",
                timestamp=timestamp
            )
        
        # Step 4: Return validated intent
        return ChatResponse(
            request_id=request_id,
            status="INTENT_PARSED",
            intent=validated,
            message=f"Intent extracted: {validated['intent_type']} - {validated['goal']}",
            timestamp=timestamp
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

---

## 📊 Test Cases

### Test Case 1: Security Request
```
Input: "Block all suspicious login attempts from foreign IPs in the last 24 hours"

Expected Output:
{
  "intent_type": "SECURITY",
  "goal": "Block suspicious foreign login attempts",
  "constraints": {
    "time_window": {"start": "2026-01-21T20:56:00", "end": "2026-01-22T20:56:00"}
  },
  "requested_actions": ["BLOCK_IP", "SCAN"],
  "confidence": 0.9
}
```

### Test Case 2: Access Request
```
Input: "Grant John Smith read access to the financial reports"

Expected Output:
{
  "intent_type": "ACCESS",
  "goal": "Grant read access to user",
  "entities": {
    "subjects": [{"type": "user", "value": "John Smith"}],
    "objects": [{"type": "resource", "value": "financial reports"}]
  },
  "requested_actions": ["GRANT_ACCESS"],
  "confidence": 0.95
}
```

### Test Case 3: System Request
```
Input: "Schedule database backup for 2 AM tonight"

Expected Output:
{
  "intent_type": "SYSTEM",
  "goal": "Schedule database backup",
  "constraints": {
    "time_window": {"scheduled": "02:00"}
  },
  "requested_actions": ["SCHEDULE"],
  "confidence": 0.9
}
```

---

## ✅ Phase 2 Checklist

| Task | Status | Notes |
|------|--------|-------|
| LLM API connection | ⬜ | |
| Prompt templates created | ⬜ | |
| Intent extractor implemented | ⬜ | |
| Entity extraction working | ⬜ | |
| Schema validation passing | ⬜ | |
| Test cases passing | ⬜ | |
| Error handling complete | ⬜ | |

---

## 🚀 Next Phase

After completing Phase 2, proceed to **[PHASE-3.md](./PHASE-3.md)** for HRM Engine Implementation.
