"""
Request and Response Schema Definitions for HRM Decision System

This module defines all Pydantic models for:
- Input Schema (User Request)
- LLM Output Schema (Structured Intent)
- HRM Input Schema (Hierarchical Levels)
- Output Schema (Decision)
- Audit Log Schema
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import uuid


# ============================================
# ENUMERATIONS
# ============================================

class IntentType(str, Enum):
    """Types of intents that can be extracted from user requests"""
    SECURITY = "SECURITY"
    COMPLIANCE = "COMPLIANCE"
    ACCESS = "ACCESS"
    SYSTEM = "SYSTEM"
    QUERY = "QUERY"


class RiskLevel(str, Enum):
    """Risk levels for strategic decisions"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class DecisionStatus(str, Enum):
    """Possible decision statuses"""
    SUCCESS = "SUCCESS"
    DENIED = "DENIED"
    PARTIAL = "PARTIAL"
    CONDITIONAL = "CONDITIONAL"
    PENDING = "PENDING"


# ============================================
# INPUT SCHEMA (User Request)
# ============================================

class RequestContext(BaseModel):
    """Context information for a user request"""
    session_id: Optional[str] = Field(default=None, description="Current session identifier")
    previous_requests: List[str] = Field(default_factory=list, description="List of previous request IDs")
    user_role: Optional[str] = Field(default=None, description="Role of the user making the request")
    user_permissions: List[str] = Field(default_factory=list, description="User's permissions")
    

class UserRequest(BaseModel):
    """Schema for incoming user requests"""
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique request identifier")
    user_id: str = Field(..., description="User identifier")
    timestamp: datetime = Field(default_factory=datetime.now, description="Request timestamp")
    message: str = Field(..., min_length=1, description="Natural language message from user")
    context: Optional[RequestContext] = Field(default=None, description="Additional context")

    class Config:
        json_schema_extra = {
            "example": {
                "request_id": "req-001",
                "user_id": "user-123",
                "timestamp": "2024-01-15T10:30:00Z",
                "message": "Block all suspicious IP addresses from the last 24 hours",
                "context": {
                    "session_id": "sess-456",
                    "previous_requests": [],
                    "user_role": "security_admin"
                }
            }
        }


# ============================================
# LLM OUTPUT SCHEMA (Structured Intent)
# ============================================

class Constraints(BaseModel):
    """Constraints extracted from user request"""
    time_window: Dict[str, Any] = Field(default_factory=dict, description="Time-based constraints")
    filters: Dict[str, Any] = Field(default_factory=dict, description="Filter conditions")
    thresholds: Dict[str, Any] = Field(default_factory=dict, description="Threshold values")


class Entities(BaseModel):
    """Entities extracted from user request"""
    targets: List[str] = Field(default_factory=list, description="Target entities (IPs, users, systems)")
    subjects: List[str] = Field(default_factory=list, description="Subject entities")
    objects: List[str] = Field(default_factory=list, description="Object entities")


class LLMOutput(BaseModel):
    """Schema for structured output from LLM interpretation"""
    intent_type: IntentType = Field(..., description="Classified intent type")
    goal: str = Field(..., description="High-level goal extracted from request")
    constraints: Constraints = Field(default_factory=Constraints, description="Request constraints")
    entities: Entities = Field(default_factory=Entities, description="Extracted entities")
    requested_actions: List[str] = Field(default_factory=list, description="List of actions to perform")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score (0-1)")
    reasoning: Optional[str] = Field(default=None, description="LLM reasoning for interpretation")

    @field_validator('confidence')
    @classmethod
    def validate_confidence(cls, v):
        if not 0 <= v <= 1:
            raise ValueError('Confidence must be between 0 and 1')
        return round(v, 4)


# ============================================
# HRM INPUT SCHEMA (Hierarchical Levels)
# ============================================

class StrategicLevel(BaseModel):
    """L1 Strategic Level - High-level goals and authorization"""
    goal: str = Field(..., description="Strategic goal")
    authorization_required: bool = Field(default=False, description="Whether authorization is needed")
    risk_level: RiskLevel = Field(default=RiskLevel.LOW, description="Risk assessment")
    priority: int = Field(default=1, ge=1, le=10, description="Priority level (1-10)")


