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
        """Mock interpretation using enhanced pattern matching with realistic variance"""
        import random
        import re
        
        message = user_request.message.lower()
        original_message = user_request.message
        
        # Advanced keyword analysis with scoring
        intent_scores = {
            IntentType.SECURITY: 0,
            IntentType.SYSTEM: 0,
            IntentType.ACCESS: 0,
            IntentType.QUERY: 0,
            IntentType.COMPLIANCE: 0
        }
        
        # Security keywords
        security_keywords = {
            "block": 3, "suspicious": 2, "attack": 3, "threat": 3, "malicious": 3,
            "firewall": 2, "intrusion": 3, "breach": 3, "hack": 3, "virus": 2,
            "malware": 3, "unauthorized": 2, "security": 2, "alert": 1
        }
        
        # System keywords
        system_keywords = {
            "shutdown": 3, "restart": 2, "delete": 2, "remove": 2, "install": 2,
            "update": 2, "deploy": 2, "configure": 2, "execute": 2, "run": 1,
            "start": 1, "stop": 2, "backup": 2, "restore": 2, "server": 1,
            "system": 1, "service": 1, "process": 1
        }
        
        # Access keywords  
        access_keywords = {
            "access": 3, "permission": 3, "grant": 3, "allow": 2, "deny": 2,
            "revoke": 3, "role": 2, "user": 1, "password": 2, "login": 2,
            "authenticate": 2, "authorize": 2, "employee": 2, "hire": 2,
            "terminate": 2, "onboard": 2, "offboard": 2
        }
        
        # Query keywords
        query_keywords = {
            "query": 3, "show": 2, "list": 2, "get": 2, "find": 2, "view": 2,
            "display": 2, "search": 2, "status": 2, "info": 1, "report": 2,
            "what": 1, "how": 1, "check": 2, "monitor": 2
        }
        
        # Compliance keywords
        compliance_keywords = {
            "comply": 3, "audit": 3, "report": 2, "verify": 2, "compliance": 3,
            "regulation": 2, "policy": 2, "standard": 2, "gdpr": 3, "hipaa": 3,
            "sox": 3, "pci": 3, "review": 2, "quarterly": 2, "annual": 2
        }
        
        # HR/Business keywords (maps to ACCESS or SYSTEM)
        hr_keywords = {
            "vacation": 2, "leave": 2, "salary": 2, "payroll": 2, "bonus": 2,
            "meeting": 1, "schedule": 2, "appointment": 1, "team": 1,
            "project": 1, "budget": 2, "expense": 2, "travel": 1
        }
        
        # Calculate scores
        words = message.split()
        for word in words:
            word_clean = re.sub(r'[^\w]', '', word)
            if word_clean in security_keywords:
                intent_scores[IntentType.SECURITY] += security_keywords[word_clean]
            if word_clean in system_keywords:
                intent_scores[IntentType.SYSTEM] += system_keywords[word_clean]
            if word_clean in access_keywords:
                intent_scores[IntentType.ACCESS] += access_keywords[word_clean]
            if word_clean in query_keywords:
                intent_scores[IntentType.QUERY] += query_keywords[word_clean]
            if word_clean in compliance_keywords:
                intent_scores[IntentType.COMPLIANCE] += compliance_keywords[word_clean]
            if word_clean in hr_keywords:
                intent_scores[IntentType.ACCESS] += hr_keywords[word_clean] * 0.5
                intent_scores[IntentType.SYSTEM] += hr_keywords[word_clean] * 0.5
        
        # Find best intent
        max_score = max(intent_scores.values())
        if max_score == 0:
            intent_type = IntentType.QUERY
            base_confidence = 0.55
        else:
            intent_type = max(intent_scores, key=intent_scores.get)
            # Calculate confidence based on score strength
            total_score = sum(intent_scores.values())
            if total_score > 0:
                base_confidence = 0.5 + (max_score / total_score) * 0.4
            else:
                base_confidence = 0.55
        
        # Add variance
        confidence = round(base_confidence + random.uniform(-0.05, 0.1), 2)
        confidence = max(0.45, min(0.95, confidence))
        
        # Determine goal and actions based on intent
        goal_actions_map = {
            IntentType.SECURITY: {
                "goal": self._generate_security_goal(message),
                "actions": self._select_security_actions(message)
            },
            IntentType.SYSTEM: {
                "goal": self._generate_system_goal(message),
                "actions": self._select_system_actions(message)
            },
            IntentType.ACCESS: {
                "goal": self._generate_access_goal(message),
                "actions": self._select_access_actions(message)
            },
            IntentType.QUERY: {
                "goal": self._generate_query_goal(message),
                "actions": self._select_query_actions(message)
            },
            IntentType.COMPLIANCE: {
                "goal": self._generate_compliance_goal(message),
                "actions": self._select_compliance_actions(message)
            }
        }
        
        goal = goal_actions_map[intent_type]["goal"]
        actions = goal_actions_map[intent_type]["actions"]
        
        # Extract time constraints
        time_window = {}
        if preprocessed_data and "time_references" in preprocessed_data:
            time_window = preprocessed_data["time_references"]
        
        # Extract entities
        entities = Entities(
            targets=self._extract_ips(message),
            subjects=self._extract_names(original_message),
            objects=self._extract_objects(message)
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
            confidence=confidence,
            reasoning=f"Analyzed request: '{user_request.message[:50]}...' | Intent: {intent_type.value} (score: {max_score:.1f})"
        )
    
    def _generate_security_goal(self, message: str) -> str:
        if "block" in message:
            return "Block malicious network traffic"
        elif "intrusion" in message or "breach" in message:
            return "Investigate and contain security breach"
        elif "firewall" in message:
            return "Update firewall security rules"
        return "Respond to security threat"
    
    def _generate_system_goal(self, message: str) -> str:
        if "shutdown" in message or "restart" in message:
            return "Execute system maintenance operation"
        elif "delete" in message or "remove" in message:
            return "Remove specified system resources"
        elif "backup" in message:
            return "Create system backup"
        elif "deploy" in message or "install" in message:
            return "Deploy new system components"
        elif "schedule" in message or "meeting" in message:
            return "Schedule organizational activity"
        elif "email" in message or "send" in message:
            return "Send communication to recipients"
        return "Execute system operation"
    
    def _generate_access_goal(self, message: str) -> str:
        if "grant" in message or "allow" in message:
            return "Grant access permissions"
        elif "revoke" in message or "deny" in message:
            return "Revoke access permissions"
        elif "hire" in message or "onboard" in message:
            return "Onboard new employee"
        elif "terminate" in message or "offboard" in message:
            return "Process employee termination"
        elif "vacation" in message or "leave" in message:
            return "Process leave request"
        elif "salary" in message or "payroll" in message:
            return "Process compensation update"
        return "Manage access control"
    
    def _generate_query_goal(self, message: str) -> str:
        if "status" in message:
            return "Retrieve system status"
        elif "log" in message:
            return "Fetch system logs"
        elif "report" in message:
            return "Generate requested report"
        return "Query system information"
    
    def _generate_compliance_goal(self, message: str) -> str:
        if "audit" in message:
            return "Conduct compliance audit"
        elif "gdpr" in message or "hipaa" in message or "pci" in message:
            return "Verify regulatory compliance"
        return "Ensure policy compliance"
    
    def _select_security_actions(self, message: str) -> list:
        actions = []
        if "block" in message:
            actions.append("BLOCK_IP")
        if "firewall" in message:
            actions.append("UPDATE_FIREWALL_RULES")
        if "scan" in message:
            actions.append("SECURITY_SCAN")
        if not actions:
            actions = ["INVESTIGATE_THREAT", "LOG_SECURITY_EVENT"]
        return actions
    
    def _select_system_actions(self, message: str) -> list:
        actions = []
        if "shutdown" in message:
            actions.append("SYSTEM_SHUTDOWN")
        if "restart" in message:
            actions.append("SYSTEM_RESTART")
        if "delete" in message:
            actions.append("DELETE_RESOURCE")
        if "backup" in message:
            actions.append("CREATE_BACKUP")
        if "deploy" in message or "install" in message:
            actions.append("DEPLOY_APPLICATION")
        if "email" in message or "send" in message:
            actions.append("SEND_NOTIFICATION")
        if "schedule" in message or "meeting" in message:
            actions.append("SCHEDULE_EVENT")
        if not actions:
            actions = ["EXECUTE_COMMAND"]
        return actions
    
    def _select_access_actions(self, message: str) -> list:
        actions = []
        if "grant" in message or "allow" in message:
            actions.append("GRANT_ACCESS")
        if "revoke" in message or "deny" in message:
            actions.append("REVOKE_ACCESS")
        if "hire" in message or "onboard" in message:
            actions.extend(["CREATE_USER_ACCOUNT", "ASSIGN_ROLE", "PROVISION_RESOURCES"])
        if "terminate" in message:
            actions.extend(["DISABLE_ACCOUNT", "REVOKE_ALL_ACCESS", "ARCHIVE_DATA"])
        if "vacation" in message or "leave" in message:
            actions.extend(["UPDATE_LEAVE_BALANCE", "NOTIFY_MANAGER", "UPDATE_CALENDAR"])
        if "salary" in message:
            actions.extend(["UPDATE_COMPENSATION", "NOTIFY_PAYROLL", "LOG_CHANGE"])
        if not actions:
            actions = ["UPDATE_ACCESS_CONTROL"]
        return actions
    
    def _select_query_actions(self, message: str) -> list:
        actions = []
        if "log" in message:
            actions.append("FETCH_LOGS")
        if "status" in message:
            actions.append("CHECK_STATUS")
        if "report" in message:
            actions.append("GENERATE_REPORT")
        if not actions:
            actions = ["QUERY_DATABASE"]
        return actions
    
    def _select_compliance_actions(self, message: str) -> list:
        actions = []
        if "audit" in message:
            actions.append("GENERATE_AUDIT_REPORT")
        if "verify" in message:
            actions.append("VERIFY_COMPLIANCE")
        if not actions:
            actions = ["RUN_COMPLIANCE_CHECK", "GENERATE_COMPLIANCE_REPORT"]
        return actions
    
    def _extract_names(self, text: str) -> list:
        """Extract potential person names from text"""
        import re
        # Simple pattern for capitalized words that might be names
        name_pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?\b'
        potential_names = re.findall(name_pattern, text)
        # Filter out common non-name words
        exclude = {'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday',
                   'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August',
                   'September', 'October', 'November', 'December', 'The', 'This', 'That'}
        return [n for n in potential_names if n not in exclude][:3]
    
    def _extract_objects(self, text: str) -> list:
        """Extract objects/resources from text"""
        objects = []
        # Look for quoted strings
        import re
        quoted = re.findall(r'"([^"]+)"', text)
        objects.extend(quoted)
        # Look for specific patterns
        if "server" in text:
            objects.append("server")
        if "database" in text:
            objects.append("database")
        if "file" in text:
            objects.append("files")
        return objects[:5]
    
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
