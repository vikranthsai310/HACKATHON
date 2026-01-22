"""
Decision API Endpoints for HRM Decision System

Provides comprehensive API endpoints for:
- Full decision pipeline
- Individual component access
- Audit trail retrieval
- Decision history and analytics
- Batch processing
"""

from fastapi import APIRouter, HTTPException, Query, Path, Body
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from enum import Enum
import uuid
import json
import asyncio
import logging

from ..schemas.request_schema import (
    UserRequest,
    RequestContext,
    LLMOutput,
    HRMInput,
    DecisionOutput,
    DecisionStatus,
    StrategicLevel,
    TacticalLevel,
    OperationalLevel,
    OperationalAction,
    RiskLevel,
    AuditLogEntry
)
from ..core.preprocessor import NLPPreprocessor
from ..core.llm_interpreter import LLMInterpreter
from ..core.hrm_engine import HRMEngine
from ..core.action_executor import ActionExecutor
from ..core.audit_logger import (
    AuditLogger,
    AuditEventType,
    AuditSeverity,
    AuditEntry,
    AuditSummary,
    get_audit_logger
)

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/decision", tags=["Decision"])

# Initialize components
preprocessor = NLPPreprocessor()
llm_interpreter = LLMInterpreter()
hrm_engine = HRMEngine(use_simulation=True)
action_executor = ActionExecutor(dry_run=True)
audit_logger = get_audit_logger()


# ==========================================
# REQUEST/RESPONSE MODELS
# ==========================================

class QuickDecisionRequest(BaseModel):
    """Simplified request for quick decisions"""
    message: str = Field(..., description="Natural language request", min_length=1)
    user_id: str = Field(default="anonymous", description="User identifier")
    user_role: str = Field(default="user", description="User role for authorization")
    dry_run: bool = Field(default=True, description="Execute in dry-run mode")


class BatchDecisionRequest(BaseModel):
    """Request for batch decision processing"""
    requests: List[QuickDecisionRequest] = Field(..., description="List of decision requests")
    parallel: bool = Field(default=False, description="Process in parallel")


class DecisionHistoryResponse(BaseModel):
    """Response for decision history"""
    total: int
    decisions: List[Dict[str, Any]]
    page: int
    page_size: int


class DecisionAnalytics(BaseModel):
    """Analytics for decisions"""
    total_decisions: int
    status_breakdown: Dict[str, int]
    average_duration_ms: Optional[float]
    risk_breakdown: Dict[str, int]
    action_breakdown: Dict[str, int]
    time_range: Dict[str, str]


class ExplanationRequest(BaseModel):
    """Request for detailed explanation"""
    decision_id: str = Field(..., description="Decision ID to explain")
    detail_level: str = Field(default="full", description="Detail level: brief, standard, full")


class ExplanationResponse(BaseModel):
    """Detailed explanation of a decision"""
    decision_id: str
    summary: str
    strategic_explanation: str
    tactical_explanation: str
    operational_explanation: str
    risk_assessment: str
    recommendations: List[str]


# ==========================================
# IN-MEMORY DECISION STORAGE
# ==========================================

_decision_store: Dict[str, DecisionOutput] = {}
_decision_metadata: Dict[str, Dict[str, Any]] = {}


def store_decision(decision: DecisionOutput, user_id: str, message: str):
    """Store decision for history and retrieval"""
    _decision_store[decision.decision_id] = decision
    _decision_metadata[decision.decision_id] = {
        "user_id": user_id,
        "message": message,
        "created_at": datetime.now().isoformat()
    }


def get_stored_decision(decision_id: str) -> Optional[DecisionOutput]:
    """Retrieve stored decision"""
    return _decision_store.get(decision_id)


# ==========================================
# MAIN DECISION ENDPOINTS
# ==========================================

