"""
Action Mapping Service

Maps parsed intents to specific system actions with parameters.
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

from ..schemas.request_schema import (
    LLMOutput, IntentType, HRMInput,
    OperationalAction, OperationalLevel,
    StrategicLevel, TacticalLevel, RiskLevel
)

logger = logging.getLogger(__name__)


class ActionCategory(Enum):
    """Categories of actions"""
    READ = "read"           # Read-only operations
    WRITE = "write"         # Modify data
    EXECUTE = "execute"     # Execute commands
    ADMIN = "admin"         # Administrative operations
    CRITICAL = "critical"   # Critical/dangerous operations


@dataclass
class ActionDefinition:
    """Defines an action and its properties"""
    name: str
    category: ActionCategory
    description: str
    required_params: List[str] = field(default_factory=list)
    optional_params: List[str] = field(default_factory=list)
    requires_confirmation: bool = False
    requires_authorization: bool = False
    risk_level: RiskLevel = RiskLevel.MEDIUM
    fallback_action: Optional[str] = None
    timeout_seconds: int = 60


@dataclass
class MappedAction:
    """Result of action mapping"""
    action: str
    params: Dict[str, Any]
    conditions: List[str]
    fallback: Optional[str]
    category: ActionCategory
    risk_level: RiskLevel
    requires_confirmation: bool
    description: str


class ActionMapper:
    """
    Maps intents to specific system actions
    
    Features:
    - Intent-to-action mapping
    - Parameter extraction
    - Risk assessment
    - Execution ordering
    """
    
    # Action definitions
    ACTIONS: Dict[str, ActionDefinition] = {
        # Security Actions
        "BLOCK_IP": ActionDefinition(
            name="BLOCK_IP",
            category=ActionCategory.CRITICAL,
            description="Block network traffic from specified IP addresses",
            required_params=["ip_addresses"],
            optional_params=["duration", "reason"],
            requires_confirmation=True,
            requires_authorization=True,
            risk_level=RiskLevel.HIGH,
            fallback_action="LOG_BLOCKED_ATTEMPT"
        ),
        "ALLOW_IP": ActionDefinition(
            name="ALLOW_IP",
            category=ActionCategory.ADMIN,
            description="Whitelist IP addresses",
            required_params=["ip_addresses"],
            optional_params=["duration", "reason"],
            requires_authorization=True,
            risk_level=RiskLevel.MEDIUM
        ),
        "UPDATE_FIREWALL_RULES": ActionDefinition(
            name="UPDATE_FIREWALL_RULES",
            category=ActionCategory.CRITICAL,
            description="Modify firewall configuration",
            required_params=["rules"],
            requires_confirmation=True,
            requires_authorization=True,
            risk_level=RiskLevel.HIGH
        ),
        "SCAN_NETWORK": ActionDefinition(
            name="SCAN_NETWORK",
            category=ActionCategory.READ,
            description="Scan network for threats or anomalies",
            optional_params=["scope", "depth"],
            risk_level=RiskLevel.LOW
        ),
        "ISOLATE_SYSTEM": ActionDefinition(
            name="ISOLATE_SYSTEM",
            category=ActionCategory.CRITICAL,
            description="Isolate a compromised system from the network",
            required_params=["system_id"],
            requires_confirmation=True,
            requires_authorization=True,
            risk_level=RiskLevel.CRITICAL
        ),
        
        # Access Actions
        "GRANT_ACCESS": ActionDefinition(
            name="GRANT_ACCESS",
            category=ActionCategory.ADMIN,
            description="Grant access permissions to users",
            required_params=["subjects", "resources"],
            optional_params=["permissions", "duration"],
            requires_authorization=True,
            risk_level=RiskLevel.MEDIUM
        ),
        "REVOKE_ACCESS": ActionDefinition(
            name="REVOKE_ACCESS",
            category=ActionCategory.ADMIN,
            description="Revoke access permissions from users",
            required_params=["subjects"],
            optional_params=["resources", "reason"],
            requires_authorization=True,
            risk_level=RiskLevel.MEDIUM
        ),
        "MODIFY_PERMISSIONS": ActionDefinition(
            name="MODIFY_PERMISSIONS",
            category=ActionCategory.ADMIN,
            description="Modify existing permissions",
            required_params=["subjects", "permissions"],
            requires_authorization=True,
            risk_level=RiskLevel.MEDIUM
        ),
        "CREATE_USER": ActionDefinition(
            name="CREATE_USER",
            category=ActionCategory.ADMIN,
            description="Create a new user account",
            required_params=["username"],
            optional_params=["email", "role"],
            requires_authorization=True,
            risk_level=RiskLevel.MEDIUM
        ),
        "DELETE_USER": ActionDefinition(
            name="DELETE_USER",
            category=ActionCategory.CRITICAL,
            description="Delete a user account",
            required_params=["username"],
            requires_confirmation=True,
            requires_authorization=True,
            risk_level=RiskLevel.HIGH
        ),
        
        # Query Actions
        "QUERY_DATABASE": ActionDefinition(
            name="QUERY_DATABASE",
            category=ActionCategory.READ,
            description="Query data from database",
            optional_params=["filters", "time_window", "limit"],
            risk_level=RiskLevel.LOW
        ),
        "FETCH_LOGS": ActionDefinition(
            name="FETCH_LOGS",
            category=ActionCategory.READ,
            description="Retrieve log entries",
            optional_params=["log_type", "time_window", "filters"],
            risk_level=RiskLevel.LOW
        ),
        "GET_STATUS": ActionDefinition(
            name="GET_STATUS",
            category=ActionCategory.READ,
            description="Get system or service status",
            optional_params=["system", "service"],
            risk_level=RiskLevel.LOW
        ),
        "GENERATE_REPORT": ActionDefinition(
            name="GENERATE_REPORT",
            category=ActionCategory.READ,
            description="Generate a report",
            required_params=["report_type"],
            optional_params=["time_window", "format"],
            risk_level=RiskLevel.LOW
        ),
        
        # System Actions
        "EXECUTE_COMMAND": ActionDefinition(
            name="EXECUTE_COMMAND",
            category=ActionCategory.EXECUTE,
            description="Execute a system command",
            required_params=["command"],
            requires_confirmation=True,
            requires_authorization=True,
            risk_level=RiskLevel.HIGH
        ),
        "SCHEDULE_TASK": ActionDefinition(
            name="SCHEDULE_TASK",
            category=ActionCategory.WRITE,
            description="Schedule a task for later execution",
            required_params=["task", "schedule"],
            requires_authorization=True,
            risk_level=RiskLevel.MEDIUM
        ),
        "BACKUP_DATA": ActionDefinition(
            name="BACKUP_DATA",
            category=ActionCategory.WRITE,
            description="Create a data backup",
            optional_params=["scope", "destination"],
            risk_level=RiskLevel.LOW
        ),
        "RESTORE_DATA": ActionDefinition(
            name="RESTORE_DATA",
            category=ActionCategory.CRITICAL,
            description="Restore data from backup",
            required_params=["backup_id"],
            requires_confirmation=True,
            requires_authorization=True,
            risk_level=RiskLevel.CRITICAL
        ),
        "RESTART_SERVICE": ActionDefinition(
            name="RESTART_SERVICE",
            category=ActionCategory.EXECUTE,
            description="Restart a service",
            required_params=["service_name"],
            requires_confirmation=True,
            requires_authorization=True,
            risk_level=RiskLevel.HIGH
        ),
        "UPDATE_CONFIG": ActionDefinition(
            name="UPDATE_CONFIG",
            category=ActionCategory.WRITE,
            description="Update configuration settings",
            required_params=["config_key", "config_value"],
            requires_authorization=True,
            risk_level=RiskLevel.MEDIUM
        ),
        "SHUTDOWN": ActionDefinition(
            name="SHUTDOWN",
            category=ActionCategory.CRITICAL,
            description="Shutdown a system or service",
            required_params=["target"],
            requires_confirmation=True,
            requires_authorization=True,
            risk_level=RiskLevel.CRITICAL
        ),
        
        # Compliance Actions
        "GENERATE_AUDIT_REPORT": ActionDefinition(
            name="GENERATE_AUDIT_REPORT",
            category=ActionCategory.READ,
            description="Generate an audit report",
            optional_params=["time_window", "scope"],
            risk_level=RiskLevel.LOW
        ),
        "VERIFY_COMPLIANCE": ActionDefinition(
            name="VERIFY_COMPLIANCE",
            category=ActionCategory.READ,
            description="Verify compliance status",
            optional_params=["policy", "scope"],
            risk_level=RiskLevel.LOW
        ),
        "ENFORCE_POLICY": ActionDefinition(
            name="ENFORCE_POLICY",
            category=ActionCategory.ADMIN,
            description="Enforce a compliance policy",
            required_params=["policy_id"],
            requires_authorization=True,
            risk_level=RiskLevel.MEDIUM
        ),
        
        # Generic Actions
        "ANALYZE": ActionDefinition(
            name="ANALYZE",
            category=ActionCategory.READ,
            description="Analyze data or situation",
            optional_params=["scope", "depth"],
            risk_level=RiskLevel.LOW
        ),
        "NOTIFY": ActionDefinition(
            name="NOTIFY",
            category=ActionCategory.WRITE,
            description="Send notifications",
            required_params=["recipients"],
            optional_params=["message", "channel"],
            risk_level=RiskLevel.LOW
        ),
        "ALERT": ActionDefinition(
            name="ALERT",
            category=ActionCategory.WRITE,
            description="Create an alert",
            required_params=["alert_type"],
            optional_params=["severity", "message"],
            risk_level=RiskLevel.LOW
        ),
    }
    
    # Intent to action mapping
    DEFAULT_ACTIONS: Dict[IntentType, List[str]] = {
        IntentType.SECURITY: ["SCAN_NETWORK", "ANALYZE"],
        IntentType.ACCESS: ["GRANT_ACCESS"],
        IntentType.QUERY: ["QUERY_DATABASE"],
        IntentType.SYSTEM: ["ANALYZE"],
        IntentType.COMPLIANCE: ["VERIFY_COMPLIANCE"]
    }
    
    def __init__(self):
        """Initialize the action mapper"""
        self.custom_mappings: Dict[str, List[str]] = {}
    
    def add_custom_mapping(self, keyword: str, actions: List[str]):
        """Add custom keyword to action mapping"""
        self.custom_mappings[keyword.lower()] = actions
    
    def map_intent_to_actions(self, intent: LLMOutput) -> List[MappedAction]:
        """
        Map an intent to specific actions with parameters
        
        Args:
            intent: The parsed intent
            
        Returns:
            List of mapped actions with parameters
        """
        mapped_actions = []
        
        # Get requested actions or defaults
        action_names = intent.requested_actions
        if not action_names:
            action_names = self.DEFAULT_ACTIONS.get(intent.intent_type, ["ANALYZE"])
        
        for action_name in action_names:
            # Get action definition
            definition = self.ACTIONS.get(action_name)
            
            if definition:
                # Extract parameters
                params = self._extract_params(action_name, intent, definition)
                
                # Build conditions
                conditions = self._build_conditions(intent, definition)
                
                mapped = MappedAction(
                    action=action_name,
                    params=params,
                    conditions=conditions,
                    fallback=definition.fallback_action,
                    category=definition.category,
                    risk_level=definition.risk_level,
                    requires_confirmation=definition.requires_confirmation,
                    description=definition.description
                )
                mapped_actions.append(mapped)
            else:
                # Unknown action - create generic mapping
                mapped = MappedAction(
                    action=action_name,
                    params={},
                    conditions=[],
                    fallback=None,
                    category=ActionCategory.EXECUTE,
                    risk_level=RiskLevel.MEDIUM,
                    requires_confirmation=False,
                    description=f"Execute {action_name}"
                )
                mapped_actions.append(mapped)
        
        return mapped_actions
    
    def _extract_params(
        self,
        action_name: str,
        intent: LLMOutput,
        definition: ActionDefinition
    ) -> Dict[str, Any]:
        """Extract parameters for an action from the intent"""
        params = {}
        
        # Map entities to common parameter names
        if intent.entities.targets:
            if "ip_addresses" in definition.required_params or "ip_addresses" in definition.optional_params:
                # Filter to only IP-like targets
                ips = [t for t in intent.entities.targets if self._looks_like_ip(t)]
                if ips:
                    params["ip_addresses"] = ips
            
            if "system_id" in definition.required_params:
                params["system_id"] = intent.entities.targets[0]
            
            if "target" in definition.required_params:
                params["target"] = intent.entities.targets[0]
        
        if intent.entities.subjects:
            if "subjects" in definition.required_params or "subjects" in definition.optional_params:
                params["subjects"] = intent.entities.subjects
            
            if "username" in definition.required_params:
                params["username"] = intent.entities.subjects[0]
            
            if "recipients" in definition.required_params:
                params["recipients"] = intent.entities.subjects
        
        if intent.entities.objects:
            if "resources" in definition.required_params or "resources" in definition.optional_params:
                params["resources"] = intent.entities.objects
        
        # Extract from constraints
        if intent.constraints:
            if intent.constraints.time_window:
                params["time_window"] = intent.constraints.time_window
            
            if intent.constraints.filters:
                params["filters"] = intent.constraints.filters
            
            if intent.constraints.thresholds:
                params["thresholds"] = intent.constraints.thresholds
        
        # Set defaults for missing required params
        for required in definition.required_params:
            if required not in params:
                params[required] = self._get_default_param(required)
        
        return params
    
    def _looks_like_ip(self, text: str) -> bool:
        """Check if text looks like an IP address"""
        import re
        ip_pattern = r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$'
        return bool(re.match(ip_pattern, text))
    
    def _get_default_param(self, param_name: str) -> Any:
        """Get default value for a parameter"""
        defaults = {
            "ip_addresses": [],
            "subjects": [],
            "resources": [],
            "time_window": {"start": "last 24 hours", "end": "now"},
            "filters": {},
            "limit": 100,
            "format": "json"
        }
        return defaults.get(param_name, None)
    
    def _build_conditions(
        self,
        intent: LLMOutput,
        definition: ActionDefinition
    ) -> List[str]:
        """Build execution conditions for an action"""
        conditions = []
        
        if definition.requires_authorization:
            conditions.append("authorization_granted")
        
        if definition.requires_confirmation:
            conditions.append("user_confirmed")
        
        # Add time-based conditions
        if intent.constraints and intent.constraints.time_window:
            if "scheduled" in intent.constraints.time_window:
                conditions.append(f"time_reached:{intent.constraints.time_window['scheduled']}")
        
        return conditions
    
    def get_execution_order(self, actions: List[MappedAction]) -> List[List[MappedAction]]:
        """
        Determine execution order for actions
        
        Returns groups of actions that can run in parallel
        """
        # Group by dependencies
        critical_actions = []
        high_risk_actions = []
        medium_risk_actions = []
        low_risk_actions = []
        
        for action in actions:
            if action.risk_level == RiskLevel.CRITICAL:
                critical_actions.append(action)
            elif action.risk_level == RiskLevel.HIGH:
                high_risk_actions.append(action)
            elif action.risk_level == RiskLevel.MEDIUM:
                medium_risk_actions.append(action)
            else:
                low_risk_actions.append(action)
        
        # Order: Low risk first, then medium, high, critical (for safety)
        # Critical actions should be last and sequential
        order = []
        
        if low_risk_actions:
            order.append(low_risk_actions)  # Can run in parallel
        if medium_risk_actions:
            order.append(medium_risk_actions)  # Can run in parallel
        if high_risk_actions:
            for action in high_risk_actions:
                order.append([action])  # Run sequentially
        if critical_actions:
            for action in critical_actions:
                order.append([action])  # Run sequentially
        
        return order
    
    def to_operational_level(self, mapped_actions: List[MappedAction]) -> OperationalLevel:
        """Convert mapped actions to HRM OperationalLevel"""
        
        operational_actions = []
        for mapped in mapped_actions:
            op_action = OperationalAction(
                action=mapped.action,
                params=mapped.params,
                conditions=mapped.conditions,
                fallback=mapped.fallback or f"{mapped.action}_ROLLBACK"
            )
            operational_actions.append(op_action)
        
        # Determine execution order
        if any(a.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL] for a in mapped_actions):
            execution_order = "sequential"
        else:
            execution_order = "parallel"
        
        return OperationalLevel(
            actions=operational_actions,
            execution_order=execution_order
        )
    
    def requires_confirmation(self, actions: List[MappedAction]) -> Tuple[bool, List[str]]:
        """
        Check if any actions require user confirmation
        
        Returns:
            Tuple of (requires_confirmation, list of action names)
        """
        confirm_actions = [a.action for a in actions if a.requires_confirmation]
        return len(confirm_actions) > 0, confirm_actions
    
    def get_risk_summary(self, actions: List[MappedAction]) -> Dict[str, Any]:
        """Get risk summary for a set of actions"""
        
        risk_counts = {
            "LOW": 0,
            "MEDIUM": 0,
            "HIGH": 0,
            "CRITICAL": 0
        }
        
        highest_risk = RiskLevel.LOW
        requires_auth = False
        requires_confirm = False
        
        for action in actions:
            risk_counts[action.risk_level.value] += 1
            if action.risk_level.value in ["HIGH", "CRITICAL"]:
                if action.risk_level == RiskLevel.CRITICAL or highest_risk != RiskLevel.CRITICAL:
                    highest_risk = action.risk_level
            if action.category == ActionCategory.ADMIN or action.category == ActionCategory.CRITICAL:
                requires_auth = True
            if action.requires_confirmation:
                requires_confirm = True
        
        return {
            "risk_counts": risk_counts,
            "highest_risk": highest_risk.value,
            "requires_authorization": requires_auth,
            "requires_confirmation": requires_confirm,
            "total_actions": len(actions)
        }


# Singleton instance
_mapper_instance: Optional[ActionMapper] = None


def get_action_mapper() -> ActionMapper:
    """Get or create singleton action mapper"""
    global _mapper_instance
    if _mapper_instance is None:
        _mapper_instance = ActionMapper()
    return _mapper_instance
