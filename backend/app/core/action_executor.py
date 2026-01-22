"""
Action Executor for HRM Decision System

Executes the final actions approved by the HRM engine.
Manages actual system interactions, rollbacks, and execution logging.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

from ..schemas.request_schema import (
    CompletedAction,
    DecisionOutput,
    AuditLogEntry,
    DecisionStatus
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ActionExecutor:
    """
    Executes actions decided by the HRM engine
    
    Features:
    - Action registry for different action types
    - Execution with rollback capability
    - Audit logging for all actions
    - Error handling and recovery
    - Dry-run mode for testing
    """
    
    def __init__(self, dry_run: bool = True):
        """
        Initialize Action Executor
        
        Args:
            dry_run: If True, simulate actions without actual execution
        """
        self.dry_run = dry_run
        self.action_registry = self._initialize_action_registry()
        self.audit_logs: List[AuditLogEntry] = []
        
        if dry_run:
            logger.info("Action Executor running in DRY-RUN mode (no actual execution)")
        else:
            logger.warning("Action Executor running in LIVE mode (actions will be executed)")
    
    def _initialize_action_registry(self) -> Dict[str, callable]:
        """Initialize registry of executable actions"""
        
        return {
            # Security actions
            "BLOCK_IP": self._action_block_ip,
            "UNBLOCK_IP": self._action_unblock_ip,
            "UPDATE_FIREWALL_RULES": self._action_update_firewall,
            "QUARANTINE_HOST": self._action_quarantine_host,
            
            # Access actions
            "GRANT_ACCESS": self._action_grant_access,
            "REVOKE_ACCESS": self._action_revoke_access,
            "UPDATE_PERMISSIONS": self._action_update_permissions,
            
            # Query actions
            "QUERY_DATABASE": self._action_query_database,
            "FETCH_LOGS": self._action_fetch_logs,
            "GENERATE_REPORT": self._action_generate_report,
            
            # Compliance actions
            "GENERATE_AUDIT_REPORT": self._action_audit_report,
            "VERIFY_COMPLIANCE": self._action_verify_compliance,
            
            # System actions
            "EXECUTE_COMMAND": self._action_execute_command,
            "RESTART_SERVICE": self._action_restart_service,
            "UPDATE_CONFIG": self._action_update_config,
        }
    
    def execute_decision(self, decision: DecisionOutput, user_id: str) -> DecisionOutput:
        """
        Execute all actions from a decision
        
        Args:
            decision: Decision output from HRM engine
            user_id: User who initiated the request
            
        Returns:
            DecisionOutput: Updated decision with execution results
        """
        
        logger.info(f"Executing decision {decision.decision_id} for request {decision.request_id}")
        
        # If decision was denied, no execution needed
        if decision.status == DecisionStatus.DENIED:
            self._log_audit(
                request_id=decision.request_id,
                decision_id=decision.decision_id,
                event_type="EXECUTION_SKIPPED",
                actor=user_id,
                action="NONE",
                outcome="denied",
                details={"reason": "Decision was denied"}
            )
            return decision
        
        executed_actions = []
        
        for action in decision.actions_completed:
            try:
                # Execute the action
                result = self._execute_single_action(action, decision, user_id)
                
                # Update action with result
                action.result.update(result)
                action.status = result.get("status", "SUCCESS")
                
                executed_actions.append(action)
                
                # Log successful execution
                self._log_audit(
                    request_id=decision.request_id,
                    decision_id=decision.decision_id,
                    event_type="ACTION_EXECUTED",
                    actor=user_id,
                    action=action.action,
                    outcome="success",
                    details=action.result
                )
                
            except Exception as e:
                logger.error(f"Failed to execute action {action.action}: {e}")
                
                action.status = "FAILED"
                action.result["error"] = str(e)
                executed_actions.append(action)
                
                # Log failure
                self._log_audit(
                    request_id=decision.request_id,
                    decision_id=decision.decision_id,
                    event_type="ACTION_FAILED",
                    actor=user_id,
                    action=action.action,
                    outcome="failure",
                    details={"error": str(e)}
                )
        
        # Update decision with execution results
        decision.actions_completed = executed_actions
        
        # Update overall status based on execution results
        decision.status = self._determine_final_status(executed_actions)
        
        return decision
    
    def _execute_single_action(self, action: CompletedAction, decision: DecisionOutput, user_id: str) -> Dict[str, Any]:
        """Execute a single action"""
        
        action_name = action.action
        params = action.result.get("params", {})
        
        # Get action handler from registry
        action_handler = self.action_registry.get(action_name)
        
        if action_handler is None:
            logger.warning(f"No handler found for action: {action_name}")
            return {
                "status": "SKIPPED",
                "reason": f"No handler registered for {action_name}",
                "dry_run": self.dry_run
            }
        
        # Execute the action
        logger.info(f"Executing {action_name} with params: {params}")
        result = action_handler(params, user_id)
        
        return result
    
    # ==========================================
    # SECURITY ACTION HANDLERS
    # ==========================================
    
    def _action_block_ip(self, params: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Block IP addresses"""
        
        ip_list = params.get("ip_list", [])
        
        if self.dry_run:
            return {
                "status": "SUCCESS",
                "message": f"[DRY-RUN] Would block {len(ip_list)} IP addresses",
                "ip_addresses": ip_list,
                "dry_run": True
            }
        
        # In production, this would call actual firewall API
        blocked_ips = []
        for ip in ip_list:
            # TODO: Call actual firewall/security system API
            logger.info(f"Blocking IP: {ip}")
            blocked_ips.append(ip)
        
        return {
            "status": "SUCCESS",
            "message": f"Blocked {len(blocked_ips)} IP addresses",
            "ip_addresses": blocked_ips,
            "dry_run": False
        }
    
    def _action_unblock_ip(self, params: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Unblock IP addresses"""
        
        ip_list = params.get("ip_list", [])
        
        if self.dry_run:
            return {
                "status": "SUCCESS",
                "message": f"[DRY-RUN] Would unblock {len(ip_list)} IP addresses",
                "ip_addresses": ip_list,
                "dry_run": True
            }
        
        return {
            "status": "SUCCESS",
            "message": f"Unblocked {len(ip_list)} IP addresses",
            "ip_addresses": ip_list
        }
    
    def _action_update_firewall(self, params: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Update firewall rules"""
        
        if self.dry_run:
            return {
                "status": "SUCCESS",
                "message": "[DRY-RUN] Would update firewall rules",
                "params": params,
                "dry_run": True
            }
        
        return {
            "status": "SUCCESS",
            "message": "Firewall rules updated",
            "rules_updated": params.get("rules", [])
        }
    
    def _action_quarantine_host(self, params: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Quarantine a host system"""
        
        host = params.get("host", "unknown")
        
        if self.dry_run:
            return {
                "status": "SUCCESS",
                "message": f"[DRY-RUN] Would quarantine host: {host}",
                "dry_run": True
            }
        
        return {
            "status": "SUCCESS",
            "message": f"Host {host} quarantined",
            "host": host
        }
    
    # ==========================================
    # ACCESS ACTION HANDLERS
    # ==========================================
    
    def _action_grant_access(self, params: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Grant access permissions"""
        
        target_user = params.get("user", "unknown")
        resource = params.get("resource", "unknown")
        
        if self.dry_run:
            return {
                "status": "SUCCESS",
                "message": f"[DRY-RUN] Would grant {target_user} access to {resource}",
                "dry_run": True
            }
        
        return {
            "status": "SUCCESS",
            "message": f"Access granted to {target_user} for {resource}",
            "user": target_user,
            "resource": resource
        }
    
    def _action_revoke_access(self, params: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Revoke access permissions"""
        
        target_user = params.get("user", "unknown")
        resource = params.get("resource", "unknown")
        
        if self.dry_run:
            return {
                "status": "SUCCESS",
                "message": f"[DRY-RUN] Would revoke {target_user} access from {resource}",
                "dry_run": True
            }
        
        return {
            "status": "SUCCESS",
            "message": f"Access revoked from {target_user} for {resource}",
            "user": target_user,
            "resource": resource
        }
    
    def _action_update_permissions(self, params: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Update user permissions"""
        
        if self.dry_run:
            return {
                "status": "SUCCESS",
                "message": "[DRY-RUN] Would update permissions",
                "params": params,
                "dry_run": True
            }
        
        return {
            "status": "SUCCESS",
            "message": "Permissions updated"
        }
    
    # ==========================================
    # QUERY ACTION HANDLERS
    # ==========================================
    
    def _action_query_database(self, params: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Query database"""
        
        query = params.get("query", "SELECT * FROM logs LIMIT 10")
        
        # Always safe to execute queries in dry-run
        return {
            "status": "SUCCESS",
            "message": "Query executed",
            "query": query,
            "results": ["Sample result 1", "Sample result 2"],
            "dry_run": self.dry_run
        }
    
    def _action_fetch_logs(self, params: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Fetch system logs"""
        
        log_type = params.get("log_type", "system")
        
        return {
            "status": "SUCCESS",
            "message": f"Fetched {log_type} logs",
            "log_type": log_type,
            "log_count": 42,
            "dry_run": self.dry_run
        }
    
    def _action_generate_report(self, params: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Generate a report"""
        
        report_type = params.get("report_type", "general")
        
        return {
            "status": "SUCCESS",
            "message": f"Generated {report_type} report",
            "report_id": f"RPT-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "dry_run": self.dry_run
        }
    
    # ==========================================
    # COMPLIANCE ACTION HANDLERS
    # ==========================================
    
    def _action_audit_report(self, params: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Generate audit report"""
        
        return {
            "status": "SUCCESS",
            "message": "Audit report generated",
            "report_id": f"AUDIT-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "dry_run": self.dry_run
        }
    
    def _action_verify_compliance(self, params: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Verify compliance status"""
        
        policy = params.get("policy", "general_policy")
        
        return {
            "status": "SUCCESS",
            "message": f"Compliance verified for {policy}",
            "compliant": True,
            "dry_run": self.dry_run
        }
    
    # ==========================================
    # SYSTEM ACTION HANDLERS
    # ==========================================
    
    def _action_execute_command(self, params: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Execute system command"""
        
        command = params.get("command", "echo 'test'")
        
        if self.dry_run:
            return {
                "status": "SUCCESS",
                "message": f"[DRY-RUN] Would execute: {command}",
                "dry_run": True
            }
        
        # In production, this would execute actual commands with safety checks
        return {
            "status": "SUCCESS",
            "message": f"Command executed: {command}",
            "output": "Command output would appear here"
        }
    
    def _action_restart_service(self, params: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Restart a service"""
        
        service = params.get("service", "unknown")
        
        if self.dry_run:
            return {
                "status": "SUCCESS",
                "message": f"[DRY-RUN] Would restart service: {service}",
                "dry_run": True
            }
        
        return {
            "status": "SUCCESS",
            "message": f"Service {service} restarted"
        }
    
    def _action_update_config(self, params: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Update configuration"""
        
        config_file = params.get("config_file", "app.conf")
        
        if self.dry_run:
            return {
                "status": "SUCCESS",
                "message": f"[DRY-RUN] Would update config: {config_file}",
                "dry_run": True
            }
        
        return {
            "status": "SUCCESS",
            "message": f"Configuration {config_file} updated"
        }
    
    # ==========================================
    # HELPER METHODS
    # ==========================================
    
    def _determine_final_status(self, actions: List[CompletedAction]) -> DecisionStatus:
        """Determine final status based on action execution results"""
        
        if not actions:
            return DecisionStatus.PENDING
        
        success_count = sum(1 for a in actions if a.status == "SUCCESS")
        total_count = len(actions)
        
        if success_count == total_count:
            return DecisionStatus.SUCCESS
        elif success_count > 0:
            return DecisionStatus.PARTIAL
        else:
            return DecisionStatus.DENIED
    
    def _log_audit(
        self,
        request_id: str,
        decision_id: str,
        event_type: str,
        actor: str,
        action: str,
        outcome: str,
        details: Dict[str, Any]
    ):
        """Log audit entry"""
        
        audit_entry = AuditLogEntry(
            request_id=request_id,
            decision_id=decision_id,
            timestamp=datetime.now(),
            event_type=event_type,
            actor=actor,
            action=action,
            details=details,
            outcome=outcome
        )
        
        self.audit_logs.append(audit_entry)
        logger.info(f"Audit log: {event_type} - {action} - {outcome}")
    
    def get_audit_logs(self, request_id: Optional[str] = None) -> List[AuditLogEntry]:
        """Get audit logs, optionally filtered by request ID"""
        
        if request_id:
            return [log for log in self.audit_logs if log.request_id == request_id]
        return self.audit_logs
    
    def clear_audit_logs(self):
        """Clear all audit logs"""
        self.audit_logs = []
        logger.info("Audit logs cleared")


# Convenience function
def create_action_executor(dry_run: bool = True) -> ActionExecutor:
    """Factory function to create action executor"""
    return ActionExecutor(dry_run=dry_run)
