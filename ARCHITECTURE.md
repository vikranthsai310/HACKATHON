# 🏗️ System Architecture - HRM Decision System

## Complete Data Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        USER INTERACTION LAYER                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  User Input: "Block all suspicious IP addresses from the last 24 hours"     │
│                                                                              │
└──────────────────────────────────┬──────────────────────────────────────────┘
                                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         API LAYER (FastAPI)                                  │
│                    POST /api/v1/decision                                     │
└──────────────────────────────────┬──────────────────────────────────────────┘
                                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    STEP 1: NLP PREPROCESSING                                 │
│                     (preprocessor.py)                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│  Input:  "Block all suspicious IP addresses from the last 24 hours"         │
│  Output: {                                                                   │
│    "normalized_text": "block all suspicious ip addresses last 24 hours",    │
│    "tags": ["security"],                                                     │
│    "keywords": ["block", "suspicious", "ip"],                               │
│    "time_references": {"last 24 hours": "2024-01-21T00:00:00Z"}            │
│  }                                                                           │
└──────────────────────────────────┬──────────────────────────────────────────┘
                                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    STEP 2: LLM INTERPRETATION                                │
│                   (llm_interpreter.py)                                       │
│                   Gemini API or Mock Mode                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│  Converts natural language → Structured Intent                              │
│                                                                              │
│  LLMOutput: {                                                                │
│    "intent_type": "SECURITY",                                               │
│    "goal": "Block malicious network activity",                              │
│    "entities": {                                                             │
│      "targets": ["IP addresses"],                                           │
│    },                                                                        │
│    "constraints": {                                                          │
│      "time_window": {"last_24_hours": "2024-01-21T00:00:00Z"}              │
│    },                                                                        │
│    "requested_actions": ["BLOCK_IP", "UPDATE_FIREWALL_RULES"],             │
│    "confidence": 0.95                                                        │
│  }                                                                           │
└──────────────────────────────────┬──────────────────────────────────────────┘
                                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                 STEP 3: HRM INPUT GENERATION                                 │
│                  (llm_interpreter.py)                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│  Converts LLM Output → 3-Level Hierarchy                                    │
│                                                                              │
│  HRMInput: {                                                                 │
│    "L1_strategic": {                  ← High-level goals                     │
│      "goal": "Block malicious network activity",                            │
│      "risk_level": "HIGH",                                                   │
│      "authorization_required": true,                                         │
│      "priority": 8                                                           │
│    },                                                                        │
│    "L2_tactical": {                   ← Strategy & policy                    │
│      "strategy": "threat_mitigation",                                        │
│      "policy": "security_blocking_policy",                                   │
│      "subsystem": "firewall",                                                │
│      "constraints": ["max_blocks_per_hour: 100"]                            │
│    },                                                                        │
│    "L3_operational": {                ← Concrete actions                     │
│      "actions": [                                                            │
│        {                                                                     │
│          "action": "BLOCK_IP",                                              │
│          "params": {"ip_list": ["192.168.1.100"]},                         │
│          "conditions": ["authorization_granted"]                            │
│        }                                                                     │
│      ]                                                                       │
│    }                                                                         │
│  }                                                                           │
└──────────────────────────────────┬──────────────────────────────────────────┘
                                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    STEP 4: HRM REASONING ENGINE                              │
│                      (hrm_engine.py)                                         │
│                   Hierarchical Decision Making                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  L1 STRATEGIC REASONING:                                                     │
│  ┌──────────────────────────────────────────────────────────────┐           │
│  │ • Assess goal: "Block malicious network activity"            │           │
│  │ • Check authorization: REQUIRED (HIGH risk)                  │           │
│  │ • Evaluate risk: HIGH (block operations are sensitive)       │           │
│  │ • Decision: APPROVED (for demo/simulation)                   │           │
│  └──────────────────────────────────────────────────────────────┘           │
│                          ▼                                                   │
│  L2 TACTICAL PLANNING:                                                       │
│  ┌──────────────────────────────────────────────────────────────┐           │
│  │ • Select strategy: threat_mitigation                         │           │
│  │ • Apply policy: security_blocking_policy                     │           │
│  │ • Target subsystem: firewall                                 │           │
│  │ • Validate constraints: ✓ All constraints met                │           │
│  └──────────────────────────────────────────────────────────────┘           │
│                          ▼                                                   │
│  L3 OPERATIONAL EXECUTION:                                                   │
│  ┌──────────────────────────────────────────────────────────────┐           │
│  │ • Check pre-conditions for BLOCK_IP                          │           │
│  │ • Verify: authorization_granted ✓                            │           │
│  │ • Execute action: BLOCK_IP                                   │           │
│  │ • Status: SUCCESS                                            │           │
│  └──────────────────────────────────────────────────────────────┘           │
│                                                                              │
│  DecisionOutput: {                                                           │
│    "status": "SUCCESS",                                                      │
│    "actions_completed": [...],                                               │
│    "confidence": 0.95,                                                       │
│    "audit_trail": {...}                                                      │
│  }                                                                           │
└──────────────────────────────────┬──────────────────────────────────────────┘
                                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    STEP 5: ACTION EXECUTION                                  │
