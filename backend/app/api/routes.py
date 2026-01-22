"""
API Routes for HRM Decision System

Defines all API endpoints for the decision system.
"""

from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Optional
import logging

from ..schemas.request_schema import (
    UserRequest,
    LLMOutput,
    HRMInput,
    DecisionOutput,
    AuditLogEntry
)
from ..core.preprocessor import NLPPreprocessor
from ..core.llm_interpreter import LLMInterpreter
from ..core.hrm_engine import HRMEngine
from ..core.action_executor import ActionExecutor

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# Initialize components (singleton instances)
preprocessor = NLPPreprocessor()
llm_interpreter = LLMInterpreter()
hrm_engine = HRMEngine(use_simulation=True)
action_executor = ActionExecutor(dry_run=True)


# ==========================================
# MAIN DECISION ENDPOINT
# ==========================================

@router.post("/decision", response_model=DecisionOutput, status_code=status.HTTP_200_OK)
async def make_decision(user_request: UserRequest):
    """
    Main endpoint: Process user request through complete decision pipeline
    
    Pipeline:
    1. Preprocess natural language input
    2. LLM interpretation → structured intent
    3. Convert to HRM hierarchical format
    4. HRM reasoning → decision
    5. Execute actions (if approved)
    6. Return decision with audit trail
    """
    
    try:
        logger.info(f"Processing request {user_request.request_id} from user {user_request.user_id}")
        
        # Step 1: Preprocess
        logger.info("Step 1: Preprocessing input")
        preprocessed_data = preprocessor.preprocess(user_request.message)
        
        # Step 2: LLM Interpretation
        logger.info("Step 2: LLM interpretation")
        llm_output = llm_interpreter.interpret(user_request, preprocessed_data)
        
        # Step 3: Convert to HRM Input
        logger.info("Step 3: Converting to HRM input format")
        hrm_input = llm_interpreter.llm_to_hrm_input(llm_output, user_request)
        
        # Step 4: HRM Reasoning
        logger.info("Step 4: HRM reasoning")
        decision = hrm_engine.process(hrm_input, user_request.request_id)
        
        # Step 5: Execute Actions
        logger.info("Step 5: Executing actions")
        decision = action_executor.execute_decision(decision, user_request.user_id)
        
        logger.info(f"Decision {decision.decision_id} completed with status: {decision.status}")
        
        return decision
        
    except Exception as e:
        logger.error(f"Error processing request {user_request.request_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process request: {str(e)}"
        )


# ==========================================
# COMPONENT-SPECIFIC ENDPOINTS (for testing)
# ==========================================

@router.post("/preprocess", status_code=status.HTTP_200_OK)
async def preprocess_text(message: str):
    """Preprocess text using NLP preprocessor"""
    
    try:
        result = preprocessor.preprocess(message)
        return {
            "original": message,
            "preprocessed": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/interpret", response_model=LLMOutput, status_code=status.HTTP_200_OK)
async def interpret_request(user_request: UserRequest):
    """Interpret user request using LLM"""
    
    try:
        preprocessed_data = preprocessor.preprocess(user_request.message)
        llm_output = llm_interpreter.interpret(user_request, preprocessed_data)
        return llm_output
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/hrm-input", response_model=HRMInput, status_code=status.HTTP_200_OK)
async def generate_hrm_input(user_request: UserRequest):
    """Generate HRM hierarchical input from user request"""
    
    try:
        preprocessed_data = preprocessor.preprocess(user_request.message)
        llm_output = llm_interpreter.interpret(user_request, preprocessed_data)
        hrm_input = llm_interpreter.llm_to_hrm_input(llm_output, user_request)
        return hrm_input
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/reason", response_model=DecisionOutput, status_code=status.HTTP_200_OK)
async def reason_hrm(hrm_input: HRMInput, request_id: str = "test-request"):
    """Process HRM input through reasoning engine"""
    
    try:
        decision = hrm_engine.process(hrm_input, request_id)
        return decision
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ==========================================
# AUDIT & MONITORING ENDPOINTS
# ==========================================

@router.get("/audit-logs", response_model=List[AuditLogEntry], status_code=status.HTTP_200_OK)
async def get_audit_logs(request_id: Optional[str] = None):
    """Get audit logs, optionally filtered by request ID"""
    
    try:
        logs = action_executor.get_audit_logs(request_id)
        return logs
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/audit-logs", status_code=status.HTTP_204_NO_CONTENT)
async def clear_audit_logs():
    """Clear all audit logs"""
    
    try:
        action_executor.clear_audit_logs()
        return {"message": "Audit logs cleared"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ==========================================
# CONFIGURATION ENDPOINTS
# ==========================================

@router.get("/config/executor-mode")
async def get_executor_mode():
    """Get current action executor mode (dry-run or live)"""
    return {
        "dry_run": action_executor.dry_run,
        "mode": "DRY-RUN" if action_executor.dry_run else "LIVE"
    }


@router.post("/config/executor-mode")
async def set_executor_mode(dry_run: bool):
    """Set action executor mode"""
    action_executor.dry_run = dry_run
    return {
        "dry_run": dry_run,
        "mode": "DRY-RUN" if dry_run else "LIVE",
        "message": f"Action executor mode set to {'DRY-RUN' if dry_run else 'LIVE'}"
    }


@router.get("/config/hrm-mode")
async def get_hrm_mode():
    """Get current HRM engine mode (simulation or model)"""
    return {
        "simulation": hrm_engine.use_simulation,
        "mode": "SIMULATION" if hrm_engine.use_simulation else "MODEL"
    }


@router.get("/config/llm-mode")
async def get_llm_mode():
    """Get current LLM interpreter mode (mock or Gemini)"""
    return {
        "mock": llm_interpreter.use_mock,
        "mode": "MOCK" if llm_interpreter.use_mock else "GEMINI",
        "model": llm_interpreter.model_name if not llm_interpreter.use_mock else None
    }


# ==========================================
# EXAMPLE REQUESTS
# ==========================================

@router.get("/examples")
async def get_examples():
    """Get example requests for testing"""
    
    return {
        "examples": [
            {
                "name": "Block Suspicious IPs",
                "request": {
                    "user_id": "admin-001",
                    "message": "Block all suspicious IP addresses from the last 24 hours",
                    "context": {
                        "user_role": "security_admin"
                    }
                }
            },
            {
                "name": "Grant Access",
                "request": {
                    "user_id": "manager-001",
                    "message": "Grant user john.doe access to the analytics dashboard",
                    "context": {
                        "user_role": "manager"
                    }
                }
            },
            {
                "name": "Query Logs",
                "request": {
                    "user_id": "analyst-001",
                    "message": "Show me all login attempts from yesterday",
                    "context": {
                        "user_role": "security_analyst"
                    }
                }
            },
            {
                "name": "Compliance Check",
                "request": {
                    "user_id": "compliance-001",
                    "message": "Generate an audit report for the last month",
                    "context": {
                        "user_role": "compliance_officer"
                    }
                }
            }
        ]
    }
