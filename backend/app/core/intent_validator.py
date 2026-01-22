"""
Intent Validator Service

Validates and scores parsed intents for correctness and completeness.
"""

import logging
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

from ..schemas.request_schema import LLMOutput, IntentType, Entities, Constraints

logger = logging.getLogger(__name__)


class ValidationSeverity(Enum):
    """Severity levels for validation issues"""
    ERROR = "error"      # Must be fixed
    WARNING = "warning"  # Should be fixed
    INFO = "info"        # Nice to have


@dataclass
class ValidationIssue:
    """Represents a validation issue"""
    severity: ValidationSeverity
    code: str
    message: str
    field: Optional[str] = None
    suggestion: Optional[str] = None


@dataclass
class ValidationResult:
    """Result of intent validation"""
    is_valid: bool
    score: float  # 0.0 to 1.0
    issues: List[ValidationIssue]
    suggestions: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_valid": self.is_valid,
            "score": self.score,
            "issues": [
                {
                    "severity": i.severity.value,
                    "code": i.code,
                    "message": i.message,
                    "field": i.field,
                    "suggestion": i.suggestion
                }
                for i in self.issues
            ],
            "suggestions": self.suggestions
        }


class IntentValidator:
    """
    Validates parsed intents for correctness and completeness
    
    Features:
    - Schema validation
    - Business rule validation
    - Completeness scoring
    - Suggestions for improvement
    """
    
    # Required entities per intent type
    REQUIRED_ENTITIES = {
        IntentType.SECURITY: {
            "targets": ["IP addresses", "systems", "or resources to protect"],
        },
        IntentType.ACCESS: {
            "subjects": ["users", "or roles to grant/revoke access"],
            "objects": ["resources", "or permissions to manage"],
        },
        IntentType.QUERY: {
            # Queries are more flexible
        },
        IntentType.SYSTEM: {
            "targets": ["systems", "services", "or resources to operate on"],
        },
        IntentType.COMPLIANCE: {
            # Compliance is more flexible
        }
    }
    
    # Valid actions per intent type
    VALID_ACTIONS = {
        IntentType.SECURITY: [
            "BLOCK_IP", "ALLOW_IP", "UPDATE_FIREWALL_RULES", "SCAN_NETWORK",
            "ISOLATE_SYSTEM", "ALERT", "NOTIFY"
        ],
        IntentType.ACCESS: [
            "GRANT_ACCESS", "REVOKE_ACCESS", "MODIFY_PERMISSIONS",
            "CREATE_USER", "DELETE_USER", "RESET_PASSWORD"
        ],
        IntentType.QUERY: [
            "QUERY_DATABASE", "FETCH_LOGS", "GET_STATUS", "GENERATE_REPORT",
            "LIST_ITEMS", "SEARCH", "ANALYZE"
        ],
        IntentType.SYSTEM: [
            "EXECUTE_COMMAND", "SCHEDULE_TASK", "BACKUP_DATA", "RESTORE_DATA",
            "RESTART_SERVICE", "UPDATE_CONFIG", "SHUTDOWN", "START_SERVICE"
        ],
        IntentType.COMPLIANCE: [
            "GENERATE_AUDIT_REPORT", "VERIFY_COMPLIANCE", "ENFORCE_POLICY",
            "CHECK_POLICY", "EXPORT_AUDIT_LOG"
        ]
    }
    
    def __init__(self):
        """Initialize the intent validator"""
        self.custom_rules: List[callable] = []
    
    def add_custom_rule(self, rule: callable):
        """Add a custom validation rule"""
        self.custom_rules.append(rule)
    
    def validate(self, intent: LLMOutput) -> ValidationResult:
        """
        Validate an intent
        
        Args:
            intent: The parsed intent to validate
            
        Returns:
            ValidationResult with validation status and issues
        """
        issues: List[ValidationIssue] = []
        suggestions: List[str] = []
        
        # 1. Validate required fields
        field_issues = self._validate_required_fields(intent)
        issues.extend(field_issues)
        
        # 2. Validate intent type
        type_issues = self._validate_intent_type(intent)
        issues.extend(type_issues)
        
        # 3. Validate entities
        entity_issues, entity_suggestions = self._validate_entities(intent)
        issues.extend(entity_issues)
        suggestions.extend(entity_suggestions)
        
        # 4. Validate actions
        action_issues, action_suggestions = self._validate_actions(intent)
        issues.extend(action_issues)
        suggestions.extend(action_suggestions)
        
        # 5. Validate constraints
        constraint_issues = self._validate_constraints(intent)
        issues.extend(constraint_issues)
        
        # 6. Validate confidence
        confidence_issues = self._validate_confidence(intent)
        issues.extend(confidence_issues)
        
        # 7. Run custom rules
        for rule in self.custom_rules:
            try:
                custom_issues = rule(intent)
                if custom_issues:
                    issues.extend(custom_issues)
            except Exception as e:
                logger.warning(f"Custom rule failed: {e}")
        
        # Calculate score
        score = self._calculate_score(intent, issues)
        
        # Determine validity
        is_valid = not any(i.severity == ValidationSeverity.ERROR for i in issues)
        
        return ValidationResult(
            is_valid=is_valid,
            score=score,
            issues=issues,
            suggestions=suggestions
        )
    
    def _validate_required_fields(self, intent: LLMOutput) -> List[ValidationIssue]:
        """Validate required fields are present"""
        issues = []
        
        # Goal is required
        if not intent.goal or len(intent.goal.strip()) < 3:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                code="MISSING_GOAL",
                message="Intent must have a clear goal",
                field="goal",
                suggestion="Provide a descriptive goal for what the user wants to achieve"
            ))
        
        # Actions are required
        if not intent.requested_actions:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                code="NO_ACTIONS",
                message="No actions specified for intent",
                field="requested_actions",
                suggestion="Specify at least one action to perform"
            ))
        
        return issues
    
    def _validate_intent_type(self, intent: LLMOutput) -> List[ValidationIssue]:
        """Validate intent type is valid"""
        issues = []
        
        valid_types = [t for t in IntentType]
        if intent.intent_type not in valid_types:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                code="INVALID_INTENT_TYPE",
                message=f"Invalid intent type: {intent.intent_type}",
                field="intent_type",
                suggestion=f"Use one of: {[t.value for t in valid_types]}"
            ))
        
        return issues
    
    def _validate_entities(self, intent: LLMOutput) -> Tuple[List[ValidationIssue], List[str]]:
        """Validate entities are appropriate for intent type"""
        issues = []
        suggestions = []
        
        required = self.REQUIRED_ENTITIES.get(intent.intent_type, {})
        
        for entity_type, description in required.items():
            entities = getattr(intent.entities, entity_type, [])
            if not entities:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    code=f"MISSING_{entity_type.upper()}",
                    message=f"Missing {entity_type} for {intent.intent_type.value} intent",
                    field=f"entities.{entity_type}",
                    suggestion=f"Specify {', '.join(description)}"
                ))
                suggestions.append(f"Please specify {', '.join(description)}")
        
        return issues, suggestions
    
    def _validate_actions(self, intent: LLMOutput) -> Tuple[List[ValidationIssue], List[str]]:
        """Validate actions are appropriate for intent type"""
        issues = []
        suggestions = []
        
        valid_actions = self.VALID_ACTIONS.get(intent.intent_type, [])
        
        for action in intent.requested_actions:
            if action not in valid_actions:
                # Check if it's valid for any type
                all_valid = set()
                for actions in self.VALID_ACTIONS.values():
                    all_valid.update(actions)
                
                if action in all_valid:
                    issues.append(ValidationIssue(
                        severity=ValidationSeverity.WARNING,
                        code="ACTION_TYPE_MISMATCH",
                        message=f"Action {action} doesn't match intent type {intent.intent_type.value}",
                        field="requested_actions",
                        suggestion=f"Consider using actions: {valid_actions[:3]}"
                    ))
                else:
                    issues.append(ValidationIssue(
                        severity=ValidationSeverity.INFO,
                        code="UNKNOWN_ACTION",
                        message=f"Unknown action: {action}",
                        field="requested_actions"
                    ))
        
        # Suggest common actions if none specified
        if not intent.requested_actions and valid_actions:
            suggestions.append(f"Common actions for {intent.intent_type.value}: {', '.join(valid_actions[:3])}")
        
        return issues, suggestions
    
    def _validate_constraints(self, intent: LLMOutput) -> List[ValidationIssue]:
        """Validate constraints are well-formed"""
        issues = []
        
        if intent.constraints:
            # Validate time window
            time_window = intent.constraints.time_window
            if time_window:
                if "start" in time_window and "end" in time_window:
                    # Could add date parsing validation here
                    pass
            
            # Validate thresholds
            thresholds = intent.constraints.thresholds
            if thresholds:
                for key, value in thresholds.items():
                    if not isinstance(value, (int, float)):
                        issues.append(ValidationIssue(
                            severity=ValidationSeverity.WARNING,
                            code="INVALID_THRESHOLD",
                            message=f"Threshold {key} should be numeric",
                            field=f"constraints.thresholds.{key}"
                        ))
        
        return issues
    
    def _validate_confidence(self, intent: LLMOutput) -> List[ValidationIssue]:
        """Validate confidence score"""
        issues = []
        
        if intent.confidence < 0 or intent.confidence > 1:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                code="INVALID_CONFIDENCE",
                message="Confidence must be between 0 and 1",
                field="confidence"
            ))
        elif intent.confidence < 0.3:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                code="LOW_CONFIDENCE",
                message="Very low confidence in intent interpretation",
                field="confidence",
                suggestion="Consider asking for clarification"
            ))
        elif intent.confidence < 0.5:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.INFO,
                code="MODERATE_CONFIDENCE",
                message="Moderate confidence - consider verification",
                field="confidence"
            ))
        
        return issues
    
    def _calculate_score(self, intent: LLMOutput, issues: List[ValidationIssue]) -> float:
        """Calculate overall validation score"""
        base_score = 1.0
        
        # Deduct for issues
        for issue in issues:
            if issue.severity == ValidationSeverity.ERROR:
                base_score -= 0.3
            elif issue.severity == ValidationSeverity.WARNING:
                base_score -= 0.1
            elif issue.severity == ValidationSeverity.INFO:
                base_score -= 0.02
        
        # Bonus for high confidence
        if intent.confidence > 0.8:
            base_score += 0.1
        
        # Bonus for complete entities
        if intent.entities.targets or intent.entities.subjects:
            base_score += 0.05
        
        # Bonus for actions
        if intent.requested_actions:
            base_score += 0.05
        
        return max(0.0, min(1.0, base_score))
    
    def is_actionable(self, intent: LLMOutput) -> Tuple[bool, str]:
        """
        Check if an intent can be acted upon
        
        Returns:
            Tuple of (is_actionable, reason)
        """
        result = self.validate(intent)
        
        if not result.is_valid:
            errors = [i for i in result.issues if i.severity == ValidationSeverity.ERROR]
            return False, f"Validation errors: {[e.message for e in errors]}"
        
        if intent.confidence < 0.3:
            return False, "Confidence too low to proceed"
        
        if not intent.requested_actions:
            return False, "No actions specified"
        
        return True, "Intent is actionable"
    
    def suggest_clarifications(self, intent: LLMOutput) -> List[str]:
        """
        Generate clarification questions for ambiguous intents
        """
        questions = []
        result = self.validate(intent)
        
        for issue in result.issues:
            if issue.severity in [ValidationSeverity.ERROR, ValidationSeverity.WARNING]:
                if "MISSING" in issue.code:
                    if "subjects" in issue.code.lower():
                        questions.append("Which user or role should this apply to?")
                    elif "targets" in issue.code.lower():
                        questions.append("Which system, IP, or resource should this target?")
                    elif "objects" in issue.code.lower():
                        questions.append("Which resource or permission should be affected?")
        
        if intent.confidence < 0.5:
            questions.append("Could you provide more details about what you want to do?")
        
        return questions