@router.post("/process", response_model=DecisionOutput)
async def process_decision(request: UserRequest):
    """
    Process a complete decision request through the full pipeline
    
    Pipeline:
    1. Preprocess natural language input
    2. LLM interpretation → structured intent
    3. Convert to HRM hierarchical format
    4. HRM reasoning → decision
    5. Execute actions (if approved and not dry-run)
    6. Return decision with audit trail
    """
    
    start_time = datetime.now()
    
    # Log request received
    audit_logger.log_request_received(
        request_id=request.request_id,
        user_id=request.user_id,
        message=request.message,
        session_id=request.context.session_id if request.context else None,
        user_role=request.context.user_role if request.context else None
    )
    
    try:
        logger.info(f"Processing decision request {request.request_id}")
        
        # Step 1: Preprocess
        preprocessed_data = preprocessor.preprocess(request.message)
        
        # Step 2: LLM Interpretation
        llm_output = llm_interpreter.interpret(request, preprocessed_data)
        
        # Step 3: Convert to HRM Input
        hrm_input = llm_interpreter.llm_to_hrm_input(llm_output, request)
        
        # Log decision started
        audit_logger.log_decision_started(
            request_id=request.request_id,
            decision_id="pending",
            goal=hrm_input.L1_strategic.goal,
            risk_level=hrm_input.L1_strategic.risk_level.value
        )
        
        # Step 4: HRM Reasoning
        decision = hrm_engine.process(hrm_input, request.request_id)
        
        # Log HRM levels
        audit_logger.log_l1_strategic(
            request_id=request.request_id,
            decision_id=decision.decision_id,
            goal=hrm_input.L1_strategic.goal,
            risk_level=hrm_input.L1_strategic.risk_level.value,
            priority=hrm_input.L1_strategic.priority,
            approved=decision.status != DecisionStatus.DENIED
        )
        
        audit_logger.log_l2_tactical(
            request_id=request.request_id,
            decision_id=decision.decision_id,
            strategy=hrm_input.L2_tactical.strategy,
            policy=hrm_input.L2_tactical.policy,
            subsystem=hrm_input.L2_tactical.subsystem
        )
        
        audit_logger.log_l3_operational(
            request_id=request.request_id,
            decision_id=decision.decision_id,
            actions=[a.action for a in hrm_input.L3_operational.actions],
            execution_order=hrm_input.L3_operational.execution_order
        )
        
        # Step 5: Execute Actions
        if decision.status != DecisionStatus.DENIED:
            decision = action_executor.execute_decision(decision, request.user_id)
            
            # Log action results
            for action in decision.actions_completed:
                audit_logger.log_action_executed(
                    request_id=request.request_id,
                    decision_id=decision.decision_id,
                    action_name=action.action,
                    params=action.result.get("params", {}),
                    outcome="success" if action.status == "SUCCESS" else "failure",
                    result=action.result
                )
        
        # Calculate duration
        duration_ms = (datetime.now() - start_time).total_seconds() * 1000
        
        # Log decision completed
        audit_logger.log_decision_completed(
            request_id=request.request_id,
            decision_id=decision.decision_id,
            status=decision.status.value,
            summary=decision.summary,
            duration_ms=duration_ms
        )
        
        # Store decision for history
        store_decision(decision, request.user_id, request.message)
        
        logger.info(f"Decision {decision.decision_id} completed: {decision.status}")
        
        return decision
        
    except Exception as e:
        logger.error(f"Error processing decision: {e}")
        
        audit_logger.log_error(
            action="process_decision",
            error_message=str(e),
            request_id=request.request_id
        )
        
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/quick", response_model=DecisionOutput)
async def quick_decision(request: QuickDecisionRequest):
    """
    Quick decision endpoint with simplified input
    
    Automatically constructs UserRequest from minimal input
    """
    
    # Build full request
    user_request = UserRequest(
        user_id=request.user_id,
        message=request.message,
        context=RequestContext(
            user_role=request.user_role
        )
    )
    
    # Set executor mode
    action_executor.dry_run = request.dry_run
    
    return await process_decision(user_request)