│                    (action_executor.py)                                      │
│                    Mode: DRY-RUN (safe testing)                              │
├─────────────────────────────────────────────────────────────────────────────┤
│  For each action in decision:                                                │
│                                                                              │
│  Action: BLOCK_IP                                                            │
│  ┌──────────────────────────────────────────────────────────────┐           │
│  │ • Get handler: _action_block_ip()                            │           │
│  │ • Parameters: {"ip_list": ["192.168.1.100"]}                │           │
│  │ • Mode: DRY-RUN                                              │           │
│  │ • Execute: Simulate blocking (no real changes)               │           │
│  │ • Result: "[DRY-RUN] Would block 1 IP addresses"            │           │
│  │ • Log: Audit entry created                                   │           │
│  └──────────────────────────────────────────────────────────────┘           │
│                                                                              │
│  Available Actions:                                                          │
│  • Security: BLOCK_IP, UNBLOCK_IP, UPDATE_FIREWALL_RULES                   │
│  • Access: GRANT_ACCESS, REVOKE_ACCESS                                      │
│  • Query: QUERY_DATABASE, FETCH_LOGS                                        │
│  • Compliance: GENERATE_AUDIT_REPORT, VERIFY_COMPLIANCE                    │
│  • System: EXECUTE_COMMAND, RESTART_SERVICE                                 │
└──────────────────────────────────┬──────────────────────────────────────────┘
                                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      FINAL OUTPUT TO USER                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│  {                                                                           │
│    "decision_id": "dec-abc123",                                             │
│    "request_id": "req-xyz789",                                              │
│    "status": "SUCCESS",                                                      │
│    "summary": "Block malicious network activity - SUCCESS",                 │
│    "actions_completed": [                                                    │
│      {                                                                       │
│        "action": "BLOCK_IP",                                                │
│        "status": "SUCCESS",                                                  │
│        "result": {                                                           │
│          "message": "[DRY-RUN] Would block 1 IP addresses",                │
│          "ip_addresses": ["192.168.1.100"]                                  │
│        }                                                                     │
│      }                                                                       │
│    ],                                                                        │
│    "explanation": "Strategic goal approved...",                             │
│    "confidence": 0.95,                                                       │
│    "audit_trail": {                                                          │
│      "L1_strategic": {...},                                                  │
│      "L2_tactical": {...},                                                   │
│      "L3_operational": {...}                                                 │
│    }                                                                         │
│  }                                                                           │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Component Interaction Diagram

```
┌─────────────┐
│   Frontend  │ (Phase 2 - Coming Soon)
│   (React)   │
└──────┬──────┘
       │ HTTP Request
       ▼
┌─────────────────────────────────────────────┐
│         FastAPI Application                 │
│  ┌───────────────────────────────────────┐  │
│  │      Routes (routes.py)               │  │
│  │  • POST /api/v1/decision              │  │
│  │  • POST /api/v1/interpret             │  │
│  │  • GET  /api/v1/audit-logs            │  │
│  └───────────────────────────────────────┘  │
│  ┌───────────────────────────────────────┐  │
│  │    Middleware (middleware.py)         │  │
│  │  • Request logging                    │  │
│  │  • Error handling                     │  │
│  └───────────────────────────────────────┘  │
└──────────────────┬──────────────────────────┘
                   │
       ┌───────────┴───────────┐
       ▼                       ▼
┌──────────────┐      ┌──────────────────┐
│ Preprocessor │      │  Schema Validator│
│   (NLP)      │      │   (Pydantic)     │
└──────┬───────┘      └──────────────────┘
       │
       ▼
┌──────────────────────┐
│  LLM Interpreter     │
│  ┌────────────────┐  │
│  │ Gemini API     │  │ (if API key configured)
│  └────────────────┘  │
│  ┌────────────────┐  │
│  │ Mock Mode      │  │ (fallback/testing)
│  └────────────────┘  │
│  ┌────────────────┐  │
│  │ LLM → HRM      │  │ (converts to hierarchy)
│  │ Converter      │  │
│  └────────────────┘  │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│   HRM Engine         │
│  ┌────────────────┐  │
│  │ Simulation     │  │ (current mode)
│  │ Mode           │  │
│  └────────────────┘  │
│  ┌────────────────┐  │
│  │ Model Mode     │  │ (future: actual HRM)
│  │ (Future)       │  │
│  └────────────────┘  │
│                      │
│  Processes:          │
│  • L1 Strategic      │
│  • L2 Tactical       │
│  • L3 Operational    │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  Action Executor     │
│  ┌────────────────┐  │
│  │ Action         │  │
│  │ Registry       │  │
│  │ (20+ actions)  │  │
│  └────────────────┘  │
│  ┌────────────────┐  │
│  │ Dry-Run Mode   │  │ (default: safe)
│  └────────────────┘  │
│  ┌────────────────┐  │
│  │ Live Mode      │  │ (production)
│  └────────────────┘  │
│  ┌────────────────┐  │
│  │ Audit Logger   │  │
│  └────────────────┘  │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  Response to User    │
│  • Decision          │
│  • Actions           │
│  • Explanation       │
│  • Audit Trail       │
└──────────────────────┘
```

