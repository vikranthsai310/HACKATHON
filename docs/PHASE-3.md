# 📋 PHASE 3: HRM Engine & Decision Logic

## 🎯 Phase Overview

**Duration:** Week 3-4  
**Goal:** Implement the Hierarchical Reasoning Model engine for decision-making

---

## ✅ Deliverables

### 3.1 HRM Engine
- [ ] Implement L1 Strategic Validation
- [ ] Implement L2 Tactical Reasoning
- [ ] Implement L3 Operational Processing

### 3.2 Action Executor
- [ ] Create action whitelist
- [ ] Implement action handlers

### 3.3 Audit System
- [ ] Create audit logger
- [ ] Generate explanations

---

## 🔧 HRM Engine Implementation

**File: `backend/app/core/hrm_engine.py`**

```python
from typing import Dict, Any
from datetime import datetime
import uuid

class HRMEngine:
    """
    Hierarchical Reasoning Model Engine
    L1 Strategic → L2 Tactical → L3 Operational
    """
    
    ROLE_PERMISSIONS = {
        "admin": ["SECURITY", "COMPLIANCE", "ACCESS", "SYSTEM", "QUERY"],
        "security_analyst": ["SECURITY", "QUERY"],
        "user": ["QUERY"]
    }
    
    ACTION_ROLES = {
        "BLOCK_IP": ["admin", "security_analyst"],
        "GRANT_ACCESS": ["admin"],
        "SCAN": ["admin", "security_analyst"],
        "NOTIFY": ["admin", "security_analyst"],
        "ANALYZE": ["admin", "security_analyst", "user"]
    }
    
    def process(self, intent: Dict, user_context: Dict) -> Dict:
        decision_id = f"DEC-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6]}"
        
        # L1: Strategic Validation
        l1 = self._l1_strategic(intent, user_context)
        if l1["status"] == "DENIED":
            return self._build_response(decision_id, l1, intent)
        
        # L2: Tactical Reasoning
        l2 = self._l2_tactical(intent, l1)
        if l2["status"] == "DENIED":
            return self._build_response(decision_id, l2, intent, l1)
        
        # L3: Operational Processing
        l3 = self._l3_operational(intent, l1, l2)
        return self._build_response(decision_id, l3, intent, l1, l2)
    
    def _l1_strategic(self, intent: Dict, user_ctx: Dict) -> Dict:
        """Check goal and user authorization"""
        intent_type = intent.get("intent_type", "QUERY")
        user_role = user_ctx.get("role", "user")
        
        allowed = self.ROLE_PERMISSIONS.get(user_role, [])
        if intent_type not in allowed:
            return {"level": "L1", "status": "DENIED", 
                    "reason": f"Intent '{intent_type}' not allowed for '{user_role}'"}
        
        # Check action permissions
        actions = intent.get("requested_actions", [])
        authorized = []
        for action in actions:
            if user_role in self.ACTION_ROLES.get(action, ["admin"]):
                authorized.append(action)
        
        return {"level": "L1", "status": "APPROVED", 
                "authorized_actions": authorized, "reason": "Strategic check passed"}
    
    def _l2_tactical(self, intent: Dict, l1: Dict) -> Dict:
        """Select policy and strategy"""
        intent_type = intent.get("intent_type", "QUERY")
        
        policies = {
            "SECURITY": "POLICY_SEC_001",
            "COMPLIANCE": "POLICY_COMP_001",
            "ACCESS": "POLICY_ACC_001"
        }
        
        return {"level": "L2", "status": "APPROVED",
                "policy": policies.get(intent_type, "POLICY_DEFAULT"),
                "reason": "Tactical check passed"}
    
    def _l3_operational(self, intent: Dict, l1: Dict, l2: Dict) -> Dict:
        """Plan action execution"""
        actions = l1.get("authorized_actions", [])
        
        action_plan = []
        for action in actions:
            action_plan.append({
                "action": action,
                "status": "PLANNED",
                "params": intent.get("constraints", {})
            })
        
        return {"level": "L3", "status": "APPROVED",
                "action_plan": action_plan, "reason": "Actions planned"}
    
    def _build_response(self, dec_id: str, final: Dict, 
                        intent: Dict, l1: Dict = None, l2: Dict = None) -> Dict:
        return {
            "decision_id": dec_id,
            "timestamp": datetime.now().isoformat(),
            "status": "SUCCESS" if final["status"] == "APPROVED" else "DENIED",
            "summary": final["reason"],
            "hrm_trace": {
                "L1": l1["status"] if l1 else "N/A",
                "L2": l2["status"] if l2 else "N/A",
                "L3": final["status"]
            },
            "actions_planned": final.get("action_plan", []),
            "policy": l2.get("policy") if l2 else None
        }
```

---

## 🔧 Action Executor

**File: `backend/app/core/action_executor.py`**

```python
from typing import Dict, List
from datetime import datetime

class ActionExecutor:
    WHITELIST = ["BLOCK_IP", "NOTIFY", "SCAN", "FILTER", "ANALYZE", "GRANT_ACCESS", "LOG"]
    
    def execute(self, decision: Dict) -> Dict:
        if decision["status"] != "SUCCESS":
            return {"executed": False, "reason": "Decision denied"}
        
        results = []
        for action in decision.get("actions_planned", []):
            if action["action"] in self.WHITELIST:
                results.append({
                    "action": action["action"],
                    "status": "COMPLETED",
                    "timestamp": datetime.now().isoformat()
                })
        
        return {"executed": True, "results": results}
```

---

## ✅ Phase 3 Checklist

| Task | Status |
|------|--------|
| L1 Strategic | ⬜ |
| L2 Tactical | ⬜ |
| L3 Operational | ⬜ |
| Action Executor | ⬜ |
| Audit Logging | ⬜ |

---

## 🚀 Next: [PHASE-4.md](./PHASE-4.md) - Frontend Integration