@router.post("/batch", response_model=List[DecisionOutput])
async def batch_decisions(batch_request: BatchDecisionRequest):
    """
    Process multiple decision requests in batch
    
    Can process sequentially or in parallel
    """
    
    results = []
    
    if batch_request.parallel:
        # Process in parallel
        tasks = [
            quick_decision(req) for req in batch_request.requests
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Convert exceptions to error responses
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    "error": str(result),
                    "request_index": i
                })
            else:
                processed_results.append(result)
        return processed_results
    else:
        # Process sequentially
        for req in batch_request.requests:
            try:
                result = await quick_decision(req)
                results.append(result)
            except Exception as e:
                # Continue processing other requests
                logger.error(f"Batch request failed: {e}")
    
    return results


@router.post("/stream")
async def stream_decision(request: QuickDecisionRequest):
    """
    Stream decision processing with real-time updates
    
    Returns Server-Sent Events for each processing step
    """
    
    async def generate_events():
        start_time = datetime.now()
        
        # Build request
        user_request = UserRequest(
            user_id=request.user_id,
            message=request.message,
            context=RequestContext(user_role=request.user_role)
        )
        
        try:
            # Step 1: Preprocess
            yield f"data: {json.dumps({'step': 1, 'name': 'preprocessing', 'status': 'started'})}\n\n"
            preprocessed = preprocessor.preprocess(request.message)
            yield f"data: {json.dumps({'step': 1, 'name': 'preprocessing', 'status': 'completed'})}\n\n"
            
            # Step 2: LLM Interpretation
            yield f"data: {json.dumps({'step': 2, 'name': 'interpretation', 'status': 'started'})}\n\n"
            llm_output = llm_interpreter.interpret(user_request, preprocessed)
            yield f"data: {json.dumps({'step': 2, 'name': 'interpretation', 'status': 'completed', 'intent_type': llm_output.intent_type.value})}\n\n"
            
            # Step 3: HRM Conversion
            yield f"data: {json.dumps({'step': 3, 'name': 'hrm_conversion', 'status': 'started'})}\n\n"
            hrm_input = llm_interpreter.llm_to_hrm_input(llm_output, user_request)
            yield f"data: {json.dumps({'step': 3, 'name': 'hrm_conversion', 'status': 'completed', 'goal': hrm_input.L1_strategic.goal})}\n\n"
            
            # Step 4: L1 Strategic
            yield f"data: {json.dumps({'step': 4, 'name': 'l1_strategic', 'status': 'started'})}\n\n"
            await asyncio.sleep(0.1)  # Simulate processing
            yield f"data: {json.dumps({'step': 4, 'name': 'l1_strategic', 'status': 'completed', 'risk_level': hrm_input.L1_strategic.risk_level.value})}\n\n"
            
            # Step 5: L2 Tactical
            yield f"data: {json.dumps({'step': 5, 'name': 'l2_tactical', 'status': 'started'})}\n\n"
            await asyncio.sleep(0.1)
            yield f"data: {json.dumps({'step': 5, 'name': 'l2_tactical', 'status': 'completed', 'strategy': hrm_input.L2_tactical.strategy})}\n\n"
            
            # Step 6: L3 Operational
            yield f"data: {json.dumps({'step': 6, 'name': 'l3_operational', 'status': 'started'})}\n\n"
            decision = hrm_engine.process(hrm_input, user_request.request_id)
            yield f"data: {json.dumps({'step': 6, 'name': 'l3_operational', 'status': 'completed', 'actions': len(decision.actions_completed)})}\n\n"
            
            # Step 7: Execution
            if decision.status != DecisionStatus.DENIED:
                yield f"data: {json.dumps({'step': 7, 'name': 'execution', 'status': 'started'})}\n\n"
                action_executor.dry_run = request.dry_run
                decision = action_executor.execute_decision(decision, user_request.user_id)
                yield f"data: {json.dumps({'step': 7, 'name': 'execution', 'status': 'completed'})}\n\n"
            
            # Final result
            duration_ms = (datetime.now() - start_time).total_seconds() * 1000
            store_decision(decision, user_request.user_id, request.message)
            
            yield f"data: {json.dumps({'step': 'final', 'decision': decision.model_dump(), 'duration_ms': duration_ms})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return StreamingResponse(
        generate_events(),
        media_type="text/event-stream"
    )