class TacticalLevel(BaseModel):
    """L2 Tactical Level - Strategy and policy selection"""
    strategy: str = Field(..., description="Selected strategy")
    policy: str = Field(..., description="Applicable policy")
    subsystem: str = Field(..., description="Target subsystem")
    constraints: List[str] = Field(default_factory=list, description="Tactical constraints")


class OperationalAction(BaseModel):
    """Individual action at operational level"""
    action: str = Field(..., description="Action name")
    params: Dict[str, Any] = Field(default_factory=dict, description="Action parameters")
    conditions: List[str] = Field(default_factory=list, description="Pre-conditions")
    fallback: Optional[str] = Field(default=None, description="Fallback action if primary fails")


class OperationalLevel(BaseModel):
    """L3 Operational Level - Concrete actions"""
    actions: List[OperationalAction] = Field(default_factory=list, description="List of actions to execute")
    execution_order: str = Field(default="sequential", description="Execution order: sequential or parallel")


class HRMInput(BaseModel):
    """Complete HRM input with three hierarchical levels"""
    L1_strategic: StrategicLevel = Field(..., description="Strategic level")
    L2_tactical: TacticalLevel = Field(..., description="Tactical level")
    L3_operational: OperationalLevel = Field(..., description="Operational level")
    
    class Config:
        json_schema_extra = {
            "example": {
                "L1_strategic": {
                    "goal": "Block malicious IP addresses",
                    "authorization_required": True,
                    "risk_level": "MEDIUM",
                    "priority": 7
                },
                "L2_tactical": {
                    "strategy": "network_blocking",
                    "policy": "security_blocking_policy",
                    "subsystem": "firewall",
                    "constraints": ["max_blocks_per_hour: 100"]
                },
                "L3_operational": {
                    "actions": [
                        {
                            "action": "BLOCK_IP",
                            "params": {"ip_list": ["192.168.1.100"]},
                            "conditions": ["ip_not_whitelisted"]
                        }
                    ],
                    "execution_order": "sequential"
                }
            }
        }


# ============================================
# OUTPUT SCHEMA (Decision)
# ============================================

class CompletedAction(BaseModel):
    """Record of a completed action"""
    action: str = Field(..., description="Action name")
    status: str = Field(..., description="Action status")
    result: Dict[str, Any] = Field(default_factory=dict, description="Action result")
    timestamp: datetime = Field(default_factory=datetime.now, description="Completion timestamp")


class DecisionOutput(BaseModel):
    """Schema for decision output from HRM engine"""
    decision_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique decision identifier")
    request_id: str = Field(..., description="Original request ID")
    status: DecisionStatus = Field(..., description="Decision status")
    summary: str = Field(..., description="Human-readable summary")
    actions_completed: List[CompletedAction] = Field(default_factory=list, description="List of completed actions")
    explanation: str = Field(..., description="Detailed explanation of decision")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Decision confidence")
    audit_trail: Dict[str, Any] = Field(default_factory=dict, description="Audit information")
    timestamp: datetime = Field(default_factory=datetime.now, description="Decision timestamp")


# ============================================
# AUDIT LOG SCHEMA
# ============================================

class AuditLogEntry(BaseModel):
    """Schema for audit log entries"""
    log_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique log identifier")
    request_id: str = Field(..., description="Related request ID")
    decision_id: Optional[str] = Field(default=None, description="Related decision ID")
    timestamp: datetime = Field(default_factory=datetime.now, description="Log timestamp")
    event_type: str = Field(..., description="Type of event")
    actor: str = Field(..., description="User or system that triggered the event")
    action: str = Field(..., description="Action performed")
    details: Dict[str, Any] = Field(default_factory=dict, description="Additional details")
    outcome: str = Field(default="success", description="Outcome of the action")
    ip_address: Optional[str] = Field(default=None, description="Source IP address")
