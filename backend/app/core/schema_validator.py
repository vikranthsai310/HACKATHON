"""
Schema Validator for HRM Decision System

Validates LLM output against expected schema,
ensures data integrity and security constraints.
"""

from typing import Dict, Any, Tuple, List, Optional
from datetime import datetime
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SchemaValidator:
    """
    Validates LLM output against expected schema.
    
    Performs structural validation, type checking,
    and security constraint verification.
    """
    
    # Valid intent types
    VALID_INTENTS = ["SECURITY", "COMPLIANCE", "ACCESS", "SYSTEM", "QUERY"]
    
    # Valid actions that can be requested
    VALID_ACTIONS = [
        # Security actions
        "BLOCK_IP", "ALLOW_IP", "QUARANTINE", "ISOLATE",
        # Notification actions
        "NOTIFY", "ALERT", "ESCALATE", "LOG",
        # Access control actions
        "GRANT_ACCESS", "REVOKE_ACCESS", "MODIFY_PERMISSIONS",
        # Analysis actions
        "SCAN", "FILTER", "ANALYZE", "INVESTIGATE",
        # System actions
        "SCHEDULE", "EXECUTE", "RESTART", "BACKUP",
        # Query actions
        "FETCH", "REPORT", "AGGREGATE", "EXPORT"
    ]
    
    # Required fields in LLM output
    REQUIRED_FIELDS = ["intent_type", "goal", "requested_actions", "confidence"]
    
    # Risk thresholds
    HIGH_RISK_ACTIONS = ["BLOCK_IP", "QUARANTINE", "ISOLATE", "REVOKE_ACCESS", "RESTART"]
    
    def __init__(self):
        """Initialize the schema validator"""
        self.validation_rules = self._init_validation_rules()
        
    def _init_validation_rules(self) -> Dict[str, callable]:
        """Initialize validation rules for each field"""
        return {
            "intent_type": self._validate_intent_type,
            "goal": self._validate_goal,
            "constraints": self._validate_constraints,
            "entities": self._validate_entities,
            "requested_actions": self._validate_actions,
            "confidence": self._validate_confidence
        }
    
    def validate(self, llm_output: Dict[str, Any]) -> Tuple[bool, str, Dict]:
        """
        Validate LLM output against schema.
        
        Args:
            llm_output: Dictionary containing LLM interpretation
            
        Returns:
            Tuple of (is_valid, error_message, validated_output)
        """
        errors = []
        warnings = []
        
        # Check required fields
        for field in self.REQUIRED_FIELDS:
            if field not in llm_output:
                errors.append(f"Missing required field: {field}")
        
        if errors:
            logger.warning(f"Validation failed - missing fields: {errors}")
            return False, "; ".join(errors), {}
        
        # Validate each field with its specific rule
        validated_output = {}
        for field, value in llm_output.items():
            if field in self.validation_rules:
                is_valid, error, validated_value = self.validation_rules[field](value)
                if not is_valid:
                    errors.append(error)
                else:
                    validated_output[field] = validated_value
            else:
                # Pass through unknown fields with warning
                validated_output[field] = value
                warnings.append(f"Unknown field passed through: {field}")
        
        if warnings:
            logger.info(f"Validation warnings: {warnings}")
        
        if errors:
            logger.warning(f"Validation failed: {errors}")
            return False, "; ".join(errors), {}
        
        # Add metadata
        validated_output["_validated_at"] = datetime.now().isoformat()
        validated_output["_validator_version"] = "1.0.0"
        
        logger.info(f"Validation successful for intent: {validated_output.get('intent_type')}")
        return True, "", validated_output
    
    def _validate_intent_type(self, value: str) -> Tuple[bool, str, str]:
        """Validate intent type"""
        if value not in self.VALID_INTENTS:
            return False, f"Invalid intent_type: {value}. Must be one of: {self.VALID_INTENTS}", None
        return True, "", value
    
    def _validate_goal(self, value: str) -> Tuple[bool, str, str]:
        """Validate goal field"""
        if not isinstance(value, str):
            return False, f"Goal must be a string, got: {type(value).__name__}", None
        if len(value.strip()) < 5:
            return False, "Goal must be at least 5 characters", None
        if len(value) > 500:
            return False, "Goal must not exceed 500 characters", None
        return True, "", value.strip()
    
    def _validate_constraints(self, value: Dict) -> Tuple[bool, str, Dict]:
        """Validate constraints object"""
        if not isinstance(value, dict):
            return False, f"Constraints must be a dictionary, got: {type(value).__name__}", None
        
        # Validate time_window if present
        if "time_window" in value:
            tw = value["time_window"]
            if not isinstance(tw, dict):
                return False, "time_window must be a dictionary", None
        
        return True, "", value
    
    def _validate_entities(self, value: Dict) -> Tuple[bool, str, Dict]:
        """Validate entities object"""
        if not isinstance(value, dict):
            return False, f"Entities must be a dictionary, got: {type(value).__name__}", None
        
        # Ensure expected keys exist with default values
        validated = {
            "targets": value.get("targets", []),
            "subjects": value.get("subjects", []),
            "objects": value.get("objects", [])
        }
        
        # Validate that lists contain strings
        for key, items in validated.items():
            if not isinstance(items, list):
                return False, f"entities.{key} must be a list", None
            for item in items:
                if not isinstance(item, str):
                    return False, f"entities.{key} must contain strings only", None
        
        return True, "", validated
    
    def _validate_actions(self, value: List[str]) -> Tuple[bool, str, List[str]]:
        """Validate requested actions"""
        if not isinstance(value, list):
            return False, f"requested_actions must be a list, got: {type(value).__name__}", None
        
        if len(value) == 0:
            return False, "At least one action must be requested", None
        
        validated_actions = []
        unknown_actions = []
        
        for action in value:
            # Handle ACTION:param format
            action_name = action.split(":")[0].upper()
            
            if action_name not in self.VALID_ACTIONS:
                unknown_actions.append(action_name)
            else:
                validated_actions.append(action)
        
        if unknown_actions:
            return False, f"Unknown actions: {unknown_actions}. Valid actions: {self.VALID_ACTIONS}", None
        
        return True, "", validated_actions
    
    def _validate_confidence(self, value: float) -> Tuple[bool, str, float]:
        """Validate confidence score"""
        try:
            conf = float(value)
        except (TypeError, ValueError):
            return False, f"Confidence must be a number, got: {type(value).__name__}", None
        
        if not (0 <= conf <= 1):
            return False, f"Confidence must be between 0 and 1, got: {conf}", None
        
        return True, "", round(conf, 4)
    
    def assess_risk(self, validated_output: Dict) -> str:
        """
        Assess risk level of validated output.
        
        Args:
            validated_output: Validated LLM output
            
        Returns:
            Risk level: LOW, MEDIUM, HIGH, or CRITICAL
        """
        actions = validated_output.get("requested_actions", [])
        confidence = validated_output.get("confidence", 0)
        
        # Check for high-risk actions
        high_risk_count = sum(1 for a in actions if a.split(":")[0] in self.HIGH_RISK_ACTIONS)
        
        if high_risk_count >= 3 or confidence < 0.5:
            return "CRITICAL"
        elif high_risk_count >= 2 or confidence < 0.7:
            return "HIGH"  
        elif high_risk_count >= 1 or confidence < 0.85:
            return "MEDIUM"
        else:
            return "LOW"
    
    def to_json(self, validated_output: Dict) -> str:
        """Convert validated output to JSON string"""
        return json.dumps(validated_output, indent=2, default=str)