# ==========================================
# DECISION RETRIEVAL ENDPOINTS
# ==========================================

@router.get("/{decision_id}", response_model=DecisionOutput)
async def get_decision(
    decision_id: str = Path(..., description="Decision ID to retrieve")
):
    """Get a specific decision by ID"""
    
    decision = get_stored_decision(decision_id)
    
    if not decision:
        raise HTTPException(status_code=404, detail=f"Decision {decision_id} not found")
    
    return decision


@router.get("/{decision_id}/explain", response_model=ExplanationResponse)
async def explain_decision(
    decision_id: str = Path(..., description="Decision ID to explain"),
    detail_level: str = Query(default="full", description="Detail level: brief, standard, full")
):
    """Get detailed explanation of a decision"""
    
    decision = get_stored_decision(decision_id)
    
    if not decision:
        raise HTTPException(status_code=404, detail=f"Decision {decision_id} not found")
    
    # Build explanation
    audit_trail = decision.audit_trail
    
    strategic_explanation = (
        f"Goal: {audit_trail.get('L1_strategic', {}).get('goal', 'N/A')}\n"
        f"Risk Level: {audit_trail.get('L1_strategic', {}).get('risk_level', 'N/A')}\n"
        f"Priority: {audit_trail.get('L1_strategic', {}).get('priority', 'N/A')}/10"
    )
    
    tactical_explanation = (
        f"Strategy: {audit_trail.get('L2_tactical', {}).get('strategy', 'N/A')}\n"
        f"Policy: {audit_trail.get('L2_tactical', {}).get('policy', 'N/A')}\n"
        f"Target Subsystem: {audit_trail.get('L2_tactical', {}).get('subsystem', 'N/A')}"
    )
    
    operational_explanation = (
        f"Total Actions: {audit_trail.get('L3_operational', {}).get('total_actions', 0)}\n"
        f"Successful: {audit_trail.get('L3_operational', {}).get('successful_actions', 0)}\n"
        f"Actions: {', '.join(audit_trail.get('L3_operational', {}).get('actions', []))}"
    )
    
    risk_assessment = _generate_risk_assessment(decision)
    recommendations = _generate_recommendations(decision)
    
    return ExplanationResponse(
        decision_id=decision_id,
        summary=decision.summary,
        strategic_explanation=strategic_explanation,
        tactical_explanation=tactical_explanation,
        operational_explanation=operational_explanation,
        risk_assessment=risk_assessment,
        recommendations=recommendations
    )


@router.get("/{decision_id}/audit-trail")
async def get_decision_audit_trail(
    decision_id: str = Path(..., description="Decision ID")
):
    """Get complete audit trail for a decision"""
    
    entries = audit_logger.get_decision_trail(decision_id)
    
    return {
        "decision_id": decision_id,
        "entry_count": len(entries),
        "entries": [e.to_dict() for e in entries]
    }


# ==========================================
# HISTORY & ANALYTICS ENDPOINTS
# ==========================================

@router.get("/history/list", response_model=DecisionHistoryResponse)
async def list_decisions(
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=20, ge=1, le=100, description="Page size"),
    status: Optional[str] = Query(default=None, description="Filter by status"),
    user_id: Optional[str] = Query(default=None, description="Filter by user ID")
):
    """List decision history with pagination and filters"""
    
    decisions = list(_decision_store.values())
    
    # Apply filters
    if status:
        decisions = [d for d in decisions if d.status.value == status]
    
    if user_id:
        decisions = [
            d for d in decisions 
            if _decision_metadata.get(d.decision_id, {}).get("user_id") == user_id
        ]
    
    # Sort by timestamp (newest first)
    decisions.sort(key=lambda d: d.timestamp, reverse=True)
    
    # Paginate
    total = len(decisions)
    start = (page - 1) * page_size
    end = start + page_size
    page_decisions = decisions[start:end]
    
    return DecisionHistoryResponse(
        total=total,
        decisions=[d.model_dump() for d in page_decisions],
        page=page,
        page_size=page_size
    )


