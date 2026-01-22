"""
LLM Interpreter for HRM Decision System

Converts natural language input into structured HRM input format using Gemini LLM.
This component translates user intent into the three-level hierarchical structure:
- L1: Strategic (goal, authorization, risk)
- L2: Tactical (strategy, policy, subsystem)
- L3: Operational (specific actions)
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logging.warning("google-generativeai not installed. Using mock LLM mode.")

from ..schemas.request_schema import (
    UserRequest, 
    LLMOutput, 
    HRMInput,
    IntentType,
    RiskLevel,
    StrategicLevel,
    TacticalLevel,
    OperationalLevel,
    OperationalAction,
    Entities,
    Constraints
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LLMInterpreter:
    """
    Interprets natural language using Gemini LLM and converts to HRM input format.
    
    Features:
    - Gemini API integration
    - Structured output generation
    - Intent classification
    - Entity extraction
    - Hierarchical mapping (L1, L2, L3)
    - Fallback to mock mode if API unavailable
    """
    
    def __init__(self, api_key: Optional[str] = None, model_name: str = "gemini-1.5-flash"):
        """
        Initialize LLM Interpreter
        
        Args:
            api_key: Gemini API key (if None, tries to get from environment)
            model_name: Gemini model to use
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model_name = model_name
        self.use_mock = not GEMINI_AVAILABLE or not self.api_key
        
        if self.use_mock:
            logger.warning("Running in MOCK mode - using pattern-based interpretation")
        else:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(model_name)
            logger.info(f"LLM Interpreter initialized with {model_name}")
    
    def interpret(self, user_request: UserRequest, preprocessed_data: Optional[Dict[str, Any]] = None) -> LLMOutput:
        """
        Convert user request to structured LLM output
        
        Args:
            user_request: User request object
            preprocessed_data: Optional preprocessed data from NLPPreprocessor
            
        Returns:
            LLMOutput: Structured intent with entities and constraints
        """
        if self.use_mock:
            return self._mock_interpret(user_request, preprocessed_data)
        else:
            return self._gemini_interpret(user_request, preprocessed_data)
    
    def _gemini_interpret(self, user_request: UserRequest, preprocessed_data: Optional[Dict[str, Any]]) -> LLMOutput:
        """Use Gemini API for interpretation"""
        
        # Build prompt
        prompt = self._build_interpretation_prompt(user_request, preprocessed_data)
        
        try:
            # Call Gemini
            response = self.model.generate_content(prompt)
            
            # Parse response
            llm_output = self._parse_gemini_response(response.text, user_request)
            
            logger.info(f"Gemini interpretation successful for request {user_request.request_id}")
            return llm_output
            
        except Exception as e:
            logger.error(f"Gemini API error: {e}. Falling back to mock mode.")
            return self._mock_interpret(user_request, preprocessed_data)
    
    def _mock_interpret(self, user_request: UserRequest, preprocessed_data: Optional[Dict[str, Any]]) -> LLMOutput:
        """Mock interpretation using pattern matching"""
        
        message = user_request.message.lower()
        
        # Determine intent type
        if any(word in message for word in ["block", "suspicious", "attack", "threat", "malicious"]):
            intent_type = IntentType.SECURITY
            goal = "Block malicious network activity"
            actions = ["BLOCK_IP", "UPDATE_FIREWALL_RULES"]
        elif any(word in message for word in ["shutdown", "delete", "remove", "destroy"]):
            intent_type = IntentType.SYSTEM
            goal = "Execute critical system operation"
            actions = ["SHUTDOWN", "DELETE", "EXECUTE_COMMAND"]
        elif any(word in message for word in ["access", "permission", "grant", "allow", "deny", "revoke"]):
            intent_type = IntentType.ACCESS
            goal = "Manage access permissions"
            actions = ["GRANT_ACCESS", "REVOKE_ACCESS"]
        elif any(word in message for word in ["query", "show", "list", "get", "find", "view", "display"]):
            intent_type = IntentType.QUERY
            goal = "Query system information"
            actions = ["QUERY_DATABASE", "FETCH_LOGS"]
        elif any(word in message for word in ["comply", "audit", "report", "verify"]):
            intent_type = IntentType.COMPLIANCE
            goal = "Ensure compliance with policies"
            actions = ["GENERATE_AUDIT_REPORT", "VERIFY_COMPLIANCE"]
        else:
            intent_type = IntentType.SYSTEM
            goal = "Perform system operation"
            actions = ["EXECUTE_COMMAND"]
        
        # Extract time constraints
        time_window = {}
        if preprocessed_data and "time_references" in preprocessed_data:
            time_window = preprocessed_data["time_references"]
        
        # Extract entities
        entities = Entities(
            targets=self._extract_ips(message),
            subjects=[],
            objects=[]
        )
        
        # Build constraints
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
            confidence=0.75,
            reasoning=f"Mock interpretation based on pattern matching in message: '{user_request.message}'"
        )
    
    def _extract_ips(self, text: str) -> list:
        """Extract IP addresses from text"""
        import re
        ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
        return re.findall(ip_pattern, text)
    
    def _build_interpretation_prompt(self, user_request: UserRequest, preprocessed_data: Optional[Dict[str, Any]]) -> str:
        """Build prompt for Gemini API"""
        
        prompt = f"""You are an expert system that converts natural language security/system requests into structured JSON format.

USER REQUEST:
"{user_request.message}"

CONTEXT:
- User ID: {user_request.user_id}
- Timestamp: {user_request.timestamp}
- User Role: {user_request.context.user_role if user_request.context else 'Unknown'}

TASK:
Analyze the request and extract:
1. Intent type (SECURITY, COMPLIANCE, ACCESS, SYSTEM, or QUERY)
2. High-level goal
3. Entities (IP addresses, usernames, systems)
4. Constraints (time windows, filters, thresholds)
5. Requested actions

OUTPUT FORMAT (JSON):
{{
    "intent_type": "SECURITY|COMPLIANCE|ACCESS|SYSTEM|QUERY",
    "goal": "High-level goal description",
    "constraints": {{
        "time_window": {{}},
        "filters": {{}},
        "thresholds": {{}}
    }},
    "entities": {{
        "targets": ["list of target entities like IPs, users"],
        "subjects": [],
        "objects": []
    }},
    "requested_actions": ["action1", "action2"],
    "confidence": 0.95,
    "reasoning": "Brief explanation of your interpretation"
}}

Respond ONLY with valid JSON, no additional text.
"""
        
        return prompt
    
    def _parse_gemini_response(self, response_text: str, user_request: UserRequest) -> LLMOutput:
        """Parse Gemini response into LLMOutput"""
        
        try:
            # Extract JSON from response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            json_str = response_text[json_start:json_end]
            
            data = json.loads(json_str)
            
            return LLMOutput(
                intent_type=IntentType(data.get("intent_type", "SYSTEM")),
                goal=data.get("goal", "Unknown goal"),
                constraints=Constraints(**data.get("constraints", {})),
                entities=Entities(**data.get("entities", {})),
                requested_actions=data.get("requested_actions", []),
                confidence=data.get("confidence", 0.8),
                reasoning=data.get("reasoning", "")
            )
        except Exception as e:
            logger.error(f"Failed to parse Gemini response: {e}")
            # Fallback
            return self._mock_interpret(user_request, None)
    
    def llm_to_hrm_input(self, llm_output: LLMOutput, user_request: UserRequest) -> HRMInput:
        """
        Convert LLM output to HRM hierarchical input format
        
        Args:
            llm_output: Structured LLM interpretation
            user_request: Original user request
            
        Returns:
            HRMInput: Three-level hierarchical structure
        """
        
        # L1 Strategic Level - High-level goals and authorization
        risk_level = self._determine_risk_level(llm_output)
        auth_required = risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]
        
        strategic = StrategicLevel(
            goal=llm_output.goal,
            authorization_required=auth_required,
            risk_level=risk_level,
            priority=self._calculate_priority(llm_output)
        )
        
        # L2 Tactical Level - Strategy and policy selection
        strategy, policy, subsystem = self._determine_tactical_plan(llm_output)
        
        tactical = TacticalLevel(
            strategy=strategy,
            policy=policy,
            subsystem=subsystem,
            constraints=self._build_constraints_list(llm_output.constraints)
        )
        
        # L3 Operational Level - Concrete actions
        operational_actions = self._build_operational_actions(llm_output)
        
        operational = OperationalLevel(
            actions=operational_actions,
            execution_order="sequential"  # Default to sequential
        )
        
        return HRMInput(
            L1_strategic=strategic,
            L2_tactical=tactical,
            L3_operational=operational
        )
    
    def _determine_risk_level(self, llm_output: LLMOutput) -> RiskLevel:
        """Determine risk level based on intent and actions"""
        
        high_risk_actions = ["BLOCK_IP", "DELETE", "SHUTDOWN", "REVOKE_ACCESS", "UPDATE_FIREWALL_RULES"]
        critical_keywords = ["critical", "emergency", "urgent", "attack", "threat", "malicious", "breach",
                           "shutdown", "delete", "destroy", "remove"]
        low_risk_keywords = ["query", "show", "list", "get", "find", "view", "display", "login"]
        
        # Check for critical keywords in message or goal
        message_lower = llm_output.goal.lower()
        if any(kw in message_lower for kw in critical_keywords):
            return RiskLevel.CRITICAL
        
        # Check for high-risk actions
        if any(action in llm_output.requested_actions for action in high_risk_actions):
            return RiskLevel.HIGH
        
        # Query operations are typically low risk
        if llm_output.intent_type == IntentType.QUERY:
            return RiskLevel.LOW
        
        # Check for low risk keywords
        if any(kw in message_lower for kw in low_risk_keywords):
            return RiskLevel.LOW
        
        return RiskLevel.MEDIUM
    
    def _calculate_priority(self, llm_output: LLMOutput) -> int:
        """Calculate priority (1-10) based on intent and confidence"""
        
        base_priority = {
            IntentType.SECURITY: 8,
            IntentType.COMPLIANCE: 6,
            IntentType.ACCESS: 7,
            IntentType.SYSTEM: 5,
            IntentType.QUERY: 3
        }
        
        priority = base_priority.get(llm_output.intent_type, 5)
        
        # Adjust based on confidence
        if llm_output.confidence < 0.5:
            priority = max(1, priority - 2)
        
        return min(10, max(1, priority))
    
    def _determine_tactical_plan(self, llm_output: LLMOutput) -> tuple:
        """Determine strategy, policy, and subsystem"""
        
        intent_mapping = {
            IntentType.SECURITY: ("threat_mitigation", "security_blocking_policy", "firewall"),
            IntentType.COMPLIANCE: ("compliance_check", "compliance_policy", "audit_system"),
            IntentType.ACCESS: ("access_management", "access_control_policy", "identity_manager"),
            IntentType.SYSTEM: ("system_operation", "general_policy", "system_controller"),
            IntentType.QUERY: ("information_retrieval", "data_access_policy", "database")
        }
        
        return intent_mapping.get(llm_output.intent_type, ("default_strategy", "default_policy", "system"))
    
    def _build_constraints_list(self, constraints: Constraints) -> list:
        """Convert Constraints object to list of constraint strings"""
        
        constraint_list = []
        
        if constraints.time_window:
            for key, value in constraints.time_window.items():
                constraint_list.append(f"{key}: {value}")
        
        if constraints.thresholds:
            for key, value in constraints.thresholds.items():
                constraint_list.append(f"{key}: {value}")
        
        return constraint_list
    
    def _build_operational_actions(self, llm_output: LLMOutput) -> list:
        """Build list of operational actions"""
        
        actions = []
        
        for action_name in llm_output.requested_actions:
            # Build parameters based on entities
            params = {}
            if llm_output.entities.targets:
                if "IP" in action_name:
                    params["ip_list"] = llm_output.entities.targets
                else:
                    params["targets"] = llm_output.entities.targets
            
            operational_action = OperationalAction(
                action=action_name,
                params=params,
                conditions=["authorization_granted"] if llm_output.intent_type == IntentType.SECURITY else [],
                fallback=f"{action_name}_ROLLBACK"
            )
            
            actions.append(operational_action)
        
        return actions


# Convenience function
def create_llm_interpreter(api_key: Optional[str] = None) -> LLMInterpreter:
    """Factory function to create LLM interpreter"""
    return LLMInterpreter(api_key=api_key)
