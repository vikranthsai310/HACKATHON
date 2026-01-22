"""
Chat API Endpoint for Phase 2

This module provides the chat interface for natural language interaction
with the HRM Decision System.

Features:
- Real-time chat processing
- Session management
- Conversation context
- Streaming responses (optional)
- Intent clarification
"""

from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
import uuid
import json
import asyncio
import logging

from ..core.preprocessor import NLPPreprocessor
from ..core.llm_enhanced import EnhancedLLMInterpreter, LLMConfig, get_llm_interpreter
from ..core.prompt_templates import ConversationContext
from ..core.schema_validator import SchemaValidator
from ..schemas.request_schema import UserRequest, RequestContext

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["Chat"])


# =============================================================================
# Request/Response Models
# =============================================================================

class ChatMessage(BaseModel):
    """A single chat message"""
    role: str = Field(..., description="Role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    metadata: Optional[Dict[str, Any]] = None


class ChatRequest(BaseModel):
    """Chat request from user"""
    message: str = Field(..., min_length=1, max_length=5000, description="User's message")
    user_id: Optional[str] = Field(default="anonymous", description="User identifier")
    session_id: Optional[str] = Field(default=None, description="Session ID for context")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Additional context")
    stream: Optional[bool] = Field(default=False, description="Enable streaming response")


class IntentDetails(BaseModel):
    """Parsed intent details"""
    intent_type: str
    goal: str
    confidence: float
    risk_level: str
    requested_actions: List[str]
    entities: Dict[str, List[str]]
    constraints: Dict[str, Any]


class ChatResponse(BaseModel):
    """Chat response to user"""
    request_id: str = Field(..., description="Unique request identifier")
    session_id: str = Field(..., description="Session identifier")
    status: str = Field(..., description="Processing status")
    message: str = Field(..., description="Response message to display")
    intent: Optional[IntentDetails] = Field(default=None, description="Parsed intent")
    suggestions: Optional[List[str]] = Field(default=None, description="Suggested actions")
    clarification_needed: bool = Field(default=False, description="Whether clarification is needed")
    clarification_questions: Optional[List[str]] = Field(default=None, description="Questions for clarification")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    processing_time_ms: Optional[float] = None


class SessionInfo(BaseModel):
    """Session information"""
    session_id: str
    created_at: str
    last_activity: str
    message_count: int
    current_intent: Optional[str]
    extracted_entities: Dict[str, List[Any]]


class ConversationHistory(BaseModel):
    """Conversation history"""
    session_id: str
    messages: List[ChatMessage]
    total_messages: int


# =============================================================================
# Global Components
# =============================================================================

# Initialize components
preprocessor = NLPPreprocessor()
interpreter = get_llm_interpreter()
schema_validator = SchemaValidator()

# Session storage (in production, use Redis or database)
sessions: Dict[str, Dict[str, Any]] = {}


# =============================================================================
# Helper Functions
# =============================================================================

def get_or_create_session(session_id: Optional[str] = None) -> str:
    """Get existing session or create new one"""
    if session_id and session_id in sessions:
        sessions[session_id]["last_activity"] = datetime.now().isoformat()
        return session_id
    
    new_session_id = session_id or str(uuid.uuid4())
    sessions[new_session_id] = {
        "created_at": datetime.now().isoformat(),
        "last_activity": datetime.now().isoformat(),
        "messages": [],
        "context": interpreter.get_or_create_context(new_session_id)
    }
    return new_session_id


def add_message_to_session(session_id: str, role: str, content: str, metadata: Dict = None):
    """Add a message to session history"""
    if session_id in sessions:
        sessions[session_id]["messages"].append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata
        })
        sessions[session_id]["last_activity"] = datetime.now().isoformat()


def generate_suggestions(intent_type: str, actions: List[str]) -> List[str]:
    """Generate contextual suggestions based on intent"""
    suggestions_map = {
        "SECURITY": [
            "View blocked IP list",
            "Check firewall status",
            "Generate security report",
            "Scan for active threats"
        ],
        "ACCESS": [
            "List user permissions",
            "View access audit log",
            "Check role assignments",
            "Generate access report"
        ],
        "QUERY": [
            "Export results",
            "Set up alerts",
            "Schedule recurring query",
            "Filter by date range"
        ],
        "SYSTEM": [
            "Check system status",
            "View scheduled tasks",
            "Review system logs",
            "Run diagnostics"
        ],
        "COMPLIANCE": [
            "View compliance status",
            "Export audit report",
            "Schedule compliance check",
            "Review policy violations"
        ]
    }
    
    return suggestions_map.get(intent_type, ["Help", "View status", "Cancel"])