@router.get("/analytics/summary", response_model=DecisionAnalytics)
async def get_decision_analytics(
    hours: int = Query(default=24, ge=1, le=720, description="Time range in hours")
):
    """Get analytics summary for decisions"""
    
    cutoff = datetime.now() - timedelta(hours=hours)
    
    decisions = [
        d for d in _decision_store.values()
        if d.timestamp >= cutoff
    ]
    
    if not decisions:
        return DecisionAnalytics(
            total_decisions=0,
            status_breakdown={},
            average_duration_ms=None,
            risk_breakdown={},
            action_breakdown={},
            time_range={"start": cutoff.isoformat(), "end": datetime.now().isoformat()}
        )
    
    # Calculate breakdowns
    status_breakdown: Dict[str, int] = {}
    risk_breakdown: Dict[str, int] = {}
    action_breakdown: Dict[str, int] = {}
    
    for d in decisions:
        # Status
        status_breakdown[d.status.value] = status_breakdown.get(d.status.value, 0) + 1
        
        # Risk level
        risk = d.audit_trail.get("L1_strategic", {}).get("risk_level", "UNKNOWN")
        risk_breakdown[risk] = risk_breakdown.get(risk, 0) + 1
        
        # Actions
        for action in d.actions_completed:
            action_breakdown[action.action] = action_breakdown.get(action.action, 0) + 1
    
    return DecisionAnalytics(
        total_decisions=len(decisions),
        status_breakdown=status_breakdown,
        average_duration_ms=None,  # Would need to track this
        risk_breakdown=risk_breakdown,
        action_breakdown=action_breakdown,
        time_range={"start": cutoff.isoformat(), "end": datetime.now().isoformat()}
    )


# ==========================================
# AUDIT ENDPOINTS
# ==========================================

@router.get("/audit/entries")
async def get_audit_entries(
    request_id: Optional[str] = Query(default=None),
    decision_id: Optional[str] = Query(default=None),
    event_type: Optional[str] = Query(default=None),
    severity: Optional[str] = Query(default=None),
    user_id: Optional[str] = Query(default=None),
    outcome: Optional[str] = Query(default=None),
    limit: int = Query(default=100, ge=1, le=1000)
):
    """Get filtered audit log entries"""
    
    # Convert string to enum if provided
    event_type_enum = AuditEventType(event_type) if event_type else None
    severity_enum = AuditSeverity(severity) if severity else None
    
    entries = audit_logger.get_entries(
        request_id=request_id,
        decision_id=decision_id,
        event_type=event_type_enum,
        severity=severity_enum,
        user_id=user_id,
        outcome=outcome,
        limit=limit
    )
    
    return {
        "count": len(entries),
        "entries": [e.to_dict() for e in entries]
    }


@router.get("/audit/summary")
async def get_audit_summary(
    hours: int = Query(default=24, ge=1, le=720, description="Time range in hours")
):
    """Get audit log summary"""
    
    start_time = datetime.now() - timedelta(hours=hours)
    summary = audit_logger.get_summary(start_time=start_time)
    
    return {
        "total_entries": summary.total_entries,
        "entries_by_type": summary.entries_by_type,
        "entries_by_severity": summary.entries_by_severity,
        "entries_by_outcome": summary.entries_by_outcome,
        "time_range_start": summary.time_range_start,
        "time_range_end": summary.time_range_end,
        "unique_users": summary.unique_users,
        "unique_sessions": summary.unique_sessions,
        "average_duration_ms": summary.average_duration_ms,
        "error_rate": summary.error_rate
    }


