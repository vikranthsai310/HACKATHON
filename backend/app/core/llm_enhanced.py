"""
Enhanced LLM Interpreter for Phase 2

This module provides a robust LLM integration with:
- Real Gemini API integration with proper error handling
- Streaming support for real-time responses
- Response caching for efficiency
- Retry logic with exponential backoff
- Structured output parsing
- Fallback to mock mode when API unavailable
"""

import os
import json
import logging
import hashlib
import asyncio
from typing import Dict, Any, Optional, AsyncGenerator, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from functools import lru_cache
import re

try:
    import google.generativeai as genai
    from google.generativeai.types import GenerateContentResponse
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    genai = None

from .prompt_templates import PromptTemplates, ConversationContext
from ..schemas.request_schema import (
    UserRequest, LLMOutput, HRMInput, IntentType, RiskLevel,
    StrategicLevel, TacticalLevel, OperationalLevel, OperationalAction,
    Entities, Constraints
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class LLMConfig:
    """Configuration for LLM Interpreter"""
    api_key: Optional[str] = None
    model_name: str = "gemini-1.5-flash"
    temperature: float = 0.1
    max_tokens: int = 4096
    timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0
    cache_ttl: int = 300  # 5 minutes
    use_few_shot: bool = True
    enable_streaming: bool = False


@dataclass
class CacheEntry:
    """Cache entry for LLM responses"""
    response: Dict[str, Any]
    timestamp: datetime
    hits: int = 0


class ResponseCache:
    """Simple in-memory cache for LLM responses"""
    
    def __init__(self, ttl: int = 300, max_size: int = 1000):
        self.ttl = ttl
        self.max_size = max_size
        self._cache: Dict[str, CacheEntry] = {}
    
    def _get_key(self, prompt: str) -> str:
        """Generate cache key from prompt"""
        return hashlib.md5(prompt.encode()).hexdigest()
    
    def get(self, prompt: str) -> Optional[Dict[str, Any]]:
        """Get cached response if valid"""
        key = self._get_key(prompt)
        entry = self._cache.get(key)
        
        if entry is None:
            return None
        
        # Check TTL
        if datetime.now() - entry.timestamp > timedelta(seconds=self.ttl):
            del self._cache[key]
            return None
        
        entry.hits += 1
        return entry.response
    
    def set(self, prompt: str, response: Dict[str, Any]):
        """Cache a response"""
        # Evict old entries if at max size
        if len(self._cache) >= self.max_size:
            self._evict_oldest()
        
        key = self._get_key(prompt)
        self._cache[key] = CacheEntry(
            response=response,
            timestamp=datetime.now()
        )
    
    def _evict_oldest(self):
        """Remove oldest cache entries"""
        if not self._cache:
            return
        
        # Sort by timestamp and remove oldest 10%
        sorted_keys = sorted(
            self._cache.keys(),
            key=lambda k: self._cache[k].timestamp
        )
        
        to_remove = max(1, len(sorted_keys) // 10)
        for key in sorted_keys[:to_remove]:
            del self._cache[key]
    
    def clear(self):
        """Clear all cached entries"""
        self._cache.clear()
    
    def stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_hits = sum(e.hits for e in self._cache.values())
        return {
            "size": len(self._cache),
            "max_size": self.max_size,
            "total_hits": total_hits,
            "ttl": self.ttl
        }


class LLMResponseParser:
    """Parse and validate LLM responses"""
    
    @staticmethod
    def parse_json_response(text: str) -> Dict[str, Any]:
        """
        Parse JSON from LLM response text
        Handles various formats including markdown code blocks
        """
        # Try direct JSON parse first
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
        
        # Try to extract JSON from markdown code blocks
        json_patterns = [
            r'```json\s*([\s\S]*?)\s*```',
            r'```\s*([\s\S]*?)\s*```',
            r'\{[\s\S]*\}'
        ]
        
        for pattern in json_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                try:
                    return json.loads(match)
                except json.JSONDecodeError:
                    continue
        
        # If all else fails, return error structure
        logger.error(f"Failed to parse JSON from response: {text[:200]}...")
        return {
            "error": "Failed to parse JSON response",
            "raw_text": text[:500],
            "intent_type": "QUERY",
            "confidence": 0.0
        }
    
    @staticmethod
    def validate_intent_response(response: Dict[str, Any]) -> tuple:
        """
        Validate the parsed intent response
        Returns: (is_valid, errors, validated_response)
        """
        errors = []
        
        # Required fields
        required_fields = ["intent_type", "goal", "requested_actions", "confidence"]
        for field in required_fields:
            if field not in response:
                errors.append(f"Missing required field: {field}")
        
        # Validate intent_type
        valid_intents = ["SECURITY", "COMPLIANCE", "ACCESS", "SYSTEM", "QUERY"]
        intent_type = response.get("intent_type", "")
        if intent_type not in valid_intents:
            errors.append(f"Invalid intent_type: {intent_type}")
            response["intent_type"] = "QUERY"  # Default
        
        # Validate confidence
        confidence = response.get("confidence", 0)
        if not isinstance(confidence, (int, float)) or not 0 <= confidence <= 1:
            errors.append(f"Invalid confidence value: {confidence}")
            response["confidence"] = 0.5
        
        # Ensure nested structures exist
        if "constraints" not in response:
            response["constraints"] = {}
        if "entities" not in response:
            response["entities"] = {"targets": [], "subjects": [], "objects": []}
        if "requested_actions" not in response:
            response["requested_actions"] = []
        
        return len(errors) == 0, errors, response
    
    @staticmethod
    def normalize_entities(entities: Dict[str, Any]) -> Entities:
        """Convert parsed entities to Entities schema"""
        targets = []
        subjects = []
        objects = []
        
        for target in entities.get("targets", []):
            if isinstance(target, dict):
                targets.append(target.get("value", str(target)))
            else:
                targets.append(str(target))
        
        for subject in entities.get("subjects", []):
            if isinstance(subject, dict):
                subjects.append(subject.get("value", str(subject)))
            else:
                subjects.append(str(subject))
        
        for obj in entities.get("objects", []):
            if isinstance(obj, dict):
                objects.append(obj.get("value", str(obj)))
            else:
                objects.append(str(obj))
        
        return Entities(targets=targets, subjects=subjects, objects=objects)


class EnhancedLLMInterpreter:
    """
    Enhanced LLM Interpreter with real Gemini integration
    
    Features:
    - Real Gemini API integration
    - Response caching
    - Retry logic with exponential backoff
    - Streaming support
    - Structured output parsing
    - Conversation context management
    """
    
    def __init__(self, config: Optional[LLMConfig] = None):
        """Initialize the enhanced LLM interpreter"""
        # Import settings here to avoid circular imports
        from ..config import settings
        
        self.config = config or LLMConfig()
        # Try config first, then settings, then environment variable
        self.config.api_key = self.config.api_key or settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY")
        self.config.model_name = self.config.model_name or settings.GEMINI_MODEL
        
        self.cache = ResponseCache(ttl=self.config.cache_ttl)
        self.parser = LLMResponseParser()
        self.contexts: Dict[str, ConversationContext] = {}
        
        # Initialize Gemini if available
        self.use_mock = not GEMINI_AVAILABLE or not self.config.api_key
        
        if self.use_mock:
            if not GEMINI_AVAILABLE:
                logger.warning("Enhanced LLM running in MOCK mode - google-generativeai not installed")
            else:
                logger.warning("Enhanced LLM running in MOCK mode - no API key provided")
        else:
            try:
                genai.configure(api_key=self.config.api_key)
                self.model = genai.GenerativeModel(
                    self.config.model_name,
                    generation_config={
                        "temperature": self.config.temperature,
                        "max_output_tokens": self.config.max_tokens,
                    }
                )
                logger.info(f"✓ Enhanced LLM initialized with {self.config.model_name} and real Gemini API")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini: {e}")
                self.use_mock = True
    
    def get_or_create_context(self, session_id: str) -> ConversationContext:
        """Get or create conversation context"""
        if session_id not in self.contexts:
            self.contexts[session_id] = ConversationContext(session_id)
        return self.contexts[session_id]
    
    def interpret(
        self,
        user_request: UserRequest,
        preprocessed_data: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None
    ) -> LLMOutput:
        """
        Interpret user request and return structured LLM output
        
        Args:
            user_request: The user's request
            preprocessed_data: Optional preprocessed data
            session_id: Optional session ID for context management
            
        Returns:
            LLMOutput: Structured intent output
        """
        # Get conversation context
        context = None
        if session_id:
            context = self.get_or_create_context(session_id)
        
        if self.use_mock:
            return self._mock_interpret(user_request, preprocessed_data)
        
        return self._gemini_interpret(user_request, preprocessed_data, context)
    
    async def interpret_async(
        self,
        user_request: UserRequest,
        preprocessed_data: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None
    ) -> LLMOutput:
        """Async version of interpret"""
        # Run in executor for non-blocking
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self.interpret,
            user_request,
            preprocessed_data,
            session_id
        )
    
    async def interpret_stream(
        self,
        user_request: UserRequest,
        preprocessed_data: Optional[Dict[str, Any]] = None,
        on_token: Optional[Callable[[str], None]] = None
    ) -> LLMOutput:
        """
        Stream interpretation with real-time token callback
        
        Args:
            user_request: The user's request
            preprocessed_data: Optional preprocessed data
            on_token: Callback for each token received
            
        Returns:
            LLMOutput: Final structured output
        """
        if self.use_mock or not self.config.enable_streaming:
            return self.interpret(user_request, preprocessed_data)
        
        try:
            prompt = self._build_prompt(user_request, preprocessed_data)
            system_prompt = PromptTemplates.get_full_system_prompt(self.config.use_few_shot)
            full_prompt = f"{system_prompt}\n\n{prompt}"
            
            # Stream response
            response_text = ""
            response = self.model.generate_content(
                full_prompt,
                stream=True
            )
            
            for chunk in response:
                if chunk.text:
                    response_text += chunk.text
                    if on_token:
                        on_token(chunk.text)
            
            # Parse final response
            parsed = self.parser.parse_json_response(response_text)
            is_valid, errors, validated = self.parser.validate_intent_response(parsed)
            
            if not is_valid:
                logger.warning(f"Validation errors: {errors}")
            
            return self._response_to_llm_output(validated, user_request)
            
        except Exception as e:
            logger.error(f"Streaming interpretation failed: {e}")
            return self._mock_interpret(user_request, preprocessed_data)
    
    def _gemini_interpret(
        self,
        user_request: UserRequest,
        preprocessed_data: Optional[Dict[str, Any]],
        context: Optional[ConversationContext] = None
    ) -> LLMOutput:
        """Use Gemini API for interpretation with caching and retries"""
        
        # Build prompt
        prompt = self._build_prompt(user_request, preprocessed_data, context)
        system_prompt = PromptTemplates.get_full_system_prompt(self.config.use_few_shot)
        full_prompt = f"{system_prompt}\n\n{prompt}"
        
        # Check cache
        cached = self.cache.get(full_prompt)
        if cached:
            logger.info("Using cached LLM response")
            return self._response_to_llm_output(cached, user_request)
        
        # Call Gemini with retries
        for attempt in range(self.config.max_retries):
            try:
                response = self.model.generate_content(full_prompt)
                
                # Parse response
                parsed = self.parser.parse_json_response(response.text)
                is_valid, errors, validated = self.parser.validate_intent_response(parsed)
                
                if not is_valid:
                    logger.warning(f"Validation errors: {errors}")
                
                # Cache successful response
                self.cache.set(full_prompt, validated)
                
                # Update context if available
                if context:
                    context.add_turn(
                        user_request.message,
                        validated,
                        f"Intent: {validated.get('intent_type')}"
                    )
                
                return self._response_to_llm_output(validated, user_request)
                
            except Exception as e:
                logger.error(f"Gemini API call failed (attempt {attempt + 1}): {e}")
                if attempt < self.config.max_retries - 1:
                    delay = self.config.retry_delay * (2 ** attempt)
                    logger.info(f"Retrying in {delay}s...")
                    import time
                    time.sleep(delay)
        
        # Fallback to mock
        logger.warning("All Gemini attempts failed, falling back to mock")
        return self._mock_interpret(user_request, preprocessed_data)
    
    def _build_prompt(
        self,
        user_request: UserRequest,
        preprocessed_data: Optional[Dict[str, Any]],
        context: Optional[ConversationContext] = None
    ) -> str:
        """Build the interpretation prompt"""
        
        context_dict = None
        if context:
            context_dict = context.get_context_for_prompt()
        elif user_request.context:
            context_dict = {
                "user_role": user_request.context.user_role,
                "session_id": user_request.context.session_id
            }
        
        return PromptTemplates.build_intent_prompt(
            message=user_request.message,
            preprocessed=preprocessed_data,
            context=context_dict
        )
    
    def _response_to_llm_output(
        self,
        response: Dict[str, Any],
        user_request: UserRequest
    ) -> LLMOutput:
        """Convert parsed response to LLMOutput schema"""
        
        # Map intent type
        intent_map = {
            "SECURITY": IntentType.SECURITY,
            "COMPLIANCE": IntentType.COMPLIANCE,
            "ACCESS": IntentType.ACCESS,
            "SYSTEM": IntentType.SYSTEM,
            "QUERY": IntentType.QUERY
        }
        
        intent_type = intent_map.get(
            response.get("intent_type", "QUERY"),
            IntentType.QUERY
        )
        
        # Build entities
        entities = self.parser.normalize_entities(response.get("entities", {}))
        
        # Build constraints
        constraints_data = response.get("constraints", {})
        constraints = Constraints(
            time_window=constraints_data.get("time_window", {}),
            filters=constraints_data.get("filters", {}),
            thresholds=constraints_data.get("thresholds", {})
        )
        
        return LLMOutput(
            intent_type=intent_type,
            goal=response.get("goal", "Process user request"),
            constraints=constraints,
            entities=entities,
            requested_actions=response.get("requested_actions", []),
            confidence=response.get("confidence", 0.5),
            raw_response=response
        )
    
    def _mock_interpret(
        self,
        user_request: UserRequest,
        preprocessed_data: Optional[Dict[str, Any]]
    ) -> LLMOutput:
        """Enhanced mock interpretation with better pattern matching"""
        
        message = user_request.message.lower()
        
        # Intent detection patterns
        security_patterns = ["block", "threat", "attack", "suspicious", "malicious", "firewall", "intrusion"]
        access_patterns = ["access", "permission", "grant", "revoke", "allow", "deny", "user", "role"]
        query_patterns = ["show", "list", "get", "find", "query", "display", "view", "status"]
        system_patterns = ["schedule", "backup", "restart", "shutdown", "configure", "update", "maintenance"]
        compliance_patterns = ["audit", "compliance", "report", "policy", "regulatory", "verify"]
        
        # Determine intent type and goal
        if any(p in message for p in security_patterns):
            intent_type = IntentType.SECURITY
            goal = "Handle security-related request"
            actions = self._get_security_actions(message)
            risk = "HIGH" if any(w in message for w in ["block", "shutdown", "delete"]) else "MEDIUM"
        elif any(p in message for p in ["shutdown", "delete", "destroy", "remove all"]):
            intent_type = IntentType.SYSTEM
            goal = "Execute critical system operation"
            actions = ["SHUTDOWN", "DELETE", "EXECUTE_COMMAND"]
            risk = "CRITICAL"
        elif any(p in message for p in access_patterns):
            intent_type = IntentType.ACCESS
            goal = "Manage access permissions"
            actions = self._get_access_actions(message)
            risk = "MEDIUM"
        elif any(p in message for p in query_patterns):
            intent_type = IntentType.QUERY
            goal = "Query system information"
            actions = ["QUERY_DATABASE", "FETCH_LOGS"]
            risk = "LOW"
        elif any(p in message for p in system_patterns):
            intent_type = IntentType.SYSTEM
            goal = "Perform system operation"
            actions = self._get_system_actions(message)
            risk = "MEDIUM"
        elif any(p in message for p in compliance_patterns):
            intent_type = IntentType.COMPLIANCE
            goal = "Ensure compliance"
            actions = ["GENERATE_AUDIT_REPORT", "VERIFY_COMPLIANCE"]
            risk = "LOW"
        else:
            intent_type = IntentType.QUERY
            goal = "Process general request"
            actions = ["ANALYZE"]
            risk = "LOW"
        
        # Extract entities
        entities = self._extract_entities_mock(message)
        
        # Build time constraints from preprocessed data
        time_window = {}
        if preprocessed_data and preprocessed_data.get("time_references"):
            time_window = preprocessed_data["time_references"]
        
        constraints = Constraints(
            time_window=time_window,
            filters={},
            thresholds={}
        )
        
        return LLMOutput(
            intent_type=intent_type,
            goal=goal,
            constraints=constraints,
            entities=entities,
            requested_actions=actions,
            confidence=0.85,
            raw_response={
                "mock": True,
                "risk_assessment": risk,
                "reasoning": f"Pattern-matched intent: {intent_type.value}"
            }
        )
    
    def _get_security_actions(self, message: str) -> list:
        """Get security-related actions"""
        actions = []
        if "block" in message:
            actions.append("BLOCK_IP")
        if "firewall" in message or "rule" in message:
            actions.append("UPDATE_FIREWALL_RULES")
        if "scan" in message:
            actions.append("SCAN_NETWORK")
        if "isolate" in message:
            actions.append("ISOLATE_SYSTEM")
        if not actions:
            actions.append("SCAN_NETWORK")
        return actions
    
    def _get_access_actions(self, message: str) -> list:
        """Get access-related actions"""
        actions = []
        if "grant" in message or "give" in message or "allow" in message:
            actions.append("GRANT_ACCESS")
        if "revoke" in message or "remove" in message or "deny" in message:
            actions.append("REVOKE_ACCESS")
        if "modify" in message or "change" in message:
            actions.append("MODIFY_PERMISSIONS")
        if not actions:
            actions.append("GRANT_ACCESS")
        return actions
    
    def _get_system_actions(self, message: str) -> list:
        """Get system-related actions"""
        actions = []
        if "schedule" in message:
            actions.append("SCHEDULE_TASK")
        if "backup" in message:
            actions.append("BACKUP_DATA")
        if "restart" in message:
            actions.append("RESTART_SERVICE")
        if "update" in message or "config" in message:
            actions.append("UPDATE_CONFIG")
        if not actions:
            actions.append("EXECUTE_COMMAND")
        return actions
    
    def _extract_entities_mock(self, message: str) -> Entities:
        """Extract entities using pattern matching"""
        import re
        
        targets = []
        subjects = []
        objects = []
        
        # IP addresses
        ips = re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', message)
        targets.extend(ips)
        
        # Email addresses
        emails = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', message)
        subjects.extend(emails)
        
        # Usernames (common patterns)
        usernames = re.findall(r'\b(?:user|admin|manager)\s+(\w+)', message, re.I)
        subjects.extend(usernames)
        
        # Names (Title Case words after certain keywords)
        name_patterns = re.findall(r'(?:grant|revoke|for|to|from)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)', message)
        subjects.extend(name_patterns)
        
        # Resources
        resource_keywords = ["database", "server", "firewall", "system", "logs", "reports", "files"]
        for keyword in resource_keywords:
            if keyword in message:
                objects.append(keyword)
        
        return Entities(targets=targets, subjects=subjects, objects=objects)
    
    def llm_to_hrm_input(self, llm_output: LLMOutput, user_request: UserRequest) -> HRMInput:
        """Convert LLM output to HRM input format"""
        
        # Determine risk level
        risk_level = self._determine_risk_level(llm_output)
        
        # Check if authorization required
        auth_required = risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]
        
        # Calculate priority
        priority = self._calculate_priority(llm_output)
        
        # Build strategic level
        strategic = StrategicLevel(
            goal=llm_output.goal,
            authorization_required=auth_required,
            risk_level=risk_level,
            priority=priority
        )
        
        # Build tactical level
        strategy, policy, subsystem = self._map_tactical(llm_output)
        tactical = TacticalLevel(
            strategy=strategy,
            policy=policy,
            subsystem=subsystem,
            constraints=list(llm_output.constraints.filters.keys()) if llm_output.constraints.filters else []
        )
        
        # Build operational level
        operational_actions = self._map_operational_actions(llm_output)
        operational = OperationalLevel(
            actions=operational_actions,
            execution_order="sequential"
        )
        
        return HRMInput(
            L1_strategic=strategic,
            L2_tactical=tactical,
            L3_operational=operational
        )
    
    def _determine_risk_level(self, llm_output: LLMOutput) -> RiskLevel:
        """Determine risk level based on intent and actions"""
        
        high_risk_actions = ["BLOCK_IP", "DELETE", "SHUTDOWN", "REVOKE_ACCESS", "UPDATE_FIREWALL_RULES"]
        critical_keywords = ["critical", "shutdown", "delete", "destroy", "attack", "breach", "threat"]
        
        # Check raw response for risk assessment if available
        raw_response = getattr(llm_output, 'raw_response', None)
        if raw_response and isinstance(raw_response, dict):
            risk = raw_response.get("risk_assessment", "")
            if risk == "CRITICAL":
                return RiskLevel.CRITICAL
            elif risk == "HIGH":
                return RiskLevel.HIGH
            elif risk == "LOW":
                return RiskLevel.LOW
        
        # Check goal for critical keywords
        if any(kw in llm_output.goal.lower() for kw in critical_keywords):
            return RiskLevel.CRITICAL
        
        # Check for high-risk actions
        if any(action in llm_output.requested_actions for action in high_risk_actions):
            return RiskLevel.HIGH
        
        # Query operations are low risk
        if llm_output.intent_type == IntentType.QUERY:
            return RiskLevel.LOW
        
        return RiskLevel.MEDIUM
    
    def _calculate_priority(self, llm_output: LLMOutput) -> int:
        """Calculate priority (1-10) based on intent"""
        
        base_priority = {
            IntentType.SECURITY: 8,
            IntentType.COMPLIANCE: 6,
            IntentType.ACCESS: 7,
            IntentType.SYSTEM: 5,
            IntentType.QUERY: 3
        }
        
        priority = base_priority.get(llm_output.intent_type, 5)
        
        # Adjust based on confidence
        if llm_output.confidence > 0.9:
            priority = min(10, priority + 1)
        elif llm_output.confidence < 0.5:
            priority = max(1, priority - 1)
        
        return priority
    
    def _map_tactical(self, llm_output: LLMOutput) -> tuple:
        """Map intent to tactical parameters"""
        
        tactical_map = {
            IntentType.SECURITY: ("threat_mitigation", "security_policy", "firewall"),
            IntentType.ACCESS: ("access_control", "access_policy", "identity_manager"),
            IntentType.QUERY: ("information_retrieval", "data_access_policy", "database"),
            IntentType.SYSTEM: ("system_operation", "operational_policy", "system_controller"),
            IntentType.COMPLIANCE: ("compliance_check", "regulatory_policy", "audit_system")
        }
        
        return tactical_map.get(
            llm_output.intent_type,
            ("general_operation", "default_policy", "general_system")
        )
    
    def _map_operational_actions(self, llm_output: LLMOutput) -> list:
        """Map requested actions to operational actions"""
        
        actions = []
        for action_name in llm_output.requested_actions:
            params = self._get_action_params(action_name, llm_output)
            actions.append(OperationalAction(
                action=action_name,
                params=params,
                conditions=[],
                fallback=f"{action_name}_ROLLBACK"
            ))
        
        return actions if actions else [
            OperationalAction(
                action="ANALYZE",
                params={},
                conditions=[],
                fallback="LOG_REQUEST"
            )
        ]
    
    def _get_action_params(self, action: str, llm_output: LLMOutput) -> Dict[str, Any]:
        """Get parameters for a specific action"""
        
        params = {}
        
        if action in ["BLOCK_IP", "ALLOW_IP"]:
            params["ip_list"] = llm_output.entities.targets
        elif action in ["GRANT_ACCESS", "REVOKE_ACCESS"]:
            params["subjects"] = llm_output.entities.subjects
            params["resources"] = llm_output.entities.objects
        elif action in ["QUERY_DATABASE", "FETCH_LOGS"]:
            params["time_window"] = llm_output.constraints.time_window
            params["filters"] = llm_output.constraints.filters
        elif action == "SCHEDULE_TASK":
            params["schedule"] = llm_output.constraints.time_window
        
        return params
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return self.cache.stats()
    
    def clear_cache(self):
        """Clear the response cache"""
        self.cache.clear()
    
    def clear_context(self, session_id: str):
        """Clear conversation context for a session"""
        if session_id in self.contexts:
            del self.contexts[session_id]


# Singleton instance for easy import
_interpreter_instance: Optional[EnhancedLLMInterpreter] = None


def get_llm_interpreter(config: Optional[LLMConfig] = None) -> EnhancedLLMInterpreter:
    """Get or create singleton LLM interpreter instance"""
    global _interpreter_instance
    
    if _interpreter_instance is None:
        _interpreter_instance = EnhancedLLMInterpreter(config)
    
    return _interpreter_instance