def build_response_message(intent_type: str, goal: str, actions: List[str], status: str) -> str:
    """Build a human-readable response message"""
    
    if status == "INTENT_PARSED":
        action_str = ", ".join(actions) if actions else "analysis"
        return f"I understand you want to {goal.lower()}. I'll proceed with: {action_str}."
    elif status == "CLARIFICATION_NEEDED":
        return f"I need some clarification to proceed with your {intent_type.lower()} request."
    elif status == "VALIDATION_FAILED":
        return "I couldn't fully understand your request. Could you please rephrase it?"
    elif status == "ERROR":
        return "I encountered an error processing your request. Please try again."
    else:
        return f"Processing your {intent_type.lower()} request..."


# =============================================================================
# API Endpoints
# =============================================================================

@router.post("", response_model=ChatResponse)
@router.post("/", response_model=ChatResponse)
async def process_chat(request: ChatRequest, background_tasks: BackgroundTasks):
    """
    Process a natural language chat request
    
    Flow:
    1. Create/retrieve session
    2. Preprocess input
    3. Send to LLM interpreter
    4. Validate output schema
    5. Check for clarification needs
    6. Return structured response
    """
    start_time = datetime.now()
    request_id = str(uuid.uuid4())[:12]
    
    try:
        # Step 1: Session management
        session_id = get_or_create_session(request.session_id)
        
        # Store user message
        add_message_to_session(session_id, "user", request.message)
        
        # Step 2: Create UserRequest
        user_request = UserRequest(
            user_id=request.user_id,
            message=request.message,
            context=RequestContext(
                user_role=request.context.get("user_role", "user") if request.context else "user",
                session_id=session_id,
                metadata=request.context or {}
            )
        )
        
        # Step 3: Preprocess
        preprocessed = preprocessor.preprocess(request.message)
        
        # Step 4: LLM Interpretation
        llm_output = interpreter.interpret(user_request, preprocessed, session_id)
        
        # Step 5: Build intent details
        intent_details = IntentDetails(
            intent_type=llm_output.intent_type.value,
            goal=llm_output.goal,
            confidence=llm_output.confidence,
            risk_level=interpreter._determine_risk_level(llm_output).value,
            requested_actions=llm_output.requested_actions,
            entities={
                "targets": llm_output.entities.targets,
                "subjects": llm_output.entities.subjects,
                "objects": llm_output.entities.objects
            },
            constraints={
                "time_window": llm_output.constraints.time_window,
                "filters": llm_output.constraints.filters
            }
        )
        
        # Step 6: Check for clarification
        context = interpreter.get_or_create_context(session_id)
        needs_clarification, ambiguities = context.needs_clarification({
            "intent_type": llm_output.intent_type.value,
            "confidence": llm_output.confidence,
            "entities": {
                "targets": llm_output.entities.targets,
                "subjects": llm_output.entities.subjects,
                "objects": llm_output.entities.objects
            },
            "requested_actions": llm_output.requested_actions
        })
        
        # Step 7: Build response
        status = "CLARIFICATION_NEEDED" if needs_clarification else "INTENT_PARSED"
        response_message = build_response_message(
            llm_output.intent_type.value,
            llm_output.goal,
            llm_output.requested_actions,
            status
        )
        
        suggestions = generate_suggestions(
            llm_output.intent_type.value,
            llm_output.requested_actions
        )
        
        # Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        
        # Store assistant response
        add_message_to_session(session_id, "assistant", response_message, {
            "intent_type": llm_output.intent_type.value,
            "confidence": llm_output.confidence
        })
        
        return ChatResponse(
            request_id=request_id,
            session_id=session_id,
            status=status,
            message=response_message,
            intent=intent_details,
            suggestions=suggestions,
            clarification_needed=needs_clarification,
            clarification_questions=ambiguities if needs_clarification else None,
            processing_time_ms=processing_time
        )
        
    except Exception as e:
        logger.error(f"Chat processing error: {e}")
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        
        return ChatResponse(
            request_id=request_id,
            session_id=request.session_id or str(uuid.uuid4()),
            status="ERROR",
            message=f"Error processing request: {str(e)}",
            intent=None,
            suggestions=["Try rephrasing your request", "Contact support"],
            clarification_needed=False,
            processing_time_ms=processing_time
        )