class IntentEnricher:
    """
    Enriches intents with additional context and inferences
    """
    
    def __init__(self, validator: IntentValidator):
        self.validator = validator
    
    def enrich(self, intent: LLMOutput, context: Dict[str, Any] = None) -> LLMOutput:
        """
        Enrich an intent with additional information
        
        Args:
            intent: The intent to enrich
            context: Additional context (user info, session history, etc.)
            
        Returns:
            Enriched intent
        """
        # Add default actions if missing
        if not intent.requested_actions:
            intent.requested_actions = self._suggest_default_actions(intent)
        
        # Infer missing entities from context
        if context:
            intent = self._infer_entities_from_context(intent, context)
        
        # Add inferred constraints
        intent = self._infer_constraints(intent)
        
        return intent
    
    def _suggest_default_actions(self, intent: LLMOutput) -> List[str]:
        """Suggest default actions based on intent type"""
        defaults = {
            IntentType.SECURITY: ["SCAN_NETWORK"],
            IntentType.ACCESS: ["GRANT_ACCESS"],
            IntentType.QUERY: ["QUERY_DATABASE"],
            IntentType.SYSTEM: ["EXECUTE_COMMAND"],
            IntentType.COMPLIANCE: ["VERIFY_COMPLIANCE"]
        }
        return defaults.get(intent.intent_type, ["ANALYZE"])
    
    def _infer_entities_from_context(
        self,
        intent: LLMOutput,
        context: Dict[str, Any]
    ) -> LLMOutput:
        """Infer entities from conversation context"""
        
        # If no subjects but user context exists
        if not intent.entities.subjects and "user_name" in context:
            # Don't auto-fill - this needs to be explicit
            pass
        
        # Use entities from previous turns
        if "previous_entities" in context:
            prev = context["previous_entities"]
            
            # Fill in missing targets
            if not intent.entities.targets and "targets" in prev:
                intent.entities.targets = prev["targets"]
            
            # Fill in missing subjects  
            if not intent.entities.subjects and "subjects" in prev:
                intent.entities.subjects = prev["subjects"]
        
        return intent
    
    def _infer_constraints(self, intent: LLMOutput) -> LLMOutput:
        """Infer constraints based on intent and actions"""
        
        # If time-sensitive action but no time window, add default
        time_sensitive_actions = ["FETCH_LOGS", "SCAN_NETWORK", "GENERATE_REPORT"]
        
        if any(a in intent.requested_actions for a in time_sensitive_actions):
            if not intent.constraints.time_window:
                intent.constraints.time_window = {
                    "start": "last 24 hours",
                    "end": "now"
                }
        
        return intent


# Singleton instances
_validator_instance: Optional[IntentValidator] = None
_enricher_instance: Optional[IntentEnricher] = None


def get_intent_validator() -> IntentValidator:
    """Get or create singleton intent validator"""
    global _validator_instance
    if _validator_instance is None:
        _validator_instance = IntentValidator()
    return _validator_instance


def get_intent_enricher() -> IntentEnricher:
    """Get or create singleton intent enricher"""
    global _enricher_instance
    if _enricher_instance is None:
        _enricher_instance = IntentEnricher(get_intent_validator())
    return _enricher_instance
