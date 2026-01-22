"""
Audit Logger for HRM Decision System

Comprehensive audit logging system that tracks:
- All requests and decisions
- Action executions and results
- Security events
- Compliance-relevant activities
- Performance metrics

Supports multiple output backends and log retention policies.
"""

import logging
import json
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field, asdict
import uuid
from collections import deque
import threading

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AuditEventType(str, Enum):
    """Types of audit events"""
    # Request lifecycle
    REQUEST_RECEIVED = "REQUEST_RECEIVED"
    REQUEST_PREPROCESSED = "REQUEST_PREPROCESSED"
    REQUEST_INTERPRETED = "REQUEST_INTERPRETED"
    REQUEST_VALIDATED = "REQUEST_VALIDATED"
    
    # Decision events
    DECISION_STARTED = "DECISION_STARTED"
    DECISION_L1_STRATEGIC = "DECISION_L1_STRATEGIC"
    DECISION_L2_TACTICAL = "DECISION_L2_TACTICAL"
    DECISION_L3_OPERATIONAL = "DECISION_L3_OPERATIONAL"
    DECISION_COMPLETED = "DECISION_COMPLETED"
    DECISION_DENIED = "DECISION_DENIED"
    
    # Action events
    ACTION_PLANNED = "ACTION_PLANNED"
    ACTION_STARTED = "ACTION_STARTED"
    ACTION_COMPLETED = "ACTION_COMPLETED"
    ACTION_FAILED = "ACTION_FAILED"
    ACTION_ROLLBACK = "ACTION_ROLLBACK"
    
    # Security events
    SECURITY_ALERT = "SECURITY_ALERT"
    SECURITY_BLOCK = "SECURITY_BLOCK"
    AUTHORIZATION_CHECK = "AUTHORIZATION_CHECK"
    AUTHORIZATION_DENIED = "AUTHORIZATION_DENIED"
    
    # System events
    SYSTEM_ERROR = "SYSTEM_ERROR"
    SYSTEM_WARNING = "SYSTEM_WARNING"
    CONFIGURATION_CHANGE = "CONFIGURATION_CHANGE"