## File Structure Map

```
backend/
│
├── app/
│   ├── __init__.py
│   │
│   ├── main.py ⭐                     # FastAPI app entry point
│   │   └─> Creates app
│   │   └─> Includes routes
│   │   └─> Configures middleware
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes.py ⭐              # All API endpoints
│   │   │   └─> /api/v1/decision     (main pipeline)
│   │   │   └─> /api/v1/interpret    (LLM only)
│   │   │   └─> /api/v1/audit-logs   (monitoring)
│   │   │
│   │   └── middleware.py             # Request/response middleware
│   │       └─> Logging
│   │       └─> Error handling
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   │
│   │   ├── preprocessor.py ⭐        # NLP preprocessing
│   │   │   └─> Text normalization
│   │   │   └─> Time reference resolution
│   │   │   └─> Keyword extraction
│   │   │
│   │   ├── llm_interpreter.py ⭐    # Gemini/Mock LLM
│   │   │   └─> Natural language → Structured intent
│   │   │   └─> Intent classification
│   │   │   └─> LLM → HRM conversion
│   │   │
│   │   ├── hrm_engine.py ⭐          # HRM reasoning
│   │   │   └─> L1 Strategic reasoning
│   │   │   └─> L2 Tactical planning
│   │   │   └─> L3 Operational execution
│   │   │
│   │   ├── action_executor.py ⭐    # Action execution
│   │   │   └─> 20+ action handlers
│   │   │   └─> Dry-run mode
│   │   │   └─> Audit logging
│   │   │
│   │   └── schema_validator.py       # Validation logic
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── request_schema.py ⭐     # All Pydantic models
│   │       └─> UserRequest
│   │       └─> LLMOutput
│   │       └─> HRMInput (L1, L2, L3)
│   │       └─> DecisionOutput
│   │       └─> AuditLogEntry
│   │
│   └── utils/
│       └── (utility functions)
│
├── config/
│   └── (configuration files)
│
├── requirements.txt ⭐               # Python dependencies
├── .env.example                      # Environment template
├── test_system.py ⭐                 # Test script
└── README.md ⭐                      # API documentation
```

## Data Models

### UserRequest
```python
{
  "request_id": str,      # Auto-generated UUID
  "user_id": str,         # User identifier
  "timestamp": datetime,  # Request time
  "message": str,         # Natural language input
  "context": {            # Optional context
    "session_id": str,
    "user_role": str,
    "user_permissions": [str]
  }
}
```

### LLMOutput
```python
{
  "intent_type": enum,    # SECURITY, ACCESS, QUERY, etc.
  "goal": str,            # High-level goal
  "constraints": {...},   # Time, filters, thresholds
  "entities": {...},      # Targets, subjects, objects
  "requested_actions": [str],
  "confidence": float,    # 0.0 - 1.0
  "reasoning": str        # LLM explanation
}
```

### HRMInput (3-Level Hierarchy)
```python
{
  "L1_strategic": {
    "goal": str,
    "authorization_required": bool,
    "risk_level": enum,   # LOW, MEDIUM, HIGH, CRITICAL
    "priority": int       # 1-10
  },
  "L2_tactical": {
    "strategy": str,
    "policy": str,
    "subsystem": str,
    "constraints": [str]
  },
  "L3_operational": {
    "actions": [{
      "action": str,
      "params": dict,
      "conditions": [str],
      "fallback": str
    }],
    "execution_order": str  # sequential or parallel
  }
}
```

### DecisionOutput
```python
{
  "decision_id": str,
  "request_id": str,
  "status": enum,         # SUCCESS, DENIED, PARTIAL, PENDING
  "summary": str,
  "actions_completed": [...],
  "explanation": str,     # Human-readable explanation
  "confidence": float,
  "audit_trail": dict,    # Complete reasoning trace
  "timestamp": datetime
}
```

---

**Legend:**
- ⭐ = Core component
- → = Data flow direction
- ┌─┐ = Component boundary
- ▼ = Process step