@router.get("/audit/export")
async def export_audit_logs(
    format: str = Query(default="json", description="Export format: json, csv"),
    hours: int = Query(default=24, ge=1, le=720, description="Time range in hours")
):
    """Export audit logs"""
    
    start_time = datetime.now() - timedelta(hours=hours)
    
    exported = audit_logger.export_entries(
        format=format,
        start_time=start_time
    )
    
    if format == "csv":
        return StreamingResponse(
            iter([exported]),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=audit_logs.csv"}
        )
    
    return {"format": format, "data": json.loads(exported)}


@router.delete("/audit/clear")
async def clear_audit_logs(
    hours: Optional[int] = Query(default=None, description="Clear entries older than N hours")
):
    """Clear audit logs"""
    
    if hours:
        before = datetime.now() - timedelta(hours=hours)
        audit_logger.clear(before=before)
        return {"message": f"Cleared audit entries older than {hours} hours"}
    else:
        audit_logger.clear()
        return {"message": "All audit entries cleared"}


# ==========================================
# CONFIGURATION ENDPOINTS
# ==========================================

@router.get("/config/status")
async def get_config_status():
    """Get current configuration status"""
    
    return {
        "hrm_engine": {
            "mode": "SIMULATION" if hrm_engine.use_simulation else "MODEL",
            "device": hrm_engine.device
        },
        "action_executor": {
            "mode": "DRY-RUN" if action_executor.dry_run else "LIVE"
        },
        "llm_interpreter": {
            "mode": "MOCK" if llm_interpreter.use_mock else "GEMINI",
            "model": llm_interpreter.model_name if not llm_interpreter.use_mock else None
        },
        "audit_logger": {
            "max_entries": audit_logger.max_entries,
            "retention_hours": audit_logger.retention_hours
        }
    }


@router.post("/config/dry-run")
async def set_dry_run_mode(enabled: bool = Body(..., embed=True)):
    """Set dry-run mode for action executor"""
    
    action_executor.dry_run = enabled
    
    audit_logger.log(
        event_type=AuditEventType.CONFIGURATION_CHANGE,
        action="set_dry_run_mode",
        action_params={"enabled": enabled}
    )
    
    return {
        "dry_run": enabled,
        "message": f"Dry-run mode {'enabled' if enabled else 'disabled'}"
    }


# ==========================================
# HELPER FUNCTIONS
# ==========================================

def _generate_risk_assessment(decision: DecisionOutput) -> str:
    """Generate risk assessment text"""
    
    risk_level = decision.audit_trail.get("L1_strategic", {}).get("risk_level", "UNKNOWN")
    
    assessments = {
        "LOW": "This decision involves low-risk operations with minimal impact.",
        "MEDIUM": "This decision involves moderate risk. Standard precautions apply.",
        "HIGH": "This decision involves high-risk operations. Careful monitoring recommended.",
        "CRITICAL": "CRITICAL: This decision involves critical operations. Full review required."
    }
    
    return assessments.get(risk_level, "Risk level could not be determined.")


def _generate_recommendations(decision: DecisionOutput) -> List[str]:
    """Generate recommendations based on decision"""
    
    recommendations = []
    
    if decision.status == DecisionStatus.DENIED:
        recommendations.append("Request additional authorization for this operation")
        recommendations.append("Contact administrator for elevated permissions")
    
    elif decision.status == DecisionStatus.PARTIAL:
        recommendations.append("Some actions were not completed - review action results")
        recommendations.append("Retry failed actions individually")
    
    elif decision.status == DecisionStatus.SUCCESS:
        recommendations.append("Monitor system for expected changes")
        recommendations.append("Verify actions completed as expected")
    
    # Risk-based recommendations
    risk_level = decision.audit_trail.get("L1_strategic", {}).get("risk_level", "LOW")
    
    if risk_level in ["HIGH", "CRITICAL"]:
        recommendations.append("Schedule follow-up review within 24 hours")
        recommendations.append("Document changes in change management system")
    
    return recommendations