class AuditSeverity(str, Enum):
    """Severity levels for audit events"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass
class AuditEntry:
    """Single audit log entry"""
    entry_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    event_type: str = ""
    severity: str = AuditSeverity.INFO.value
    
    # Context
    request_id: Optional[str] = None
    decision_id: Optional[str] = None
    session_id: Optional[str] = None
    
    # Actor
    user_id: Optional[str] = None
    user_role: Optional[str] = None
    ip_address: Optional[str] = None
    
    # Action
    action: str = ""
    action_params: Dict[str, Any] = field(default_factory=dict)
    
    # Result
    outcome: str = "pending"  # success, failure, pending
    result_data: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None
    
    # Metadata
    duration_ms: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), default=str)


@dataclass
class AuditSummary:
    """Summary of audit activity"""
    total_entries: int = 0
    entries_by_type: Dict[str, int] = field(default_factory=dict)
    entries_by_severity: Dict[str, int] = field(default_factory=dict)
    entries_by_outcome: Dict[str, int] = field(default_factory=dict)
    time_range_start: Optional[str] = None
    time_range_end: Optional[str] = None
    unique_users: int = 0
    unique_sessions: int = 0
    average_duration_ms: Optional[float] = None
    error_rate: float = 0.0


class AuditLogger:
    """
    Centralized audit logging system
    
    Features:
    - In-memory log storage with configurable retention
    - Multiple severity levels
    - Structured logging with context
    - Search and filter capabilities
    - Export functionality
    - Thread-safe operations
    """
    
    def __init__(
        self,
        max_entries: int = 10000,
        retention_hours: int = 24,
        enable_console: bool = True,
        enable_file: bool = False,
        log_file_path: Optional[str] = None
    ):
        """
        Initialize Audit Logger
        
        Args:
            max_entries: Maximum entries to keep in memory
            retention_hours: Hours to retain entries
            enable_console: Log to console
            enable_file: Log to file
            log_file_path: Path for file logging
        """
        self.max_entries = max_entries
        self.retention_hours = retention_hours
        self.enable_console = enable_console
        self.enable_file = enable_file
        self.log_file_path = log_file_path
        
        # Thread-safe storage
        self._lock = threading.Lock()
        self._entries: deque = deque(maxlen=max_entries)
        
        # Callbacks for external integrations
        self._callbacks: List[Callable[[AuditEntry], None]] = []
        
        logger.info(f"Audit Logger initialized (max_entries={max_entries}, retention={retention_hours}h)")
    
    def log(
        self,
        event_type: AuditEventType,
        action: str,
        severity: AuditSeverity = AuditSeverity.INFO,
        request_id: Optional[str] = None,
        decision_id: Optional[str] = None,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None,
        user_role: Optional[str] = None,
        ip_address: Optional[str] = None,
        action_params: Optional[Dict[str, Any]] = None,
        outcome: str = "success",
        result_data: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None,
        duration_ms: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AuditEntry:
        """
        Log an audit event
        
        Args:
            event_type: Type of event
            action: Action being performed
            severity: Severity level
            request_id: Associated request ID
            decision_id: Associated decision ID
            session_id: User session ID
            user_id: User identifier
            user_role: User's role
            ip_address: Source IP
            action_params: Parameters for the action
            outcome: Result outcome
            result_data: Result details
            error_message: Error message if failed
            duration_ms: Duration in milliseconds
            metadata: Additional metadata
            
        Returns:
            AuditEntry: The created audit entry
        """
        
        entry = AuditEntry(
            event_type=event_type.value,
            severity=severity.value,
            request_id=request_id,
            decision_id=decision_id,
            session_id=session_id,
            user_id=user_id,
            user_role=user_role,
            ip_address=ip_address,
            action=action,
            action_params=action_params or {},
            outcome=outcome,
            result_data=result_data or {},
            error_message=error_message,
            duration_ms=duration_ms,
            metadata=metadata or {}
        )
        
        with self._lock:
            self._entries.append(entry)
        
        # Console output
        if self.enable_console:
            self._log_to_console(entry)
        
        # File output
        if self.enable_file and self.log_file_path:
            self._log_to_file(entry)
        
        # Execute callbacks
        for callback in self._callbacks:
            try:
                callback(entry)
            except Exception as e:
                logger.error(f"Audit callback error: {e}")
        
        return entry
    
    def log_request_received(
        self,
        request_id: str,
        user_id: str,
        message: str,
        session_id: Optional[str] = None,
        user_role: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> AuditEntry:
        """Log request received event"""
        return self.log(
            event_type=AuditEventType.REQUEST_RECEIVED,
            action="receive_request",
            request_id=request_id,
            user_id=user_id,
            session_id=session_id,
            user_role=user_role,
            ip_address=ip_address,
            action_params={"message_length": len(message)},
            metadata={"message_preview": message[:100] + "..." if len(message) > 100 else message}
        )
    
    def log_decision_started(
        self,
        request_id: str,
        decision_id: str,
        goal: str,
        risk_level: str
    ) -> AuditEntry:
        """Log decision started event"""
        return self.log(
            event_type=AuditEventType.DECISION_STARTED,
            action="start_decision",
            request_id=request_id,
            decision_id=decision_id,
            action_params={"goal": goal, "risk_level": risk_level}
        )
    
    def log_l1_strategic(
        self,
        request_id: str,
        decision_id: str,
        goal: str,
        risk_level: str,
        priority: int,
        approved: bool
    ) -> AuditEntry:
        """Log L1 Strategic level assessment"""
        return self.log(
            event_type=AuditEventType.DECISION_L1_STRATEGIC,
            action="l1_strategic_assessment",
            request_id=request_id,
            decision_id=decision_id,
            outcome="approved" if approved else "denied",
            action_params={
                "goal": goal,
                "risk_level": risk_level,
                "priority": priority
            }
        )
    
    def log_l2_tactical(
        self,
        request_id: str,
        decision_id: str,
        strategy: str,
        policy: str,
        subsystem: str
    ) -> AuditEntry:
        """Log L2 Tactical level planning"""
        return self.log(
            event_type=AuditEventType.DECISION_L2_TACTICAL,
            action="l2_tactical_planning",
            request_id=request_id,
            decision_id=decision_id,
            action_params={
                "strategy": strategy,
                "policy": policy,
                "subsystem": subsystem
            }
        )
    
    def log_l3_operational(
        self,
        request_id: str,
        decision_id: str,
        actions: List[str],
        execution_order: str
    ) -> AuditEntry:
        """Log L3 Operational level execution"""
        return self.log(
            event_type=AuditEventType.DECISION_L3_OPERATIONAL,
            action="l3_operational_execution",
            request_id=request_id,
            decision_id=decision_id,
            action_params={
                "actions": actions,
                "execution_order": execution_order,
                "action_count": len(actions)
            }
        )
    
    def log_decision_completed(
        self,
        request_id: str,
        decision_id: str,
        status: str,
        summary: str,
        duration_ms: float
    ) -> AuditEntry:
        """Log decision completed event"""
        return self.log(
            event_type=AuditEventType.DECISION_COMPLETED,
            action="complete_decision",
            request_id=request_id,
            decision_id=decision_id,
            outcome=status.lower(),
            result_data={"summary": summary},
            duration_ms=duration_ms
        )
    
    def log_action_executed(
        self,
        request_id: str,
        decision_id: str,
        action_name: str,
        params: Dict[str, Any],
        outcome: str,
        result: Dict[str, Any],
        duration_ms: Optional[float] = None
    ) -> AuditEntry:
        """Log action execution event"""
        event_type = AuditEventType.ACTION_COMPLETED if outcome == "success" else AuditEventType.ACTION_FAILED
        severity = AuditSeverity.INFO if outcome == "success" else AuditSeverity.WARNING
        
        return self.log(
            event_type=event_type,
            action=action_name,
            severity=severity,
            request_id=request_id,
            decision_id=decision_id,
            action_params=params,
            outcome=outcome,
            result_data=result,
            duration_ms=duration_ms
        )
    
    def log_security_event(
        self,
        event_type: AuditEventType,
        action: str,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        severity: AuditSeverity = AuditSeverity.WARNING
    ) -> AuditEntry:
        """Log security-related event"""
        return self.log(
            event_type=event_type,
            action=action,
            severity=severity,
            user_id=user_id,
            ip_address=ip_address,
            action_params=details or {},
            outcome="logged"
        )
    
    def log_error(
        self,
        action: str,
        error_message: str,
        request_id: Optional[str] = None,
        decision_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AuditEntry:
        """Log error event"""
        return self.log(
            event_type=AuditEventType.SYSTEM_ERROR,
            action=action,
            severity=AuditSeverity.ERROR,
            request_id=request_id,
            decision_id=decision_id,
            outcome="failure",
            error_message=error_message,
            metadata=metadata or {}
        )
    
    def get_entries(
        self,
        request_id: Optional[str] = None,
        decision_id: Optional[str] = None,
        event_type: Optional[AuditEventType] = None,
        severity: Optional[AuditSeverity] = None,
        user_id: Optional[str] = None,
        outcome: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: Optional[int] = None
    ) -> List[AuditEntry]:
        """
        Get filtered audit entries
        
        Args:
            request_id: Filter by request ID
            decision_id: Filter by decision ID
            event_type: Filter by event type
            severity: Filter by severity
            user_id: Filter by user ID
            outcome: Filter by outcome
            start_time: Filter by start time
            end_time: Filter by end time
            limit: Maximum entries to return
            
        Returns:
            List of matching audit entries
        """
        
        with self._lock:
            entries = list(self._entries)
        
        # Apply filters
        if request_id:
            entries = [e for e in entries if e.request_id == request_id]
        
        if decision_id:
            entries = [e for e in entries if e.decision_id == decision_id]
        
        if event_type:
            entries = [e for e in entries if e.event_type == event_type.value]
        
        if severity:
            entries = [e for e in entries if e.severity == severity.value]
        
        if user_id:
            entries = [e for e in entries if e.user_id == user_id]
        
        if outcome:
            entries = [e for e in entries if e.outcome == outcome]
        
        if start_time:
            entries = [e for e in entries if datetime.fromisoformat(e.timestamp) >= start_time]
        
        if end_time:
            entries = [e for e in entries if datetime.fromisoformat(e.timestamp) <= end_time]
        
        # Sort by timestamp (newest first)
        entries.sort(key=lambda e: e.timestamp, reverse=True)
        
        # Apply limit
        if limit:
            entries = entries[:limit]
        
        return entries
    
    def get_summary(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> AuditSummary:
        """
        Get summary of audit activity
        
        Args:
            start_time: Start of time range
            end_time: End of time range
            
        Returns:
            AuditSummary with statistics
        """
        
        entries = self.get_entries(start_time=start_time, end_time=end_time)
        
        if not entries:
            return AuditSummary()
        
        # Calculate statistics
        entries_by_type: Dict[str, int] = {}
        entries_by_severity: Dict[str, int] = {}
        entries_by_outcome: Dict[str, int] = {}
        users = set()
        sessions = set()
        durations = []
        error_count = 0
        
        for entry in entries:
            # Count by type
            entries_by_type[entry.event_type] = entries_by_type.get(entry.event_type, 0) + 1
            
            # Count by severity
            entries_by_severity[entry.severity] = entries_by_severity.get(entry.severity, 0) + 1
            
            # Count by outcome
            entries_by_outcome[entry.outcome] = entries_by_outcome.get(entry.outcome, 0) + 1
            
            # Collect unique users and sessions
            if entry.user_id:
                users.add(entry.user_id)
            if entry.session_id:
                sessions.add(entry.session_id)
            
            # Collect durations
            if entry.duration_ms is not None:
                durations.append(entry.duration_ms)
            
            # Count errors
            if entry.outcome == "failure":
                error_count += 1
        
        # Calculate averages
        avg_duration = sum(durations) / len(durations) if durations else None
        error_rate = error_count / len(entries) if entries else 0.0
        
        return AuditSummary(
            total_entries=len(entries),
            entries_by_type=entries_by_type,
            entries_by_severity=entries_by_severity,
            entries_by_outcome=entries_by_outcome,
            time_range_start=entries[-1].timestamp if entries else None,
            time_range_end=entries[0].timestamp if entries else None,
            unique_users=len(users),
            unique_sessions=len(sessions),
            average_duration_ms=avg_duration,
            error_rate=error_rate
        )
    
    def get_request_trail(self, request_id: str) -> List[AuditEntry]:
        """Get complete audit trail for a request"""
        return self.get_entries(request_id=request_id)
    
    def get_decision_trail(self, decision_id: str) -> List[AuditEntry]:
        """Get complete audit trail for a decision"""
        return self.get_entries(decision_id=decision_id)
    
    def get_user_activity(self, user_id: str, limit: int = 100) -> List[AuditEntry]:
        """Get recent activity for a user"""
        return self.get_entries(user_id=user_id, limit=limit)
    
    def export_entries(
        self,
        format: str = "json",
        **filter_kwargs
    ) -> str:
        """
        Export audit entries
        
        Args:
            format: Export format ('json', 'csv')
            **filter_kwargs: Filter parameters
            
        Returns:
            Exported data as string
        """
        
        entries = self.get_entries(**filter_kwargs)
        
        if format == "json":
            return json.dumps([e.to_dict() for e in entries], indent=2, default=str)
        
        elif format == "csv":
            if not entries:
                return ""
            
            # Build CSV
            headers = list(entries[0].to_dict().keys())
            lines = [",".join(headers)]
            
            for entry in entries:
                values = [str(v).replace(",", ";") for v in entry.to_dict().values()]
                lines.append(",".join(values))
            
            return "\n".join(lines)
        
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def clear(self, before: Optional[datetime] = None):
        """
        Clear audit entries
        
        Args:
            before: Clear entries before this time (None = clear all)
        """
        
        with self._lock:
            if before is None:
                self._entries.clear()
            else:
                self._entries = deque(
                    [e for e in self._entries if datetime.fromisoformat(e.timestamp) >= before],
                    maxlen=self.max_entries
                )
        
        logger.info(f"Audit log cleared (before={before})")
    
    def cleanup_old_entries(self):
        """Remove entries older than retention period"""
        cutoff = datetime.now() - timedelta(hours=self.retention_hours)
        self.clear(before=cutoff)
    
    def register_callback(self, callback: Callable[[AuditEntry], None]):
        """Register callback for new audit entries"""
        self._callbacks.append(callback)
    
    def _log_to_console(self, entry: AuditEntry):
        """Log entry to console"""
        level = getattr(logging, entry.severity, logging.INFO)
        logger.log(
            level,
            f"[AUDIT] {entry.event_type} | {entry.action} | {entry.outcome} | "
            f"req={entry.request_id} | user={entry.user_id}"
        )
    
    def _log_to_file(self, entry: AuditEntry):
        """Log entry to file"""
        try:
            with open(self.log_file_path, "a") as f:
                f.write(entry.to_json() + "\n")
        except Exception as e:
            logger.error(f"Failed to write audit log to file: {e}")


# Singleton instance
_audit_logger: Optional[AuditLogger] = None


def get_audit_logger() -> AuditLogger:
    """Get or create singleton audit logger instance"""
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = AuditLogger()
    return _audit_logger


def create_audit_logger(**kwargs) -> AuditLogger:
    """Create a new audit logger instance"""
    return AuditLogger(**kwargs)
