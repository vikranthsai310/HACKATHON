# 🧠 Hybrid Decision-Making System
## LLM-based NLP Interpreter + Hierarchical Reasoning Model (HRM)

<div align="center">

**A Revolutionary Approach to Safe, Explainable AI Decision Systems**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![AI](https://img.shields.io/badge/AI-Hybrid%20System-green.svg)](#)

</div>

---

## 📋 Table of Contents

1. [Core Idea](#-core-idea)
2. [Problem Statement](#-problem-statement)
3. [Proposed Solution](#-proposed-solution)
4. [System Architecture](#-system-architecture)
5. [Complete Input → Output Flow](#-complete-input--output-flow)
6. [Input Examples](#-input-examples)
7. [Output Examples](#-output-examples)
8. [Safety & Control Mechanisms](#-safety--control-mechanisms)
9. [Use Cases](#-use-cases)

---

## 🧠 Core Idea

> **1-Minute Understanding**

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│   Humans speak      →  Natural Language                        │
│   Machines require  →  Structured Logic                        │
│                                                                 │
│   LLM translates    →  Language → Structured Intent            │
│   HRM reasons over  →  Intent → Safe, Explainable Decisions    │
│                                                                 │
│   ❌ LLM does NOT decide                                        │
│   ❌ HRM does NOT understand language                           │
│                                                                 │
│   ✅ Together → Reliable AI Decision System                     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Role | What It Does | What It DOESN'T Do |
|-----------|------|--------------|-------------------|
| **LLM** | Translator | Understands language, extracts intent | Make decisions |
| **HRM** | Decision Engine | Applies logic, policies, rules | Understand language |
| **Schema Layer** | Validator | Prevents ambiguity | Process requests |
| **Audit Layer** | Logger | Ensures explainability | Execute actions |

---

## ❌ Problem Statement

### Why Pure LLMs Fail for Decision-Making

| Issue | Impact | Example |
|-------|--------|---------|
| 🎭 **Hallucinations** | Generates incorrect information | "Block IP 192.168.1.1" (IP doesn't exist) |
| ⚖️ **No Rule Compliance** | Cannot guarantee policy adherence | Blocks user without authorization |
| 🔄 **Inconsistent Answers** | Same query → different responses | Different risk scores for same threat |
| 📊 **Hard to Audit** | Black-box, no traceability | "Why was this decision made?" |
| 🔒 **Unsafe** | Cannot be trusted for critical systems | Auto-approves financial transaction |

### Why Rule-Only Systems Fail

| Issue | Impact | Example |
|-------|--------|---------|
| 🗣️ **No Language Understanding** | Requires structured input | User must know exact command syntax |
| 📏 **Rigid Interface** | Poor user experience | Error: "Invalid command format" |
| 💰 **High Configuration Cost** | Expensive to maintain rules | 1000s of if-else conditions |

---

## ✅ Proposed Solution

A **Hybrid AI System** combining the best of both worlds:

```
┌─────────────────────────────────────────────────────────────────────┐
│                       HYBRID DECISION SYSTEM                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   USER INPUT                    SYSTEM OUTPUT                       │
│   (Natural Language)            (Explainable Decision)              │
│         │                              ▲                            │
│         ▼                              │                            │
│   ┌───────────┐    ┌──────────┐    ┌───────────┐    ┌──────────┐   │
│   │    LLM    │───▶│  Schema  │───▶│    HRM    │───▶│  Action  │   │
│   │Interpreter│    │ Validator│    │  Engine   │    │ Executor │   │
│   └───────────┘    └──────────┘    └───────────┘    └──────────┘   │
│        │                                │                │          │
│        ▼                                ▼                ▼          │
│   Intent Extraction            Hierarchical         Deterministic   │
│   Entity Recognition           Reasoning            Execution       │
│   Semantic Parsing             Policy Validation    Audit Logging   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🏗️ System Architecture

### High-Level Flow

```
                        INPUT                              OUTPUT
                          │                                  ▲
                          ▼                                  │
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│  ┌──────────────┐                                                   │
│  │ User Request │  "Check for suspicious login attempts from       │
│  │   (Text)     │   foreign IPs yesterday and block if high risk"  │
│  └──────┬───────┘                                                   │
│         │                                                           │
│         ▼                                                           │
│  ┌──────────────────────────────────────────────────────────┐      │
│  │              NLP PREPROCESSING LAYER                      │      │
│  │  • Lowercasing                                            │      │
│  │  • Date resolution ("yesterday" → 2026-01-21)            │      │
│  │  • Keyword tagging                                        │      │
│  └──────────────────────────┬───────────────────────────────┘      │
│                             │                                       │
│                             ▼                                       │
│  ┌──────────────────────────────────────────────────────────┐      │
│  │                   LLM INTERPRETER                         │      │
│  │  • Extract intent                                         │      │
│  │  • Identify entities                                      │      │
│  │  • Map to HRM schema                                      │      │
│  │  • Output: Structured JSON                                │      │
│  └──────────────────────────┬───────────────────────────────┘      │
│                             │                                       │
│                             ▼                                       │
│  ┌──────────────────────────────────────────────────────────┐      │
│  │                 SCHEMA VALIDATOR                          │      │
│  │  • Validate JSON structure                                │      │
│  │  • Check required fields                                  │      │
│  │  • Reject invalid outputs                                 │      │
│  └──────────────────────────┬───────────────────────────────┘      │
│                             │                                       │
│                             ▼                                       │
│  ┌──────────────────────────────────────────────────────────┐      │
│  │           HIERARCHICAL REASONING MODEL (HRM)              │      │
│  │                                                           │      │
│  │   Level 1: STRATEGIC    → Goal Validation                │      │
│  │            ↓                                              │      │
│  │   Level 2: TACTICAL     → Policy Selection               │      │
│  │            ↓                                              │      │
│  │   Level 3: OPERATIONAL  → Action Reasoning               │      │
│  │                                                           │      │
│  └──────────────────────────┬───────────────────────────────┘      │
│                             │                                       │
│                             ▼                                       │
│  ┌──────────────────────────────────────────────────────────┐      │
│  │                  ACTION EXECUTOR                          │      │
│  │  • Execute approved actions                               │      │
│  │  • Update system state                                    │      │
│  │  • Generate audit logs                                    │      │
│  └──────────────────────────┬───────────────────────────────┘      │
│                             │                                       │
│                             ▼                                       │
│  ┌──────────────┐                                                   │
│  │   Response   │  Decision + Explanation + Audit Trail            │
│  │   (Output)   │                                                   │
│  └──────────────┘                                                   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🔁 Complete Input → Output Flow

### Step-by-Step Process

---

### 📥 STEP 1: User Input (Natural Language)

**Input:**
```
"Check for suspicious login attempts from foreign IPs yesterday and block them if risk is high."
```

**Characteristics:**
- ❓ Ambiguous ("foreign" is subjective)
- 📍 Contextual ("yesterday" needs resolution)
- ⚠️ Unsafe to act on directly

---

### 🧹 STEP 2: NLP Preprocessing

**Process:**
| Operation | Input | Output |
|-----------|-------|--------|
| Lowercasing | "Check for..." | "check for..." |
| Date Resolution | "yesterday" | "2026-01-21" |
| Keyword Tagging | "suspicious", "foreign" | `[SECURITY]`, `[GEO_FILTER]` |

**Preprocessed Output:**
```
check suspicious login attempts foreign IPs 2026-01-21 high risk
Tags: [SECURITY, GEO_FILTER, RISK_ASSESSMENT]
```

---

### 🤖 STEP 3: LLM Interpreter

> **Role:** Semantic Compiler (NOT Decision Maker)

**LLM Settings:**
- Temperature = 0 (deterministic)
- Output validated against schema
- Invalid output → REJECTED

**LLM Output (Structured JSON):**
```json
{
  "intent_type": "SECURITY_INVESTIGATION",
  "goal": "DETECT_AND_MITIGATE_LOGIN_ANOMALIES",
  "constraints": {
    "time_window": {
      "start": "2026-01-21T00:00:00",
      "end": "2026-01-21T23:59:59"
    },
    "ip_origin": "NON_LOCAL",
    "risk_threshold": "HIGH"
  },
  "requested_actions": [
    "BLOCK_SOURCE",
    "ALERT_ADMIN"
  ],
  "entities": {
    "target": "login_attempts",
    "filter": "foreign_ips"
  }
}
```

---

### ✅ STEP 4: Schema Validation

**Validation Checks:**
```
✓ intent_type is valid enum
✓ goal is non-empty string
✓ constraints.time_window has valid ISO dates
✓ constraints.risk_threshold is valid level
✓ requested_actions are whitelisted
```

**Result:** `VALID` → Proceed to HRM

---

### 🧠 STEP 5: HRM Processing

#### Level 1 — Strategic Goal Validation

**Input:**
```json
{
  "L1_GOAL": "SECURITY_RISK_MITIGATION"
}
```

**Validation:**
| Check | Status | Details |
|-------|--------|---------|
| Goal Allowed? | ✅ | In approved goal list |
| User Authorized? | ✅ | Has SECURITY_ADMIN role |
| System Ready? | ✅ | All services online |
| Read/Write? | ⚠️ | WRITE (requires approval) |

**L1 Output:** `APPROVED`

---

#### Level 2 — Tactical Strategy Selection

**Input:**
```json
{
  "L2_STRATEGY": "LOGIN_BEHAVIOR_ANALYSIS"
}
```

**Validation:**
| Check | Status | Details |
|-------|--------|---------|
| Subsystem? | ✅ | Security Monitoring |
| Detection Model? | ✅ | GeoIP + Anomaly Detection |
| Policy? | ✅ | POLICY_SEC_002 |
| Data Available? | ✅ | Logs from 2026-01-21 |

**L2 Output:** `STRATEGY_CONFIRMED`

---

#### Level 3 — Operational Reasoning

**Input:**
```json
{
  "L3_ACTIONS": [
    {
      "action": "FILTER_LOGS",
      "params": {
        "date": "2026-01-21",
        "geo": "NON_LOCAL"
      }
    },
    {
      "action": "CALCULATE_RISK_SCORE",
      "params": {
        "threshold": 0.75
      }
    },
    {
      "action": "CONDITIONAL_BLOCK",
      "condition": "risk_score > 0.75",
      "target": "source_ip"
    },
    {
      "action": "SEND_ALERT",
      "target": "ADMIN",
      "priority": "HIGH"
    }
  ]
}
```

**Execution Trace:**
```
[1] FILTER_LOGS
    → Scanned 15,847 log entries
    → Found 342 non-local login attempts
    → 23 flagged as suspicious

[2] CALCULATE_RISK_SCORE
    → IP 203.45.67.89: Risk = 0.91 ⚠️ HIGH
    → IP 185.23.45.12: Risk = 0.87 ⚠️ HIGH
    → IP 91.234.56.78: Risk = 0.82 ⚠️ HIGH
    → IP 178.90.12.34: Risk = 0.45 ✓ LOW

[3] CONDITIONAL_BLOCK
    → Condition: risk_score > 0.75
    → Blocked: 203.45.67.89, 185.23.45.12, 91.234.56.78
    → Total: 3 IPs blocked

[4] SEND_ALERT
    → Alert sent to: security-admin@company.com
    → Priority: HIGH
    → Status: DELIVERED
```

**L3 Output:** `ACTIONS_EXECUTED`

---

### 📤 STEP 6: Final Output

#### Decision Response

```json
{
  "status": "SUCCESS",
  "summary": "Analyzed 342 foreign login attempts from 2026-01-21. Blocked 3 high-risk IPs. Admin notified.",
  "details": {
    "logs_scanned": 15847,
    "suspicious_attempts": 342,
    "high_risk_ips": 3,
    "ips_blocked": [
      "203.45.67.89",
      "185.23.45.12",
      "91.234.56.78"
    ],
    "alert_sent": true
  }
}
```

#### Explanation (Human-Readable)

```
📊 DECISION SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Your request: "Check for suspicious login attempts from foreign 
              IPs yesterday and block them if risk is high."

✅ ACTIONS TAKEN:

1. Scanned 15,847 security log entries from January 21, 2026
2. Identified 342 login attempts from non-local IP addresses
3. Computed risk scores using GeoIP + Behavior Analysis
4. Blocked 3 IPs with risk score > 75%:
   • 203.45.67.89  (Risk: 91%) - Russia
   • 185.23.45.12  (Risk: 87%) - China
   • 91.234.56.78  (Risk: 82%) - Unknown
5. Sent HIGH priority alert to security admin

⚖️ POLICY APPLIED: POLICY_SEC_002 (Auto-block high-risk foreign IPs)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

#### Audit Log

```json
{
  "decision_id": "DEC-2026-01-22-98127",
  "timestamp": "2026-01-22T20:40:00Z",
  "user_request": "Check for suspicious login attempts from foreign IPs yesterday and block them if risk is high.",
  "intent_parsed": "SECURITY_INVESTIGATION",
  "goal": "DETECT_AND_MITIGATE_LOGIN_ANOMALIES",
  "hrm_levels": {
    "L1_strategic": "APPROVED",
    "L2_tactical": "STRATEGY_CONFIRMED",
    "L3_operational": "ACTIONS_EXECUTED"
  },
  "actions_taken": [
    "FILTER_LOGS",
    "CALCULATE_RISK_SCORE",
    "BLOCK_IP:203.45.67.89",
    "BLOCK_IP:185.23.45.12",
    "BLOCK_IP:91.234.56.78",
    "SEND_ALERT:ADMIN"
  ],
  "rules_triggered": [
    "FOREIGN_IP_HIGH_RISK",
    "FAILED_LOGIN_THRESHOLD",
    "GEO_ANOMALY_DETECTED"
  ],
  "policy_applied": "POLICY_SEC_002",
  "decision_path": "L1→L2→L3→EXECUTE",
  "execution_time_ms": 1247,
  "user_id": "admin@company.com",
  "session_id": "sess_abc123xyz"
}
```

---

## 📥 Input Examples

### Example 1: Security Investigation

**Input:**
```
"Find all failed SSH attempts in the last hour and notify the security team"
```

**Parsed Intent:**
```json
{
  "intent_type": "SECURITY_MONITORING",
  "goal": "DETECT_FAILED_SSH_ATTEMPTS",
  "constraints": {
    "time_window": "LAST_1_HOUR",
    "event_type": "SSH_FAILED"
  },
  "requested_actions": ["NOTIFY_SECURITY_TEAM"]
}
```

---

### Example 2: Financial Compliance

**Input:**
```
"Review transactions over $10,000 today and flag any that violate AML policy"
```

**Parsed Intent:**
```json
{
  "intent_type": "COMPLIANCE_CHECK",
  "goal": "AML_VIOLATION_DETECTION",
  "constraints": {
    "time_window": "TODAY",
    "amount_threshold": 10000,
    "currency": "USD",
    "policy": "AML"
  },
  "requested_actions": ["FLAG_VIOLATIONS", "GENERATE_REPORT"]
}
```

---

### Example 3: Access Control

**Input:**
```
"Grant John Smith read access to the Q4 financial reports"
```

**Parsed Intent:**
```json
{
  "intent_type": "ACCESS_MANAGEMENT",
  "goal": "GRANT_ACCESS",
  "constraints": {
    "user": "john.smith@company.com",
    "permission_level": "READ",
    "resource": "Q4_FINANCIAL_REPORTS"
  },
  "requested_actions": ["GRANT_PERMISSION", "LOG_ACCESS_CHANGE"]
}
```

---

### Example 4: System Maintenance

**Input:**
```
"Schedule database backup for tonight at 2 AM if server load is below 30%"
```

**Parsed Intent:**
```json
{
  "intent_type": "SYSTEM_MAINTENANCE",
  "goal": "SCHEDULE_BACKUP",
  "constraints": {
    "scheduled_time": "02:00",
    "condition": {
      "metric": "server_load",
      "operator": "LESS_THAN",
      "value": 30
    }
  },
  "requested_actions": ["SCHEDULE_TASK", "SET_CONDITION"]
}
```

---

## 📤 Output Examples

### Example 1: Successful Execution

```json
{
  "status": "SUCCESS",
  "decision_id": "DEC-2026-01-22-00142",
  "summary": "Access granted to John Smith for Q4 Financial Reports",
  "actions_completed": [
    {
      "action": "GRANT_PERMISSION",
      "target": "john.smith@company.com",
      "resource": "Q4_FINANCIAL_REPORTS",
      "permission": "READ",
      "status": "COMPLETED"
    },
    {
      "action": "LOG_ACCESS_CHANGE",
      "status": "COMPLETED"
    }
  ],
  "explanation": "User john.smith@company.com now has READ access to Q4 financial reports. This action was logged and the user has been notified."
}
```

---

### Example 2: Conditional Approval

```json
{
  "status": "CONDITIONAL_APPROVAL",
  "decision_id": "DEC-2026-01-22-00143",
  "summary": "Database backup scheduled with conditions",
  "conditions": [
    {
      "condition": "server_load < 30%",
      "check_time": "2026-01-23T02:00:00Z",
      "fallback": "RESCHEDULE_TO_NEXT_NIGHT"
    }
  ],
  "scheduled_task": {
    "task": "DATABASE_BACKUP",
    "scheduled_time": "2026-01-23T02:00:00Z",
    "conditional": true
  },
  "explanation": "Backup scheduled for 2:00 AM. Will only execute if server load is below 30%. Otherwise, will be rescheduled."
}
```

---

### Example 3: Request Denied

```json
{
  "status": "DENIED",
  "decision_id": "DEC-2026-01-22-00144",
  "summary": "Request denied due to policy violation",
  "reason": {
    "code": "POLICY_VIOLATION",
    "policy": "DATA_ACCESS_POLICY_001",
    "details": "User does not have clearance for classified financial documents"
  },
  "hrm_trace": {
    "L1_strategic": "APPROVED",
    "L2_tactical": "DENIED",
    "failure_point": "Authorization check failed"
  },
  "explanation": "The requested access to classified financial documents requires FINANCE_ADMIN role. Current user has FINANCE_VIEWER role only. Please contact your supervisor for elevated access."
}
```

---

### Example 4: Partial Success

```json
{
  "status": "PARTIAL_SUCCESS",
  "decision_id": "DEC-2026-01-22-00145",
  "summary": "3 of 5 requested actions completed",
  "actions": [
    {"action": "SCAN_LOGS", "status": "COMPLETED"},
    {"action": "IDENTIFY_THREATS", "status": "COMPLETED"},
    {"action": "BLOCK_IPS", "status": "COMPLETED"},
    {"action": "NOTIFY_ADMIN", "status": "FAILED", "reason": "Email service unavailable"},
    {"action": "UPDATE_FIREWALL", "status": "FAILED", "reason": "Firewall API timeout"}
  ],
  "retry_scheduled": true,
  "retry_time": "2026-01-22T21:00:00Z",
  "explanation": "Threat mitigation actions completed. Notification and firewall update failed due to service issues. Retry scheduled in 20 minutes."
}
```

---

## 🔒 Safety & Control Mechanisms

### Multi-Layer Protection

```
┌─────────────────────────────────────────────────────────────────┐
│                     SAFETY ARCHITECTURE                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  LAYER 1: LLM CONTROLS                                          │
│  ├─ Temperature = 0 (deterministic)                             │
│  ├─ Output schema validation                                    │
│  └─ No decision authority                                       │
│                                                                 │
│  LAYER 2: SCHEMA VALIDATION                                     │
│  ├─ JSON schema enforcement                                     │
│  ├─ Required field checks                                       │
│  └─ Value range validation                                      │
│                                                                 │
│  LAYER 3: HRM POLICY ENGINE                                     │
│  ├─ Authorization verification                                  │
│  ├─ Policy compliance checks                                    │
│  └─ State consistency validation                                │
│                                                                 │
│  LAYER 4: ACTION WHITELIST                                      │
│  ├─ Only approved actions execute                               │
│  ├─ Rate limiting                                               │
│  └─ Scope restrictions                                          │
│                                                                 │
│  LAYER 5: AUDIT TRAIL                                           │
│  ├─ Immutable logs                                              │
│  ├─ Full decision traceability                                  │
│  └─ Regulatory compliance                                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Rejection Scenarios

| Scenario | Layer | Response |
|----------|-------|----------|
| Invalid JSON from LLM | Schema Validation | "Request parsing failed. Please rephrase." |
| Unauthorized action | HRM L1 | "You don't have permission for this action." |
| Policy violation | HRM L2 | "This request violates policy X. Denied." |
| Action not whitelisted | Action Executor | "Requested action is not available." |
| Rate limit exceeded | Action Executor | "Too many requests. Please wait." |

---

## 🎯 Use Cases

| Domain | Application | Example Input |
|--------|-------------|---------------|
| 🔐 **Security** | SIEM/SOC | "Block all IPs from country X with failed logins" |
| 🏢 **Enterprise** | Workflow Automation | "Approve all pending invoices under $500" |
| 🗳️ **Governance** | Policy Enforcement | "Flag any votes that violate procedure" |
| 💰 **Finance** | Compliance | "Review transactions for suspicious patterns" |
| 🏥 **Healthcare** | Clinical Support | "Alert if patient vitals exceed thresholds" |
| 🏭 **Manufacturing** | Quality Control | "Stop production line if defect rate > 2%" |

---

## 🧠 Summary

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│   📥 INPUT                          📤 OUTPUT                   │
│   Natural Language      →→→→→→→     Structured Decision        │
│   "Block suspicious IPs"            + Explanation               │
│                                     + Audit Trail               │
│                                                                 │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │                                                         │   │
│   │   LLM UNDERSTANDS what the user wants                   │   │
│   │                        ↓                                │   │
│   │   HRM DECIDES what the system should do                 │   │
│   │                        ↓                                │   │
│   │   TOGETHER → Safe, Explainable AI Decisions             │   │
│   │                                                         │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

<div align="center">

**Built for Safe, Explainable AI Decision Systems**

*Where Language Meets Logic*

</div>