@router.post("/stream")
async def process_chat_stream(request: ChatRequest):
    """
    Process chat with streaming response
    
    Returns a stream of JSON chunks as the response is generated
    """
    session_id = get_or_create_session(request.session_id)
    
    async def generate():
        try:
            # Send session info
            yield json.dumps({"type": "session", "session_id": session_id}) + "\n"
            
            # Preprocessing status
            yield json.dumps({"type": "status", "message": "Preprocessing..."}) + "\n"
            preprocessed = preprocessor.preprocess(request.message)
            
            # Create user request
            user_request = UserRequest(
                user_id=request.user_id,
                message=request.message
            )
            
            # Interpretation status
            yield json.dumps({"type": "status", "message": "Analyzing intent..."}) + "\n"
            
            # Token callback for streaming
            tokens = []
            def on_token(token: str):
                tokens.append(token)
            
            # Interpret with streaming
            llm_output = await interpreter.interpret_stream(
                user_request, 
                preprocessed,
                on_token
            )
            
            # Send tokens
            for token in tokens:
                yield json.dumps({"type": "token", "content": token}) + "\n"
                await asyncio.sleep(0.01)
            
            # Send final result
            result = {
                "type": "complete",
                "intent_type": llm_output.intent_type.value,
                "goal": llm_output.goal,
                "confidence": llm_output.confidence,
                "actions": llm_output.requested_actions
            }
            yield json.dumps(result) + "\n"
            
        except Exception as e:
            yield json.dumps({"type": "error", "message": str(e)}) + "\n"
    
    return StreamingResponse(
        generate(),
        media_type="application/x-ndjson"
    )


@router.get("/session/{session_id}", response_model=SessionInfo)
async def get_session(session_id: str):
    """Get session information"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    context = interpreter.get_or_create_context(session_id)
    
    return SessionInfo(
        session_id=session_id,
        created_at=session["created_at"],
        last_activity=session["last_activity"],
        message_count=len(session["messages"]),
        current_intent=context.current_intent.get("intent_type") if context.current_intent else None,
        extracted_entities=context.extracted_entities
    )


@router.get("/session/{session_id}/history", response_model=ConversationHistory)
async def get_session_history(
    session_id: str,
    limit: int = Query(default=50, ge=1, le=100)
):
    """Get conversation history for a session"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    messages = sessions[session_id]["messages"][-limit:]
    
    return ConversationHistory(
        session_id=session_id,
        messages=[
            ChatMessage(
                role=m["role"],
                content=m["content"],
                timestamp=m["timestamp"],
                metadata=m.get("metadata")
            )
            for m in messages
        ],
        total_messages=len(sessions[session_id]["messages"])
    )


@router.delete("/session/{session_id}")
async def delete_session(session_id: str):
    """Delete a session and its context"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    del sessions[session_id]
    interpreter.clear_context(session_id)
    
    return {"status": "deleted", "session_id": session_id}


@router.post("/clarify")
async def clarify_intent(
    session_id: str,
    clarification: str
):
    """
    Provide clarification for an ambiguous request
    """
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    context = interpreter.get_or_create_context(session_id)
    
    # Get previous intent
    if not context.current_intent:
        raise HTTPException(status_code=400, detail="No pending intent to clarify")
    
    # Combine original with clarification
    combined_message = f"{context.history[-1]['user_message']}. Clarification: {clarification}"
    
    # Re-process with clarification
    request = ChatRequest(
        message=combined_message,
        session_id=session_id
    )
    
    return await process_chat(request, BackgroundTasks())


@router.get("/examples")
async def get_chat_examples():
    """Get example chat messages for different intent types"""
    return {
        "examples": [
            {
                "intent_type": "SECURITY",
                "examples": [
                    "Block all suspicious login attempts from foreign IPs",
                    "Check for any active security threats",
                    "Show me failed authentication attempts in the last hour"
                ]
            },
            {
                "intent_type": "ACCESS",
                "examples": [
                    "Grant John Smith read access to financial reports",
                    "Revoke admin permissions for user jdoe",
                    "List all users with database access"
                ]
            },
            {
                "intent_type": "QUERY",
                "examples": [
                    "Show me system logs from yesterday",
                    "List all active user sessions",
                    "Get the status of all running services"
                ]
            },
            {
                "intent_type": "SYSTEM",
                "examples": [
                    "Schedule database backup for 2 AM tonight",
                    "Restart the authentication service",
                    "Update the firewall configuration"
                ]
            },
            {
                "intent_type": "COMPLIANCE",
                "examples": [
                    "Generate compliance audit report for Q4",
                    "Check GDPR compliance status",
                    "List all policy violations this month"
                ]
            }
        ]
    }


@router.get("/stats")
async def get_chat_stats():
    """Get chat system statistics"""
    active_sessions = len(sessions)
    total_messages = sum(len(s["messages"]) for s in sessions.values())
    cache_stats = interpreter.get_cache_stats()
    
    return {
        "active_sessions": active_sessions,
        "total_messages": total_messages,
        "cache": cache_stats,
        "interpreter_mode": "mock" if interpreter.use_mock else "gemini"
    }
