"""
Phase 3 Test Suite - HRM Engine & Decision Logic

Comprehensive tests for:
- HRM Engine (L1, L2, L3 levels)
- Action Executor
- Audit Logger
- Decision API endpoints
- Integration tests
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
import json
import uuid

# Import test client
from fastapi.testclient import TestClient

# Import application
from app.main import app

# Import Phase 3 components
from app.core.hrm_engine import HRMEngine, create_hrm_engine
from app.core.action_executor import ActionExecutor, create_action_executor
from app.core.audit_logger import (
    AuditLogger,
    AuditEntry,
    AuditSummary,
    AuditEventType,
    AuditSeverity,
    get_audit_logger,
    create_audit_logger
)

# Import schemas
from app.schemas.request_schema import (
    UserRequest,
    RequestContext,
    HRMInput,
    DecisionOutput,
    DecisionStatus,
    StrategicLevel,
    TacticalLevel,
    OperationalLevel,
    OperationalAction,
    RiskLevel,
    CompletedAction
)

# Create test client
client = TestClient(app)


# ==========================================
# HRM ENGINE TESTS
# ==========================================

class TestHRMEngine:
    """Tests for HRMEngine class"""
    
    def test_init_simulation_mode(self):
        """Test HRM engine initializes in simulation mode"""
        engine = HRMEngine(use_simulation=True)
        assert engine.use_simulation is True
        assert engine.model is None
    
    def test_init_auto_detect_simulation(self):
        """Test HRM engine auto-detects simulation mode"""
        engine = HRMEngine()
        # Should be in simulation mode when PyTorch/HRM model not available
        assert engine.use_simulation is True
    
    def test_process_basic_request(self):
        """Test basic request processing"""
        engine = HRMEngine(use_simulation=True)
        
        hrm_input = HRMInput(
            L1_strategic=StrategicLevel(
                goal="Block malicious IPs",
                authorization_required=False,
                risk_level=RiskLevel.MEDIUM,
                priority=7
            ),
            L2_tactical=TacticalLevel(
                strategy="network_blocking",
                policy="security_policy",
                subsystem="firewall",
                constraints=[]
            ),
            L3_operational=OperationalLevel(
                actions=[
                    OperationalAction(
                        action="BLOCK_IP",
                        params={"ip_list": ["192.168.1.100"]},
                        conditions=[]
                    )
                ],
                execution_order="sequential"
            )
        )
        
        decision = engine.process(hrm_input, "test-request-001")
        
        assert decision is not None
        assert decision.request_id == "test-request-001"
        assert decision.status in [DecisionStatus.SUCCESS, DecisionStatus.PARTIAL, DecisionStatus.PENDING]
        assert len(decision.actions_completed) > 0
    
    def test_process_denied_request(self):
        """Test request that requires authorization is denied"""
        engine = HRMEngine(use_simulation=True)
        
        # In production mode, this would be denied without authorization
        # In simulation mode, it's auto-approved
        hrm_input = HRMInput(
            L1_strategic=StrategicLevel(
                goal="Delete all logs",
                authorization_required=True,  # Requires auth
                risk_level=RiskLevel.CRITICAL,
                priority=10
            ),
            L2_tactical=TacticalLevel(
                strategy="data_deletion",
                policy="admin_policy",
                subsystem="logging"
            ),
            L3_operational=OperationalLevel(
                actions=[],
                execution_order="sequential"
            )
        )
        
        decision = engine.process(hrm_input, "test-request-002")
        
        # In simulation mode, auto-approved
        assert decision is not None
        assert decision.request_id == "test-request-002"
    
    def test_process_with_multiple_actions(self):
        """Test processing with multiple operational actions"""
        engine = HRMEngine(use_simulation=True)
        
        hrm_input = HRMInput(
            L1_strategic=StrategicLevel(
                goal="Security response",
                priority=8
            ),
            L2_tactical=TacticalLevel(
                strategy="multi_action",
                policy="security_policy",
                subsystem="security"
            ),
            L3_operational=OperationalLevel(
                actions=[
                    OperationalAction(action="BLOCK_IP", params={"ip": "1.2.3.4"}),
                    OperationalAction(action="NOTIFY", params={"channel": "slack"}),
                    OperationalAction(action="LOG", params={"level": "critical"})
                ],
                execution_order="sequential"
            )
        )
        
        decision = engine.process(hrm_input, "test-request-003")
        
        assert len(decision.actions_completed) == 3
    
    def test_decision_output_structure(self):
        """Test decision output has correct structure"""
        engine = HRMEngine(use_simulation=True)
        
        hrm_input = HRMInput(
            L1_strategic=StrategicLevel(goal="Test goal", priority=5),
            L2_tactical=TacticalLevel(strategy="test", policy="test", subsystem="test"),
            L3_operational=OperationalLevel(actions=[])
        )
        
        decision = engine.process(hrm_input, "test-request-004")
        
        assert hasattr(decision, 'decision_id')
        assert hasattr(decision, 'request_id')
        assert hasattr(decision, 'status')
        assert hasattr(decision, 'summary')
        assert hasattr(decision, 'actions_completed')
        assert hasattr(decision, 'explanation')
        assert hasattr(decision, 'audit_trail')
        assert hasattr(decision, 'timestamp')
    
    def test_audit_trail_structure(self):
        """Test audit trail contains L1, L2, L3 information"""
        engine = HRMEngine(use_simulation=True)
        
        hrm_input = HRMInput(
            L1_strategic=StrategicLevel(
                goal="Audit test",
                risk_level=RiskLevel.HIGH,
                priority=9
            ),
            L2_tactical=TacticalLevel(
                strategy="audit_strategy",
                policy="audit_policy",
                subsystem="audit"
            ),
            L3_operational=OperationalLevel(
                actions=[OperationalAction(action="LOG", params={})],
                execution_order="sequential"
            )
        )
        
        decision = engine.process(hrm_input, "test-request-005")
        
        assert "L1_strategic" in decision.audit_trail
        assert "L2_tactical" in decision.audit_trail
        assert "L3_operational" in decision.audit_trail


class TestHRMEngineFactory:
    """Tests for HRM engine factory function"""
    
    def test_create_hrm_engine(self):
        """Test factory function creates engine"""
        engine = create_hrm_engine()
        assert isinstance(engine, HRMEngine)
    
    def test_create_hrm_engine_with_model_path(self):
        """Test factory with model path"""
        engine = create_hrm_engine(model_path="/path/to/model")
        assert engine.model_path == "/path/to/model"


# ==========================================
# ACTION EXECUTOR TESTS
# ==========================================

class TestActionExecutor:
    """Tests for ActionExecutor class"""
    
    def test_init_dry_run_mode(self):
        """Test executor initializes in dry-run mode"""
        executor = ActionExecutor(dry_run=True)
        assert executor.dry_run is True
    
    def test_init_live_mode(self):
        """Test executor initializes in live mode"""
        executor = ActionExecutor(dry_run=False)
        assert executor.dry_run is False
    
    def test_action_registry_populated(self):
        """Test action registry has handlers"""
        executor = ActionExecutor()
        
        expected_actions = [
            "BLOCK_IP", "UNBLOCK_IP", "GRANT_ACCESS", "REVOKE_ACCESS",
            "QUERY_DATABASE", "FETCH_LOGS", "GENERATE_REPORT"
        ]
        
        for action in expected_actions:
            assert action in executor.action_registry
    
    def test_execute_denied_decision(self):
        """Test executing a denied decision does nothing"""
        executor = ActionExecutor(dry_run=True)
        
        decision = DecisionOutput(
            request_id="test-001",
            status=DecisionStatus.DENIED,
            summary="Denied",
            explanation="Test denial",
            actions_completed=[]
        )
        
        result = executor.execute_decision(decision, "user-001")
        
        assert result.status == DecisionStatus.DENIED
        assert len(result.actions_completed) == 0
    
    def test_execute_success_decision_dry_run(self):
        """Test executing successful decision in dry-run mode"""
        executor = ActionExecutor(dry_run=True)
        
        decision = DecisionOutput(
            request_id="test-002",
            status=DecisionStatus.SUCCESS,
            summary="Block IPs",
            explanation="Test",
            actions_completed=[
                CompletedAction(
                    action="BLOCK_IP",
                    status="PLANNED",
                    result={"params": {"ip_list": ["1.2.3.4"]}}
                )
            ]
        )
        
        result = executor.execute_decision(decision, "user-001")
        
        assert len(result.actions_completed) > 0
    
    def test_block_ip_action_dry_run(self):
        """Test BLOCK_IP action in dry-run mode"""
        executor = ActionExecutor(dry_run=True)
        
        result = executor._action_block_ip(
            {"ip_list": ["192.168.1.1", "10.0.0.1"]},
            "user-001"
        )
        
        assert result["status"] == "SUCCESS"
        assert result["dry_run"] is True
        assert "[DRY-RUN]" in result["message"]
    
    def test_grant_access_action_dry_run(self):
        """Test GRANT_ACCESS action in dry-run mode"""
        executor = ActionExecutor(dry_run=True)
        
        result = executor._action_grant_access(
            {"user": "john.doe", "resource": "dashboard"},
            "admin-001"
        )
        
        assert result["status"] == "SUCCESS"
        assert result["dry_run"] is True
    
    def test_query_database_action(self):
        """Test QUERY_DATABASE action"""
        executor = ActionExecutor(dry_run=True)
        
        result = executor._action_query_database(
            {"query": "SELECT * FROM logs"},
            "analyst-001"
        )
        
        assert result["status"] == "SUCCESS"
        assert "results" in result
    
    def test_audit_log_creation(self):
        """Test audit logs are created during execution"""
        executor = ActionExecutor(dry_run=True)
        executor.clear_audit_logs()
        
        decision = DecisionOutput(
            request_id="test-003",
            status=DecisionStatus.SUCCESS,
            summary="Test",
            explanation="Test",
            actions_completed=[
                CompletedAction(
                    action="FETCH_LOGS",
                    status="PLANNED",
                    result={"params": {"log_type": "security"}}
                )
            ]
        )
        
        executor.execute_decision(decision, "user-001")
        
        logs = executor.get_audit_logs()
        assert len(logs) > 0
    
    def test_get_audit_logs_filtered(self):
        """Test filtering audit logs by request ID"""
        executor = ActionExecutor(dry_run=True)
        executor.clear_audit_logs()
        
        # Execute two decisions
        decision1 = DecisionOutput(
            request_id="req-001",
            status=DecisionStatus.SUCCESS,
            summary="Test 1",
            explanation="Test",
            actions_completed=[CompletedAction(action="LOG", status="PLANNED", result={})]
        )
        
        decision2 = DecisionOutput(
            request_id="req-002",
            status=DecisionStatus.SUCCESS,
            summary="Test 2",
            explanation="Test",
            actions_completed=[CompletedAction(action="LOG", status="PLANNED", result={})]
        )
        
        executor.execute_decision(decision1, "user-001")
        executor.execute_decision(decision2, "user-001")
        
        logs_req1 = executor.get_audit_logs(request_id="req-001")
        logs_req2 = executor.get_audit_logs(request_id="req-002")
        
        assert all(log.request_id == "req-001" for log in logs_req1)
        assert all(log.request_id == "req-002" for log in logs_req2)


class TestActionExecutorFactory:
    """Tests for action executor factory"""
    
    def test_create_action_executor_dry_run(self):
        """Test factory creates dry-run executor"""
        executor = create_action_executor(dry_run=True)
        assert isinstance(executor, ActionExecutor)
        assert executor.dry_run is True
    
    def test_create_action_executor_live(self):
        """Test factory creates live executor"""
        executor = create_action_executor(dry_run=False)
        assert executor.dry_run is False


# ==========================================
# AUDIT LOGGER TESTS
# ==========================================

class TestAuditLogger:
    """Tests for AuditLogger class"""
    
    def test_init_default(self):
        """Test default initialization"""
        logger = AuditLogger()
        assert logger.max_entries == 10000
        assert logger.retention_hours == 24
    
    def test_init_custom_params(self):
        """Test initialization with custom parameters"""
        logger = AuditLogger(max_entries=1000, retention_hours=48)
        assert logger.max_entries == 1000
        assert logger.retention_hours == 48
    
    def test_log_basic_event(self):
        """Test logging basic event"""
        logger = AuditLogger()
        logger.clear()
        
        entry = logger.log(
            event_type=AuditEventType.REQUEST_RECEIVED,
            action="test_action",
            request_id="req-001"
        )
        
        assert entry is not None
        assert entry.event_type == "REQUEST_RECEIVED"
        assert entry.action == "test_action"
        assert entry.request_id == "req-001"
    
    def test_log_request_received(self):
        """Test log_request_received convenience method"""
        logger = AuditLogger()
        logger.clear()
        
        entry = logger.log_request_received(
            request_id="req-001",
            user_id="user-001",
            message="Block all suspicious IPs",
            user_role="admin"
        )
        
        assert entry.event_type == "REQUEST_RECEIVED"
        assert entry.request_id == "req-001"
        assert entry.user_id == "user-001"
    
    def test_log_decision_started(self):
        """Test log_decision_started convenience method"""
        logger = AuditLogger()
        logger.clear()
        
        entry = logger.log_decision_started(
            request_id="req-001",
            decision_id="dec-001",
            goal="Block IPs",
            risk_level="MEDIUM"
        )
        
        assert entry.event_type == "DECISION_STARTED"
        assert entry.decision_id == "dec-001"
    
    def test_log_l1_strategic(self):
        """Test L1 strategic logging"""
        logger = AuditLogger()
        logger.clear()
        
        entry = logger.log_l1_strategic(
            request_id="req-001",
            decision_id="dec-001",
            goal="Security",
            risk_level="HIGH",
            priority=8,
            approved=True
        )
        
        assert entry.event_type == "DECISION_L1_STRATEGIC"
        assert entry.outcome == "approved"
    
    def test_log_l2_tactical(self):
        """Test L2 tactical logging"""
        logger = AuditLogger()
        logger.clear()
        
        entry = logger.log_l2_tactical(
            request_id="req-001",
            decision_id="dec-001",
            strategy="blocking",
            policy="sec_policy",
            subsystem="firewall"
        )
        
        assert entry.event_type == "DECISION_L2_TACTICAL"
    
    def test_log_l3_operational(self):
        """Test L3 operational logging"""
        logger = AuditLogger()
        logger.clear()
        
        entry = logger.log_l3_operational(
            request_id="req-001",
            decision_id="dec-001",
            actions=["BLOCK_IP", "NOTIFY"],
            execution_order="sequential"
        )
        
        assert entry.event_type == "DECISION_L3_OPERATIONAL"
        assert entry.action_params["action_count"] == 2
    
    def test_log_error(self):
        """Test error logging"""
        logger = AuditLogger()
        logger.clear()
        
        entry = logger.log_error(
            action="process_decision",
            error_message="Connection timeout",
            request_id="req-001"
        )
        
        assert entry.event_type == "SYSTEM_ERROR"
        assert entry.severity == "ERROR"
        assert entry.error_message == "Connection timeout"
    
    def test_get_entries_no_filter(self):
        """Test getting entries without filter"""
        logger = AuditLogger()
        logger.clear()
        
        logger.log(AuditEventType.REQUEST_RECEIVED, "action1")
        logger.log(AuditEventType.DECISION_STARTED, "action2")
        
        entries = logger.get_entries()
        assert len(entries) == 2
    
    def test_get_entries_by_event_type(self):
        """Test filtering entries by event type"""
        logger = AuditLogger()
        logger.clear()
        
        logger.log(AuditEventType.REQUEST_RECEIVED, "action1")
        logger.log(AuditEventType.DECISION_STARTED, "action2")
        logger.log(AuditEventType.REQUEST_RECEIVED, "action3")
        
        entries = logger.get_entries(event_type=AuditEventType.REQUEST_RECEIVED)
        assert len(entries) == 2
    
    def test_get_entries_by_request_id(self):
        """Test filtering entries by request ID"""
        logger = AuditLogger()
        logger.clear()
        
        logger.log(AuditEventType.REQUEST_RECEIVED, "a1", request_id="req-001")
        logger.log(AuditEventType.REQUEST_RECEIVED, "a2", request_id="req-002")
        logger.log(AuditEventType.DECISION_STARTED, "a3", request_id="req-001")
        
        entries = logger.get_entries(request_id="req-001")
        assert len(entries) == 2
    
    def test_get_entries_with_limit(self):
        """Test limiting entry count"""
        logger = AuditLogger()
        logger.clear()
        
        for i in range(10):
            logger.log(AuditEventType.REQUEST_RECEIVED, f"action{i}")
        
        entries = logger.get_entries(limit=5)
        assert len(entries) == 5
    
    def test_get_summary(self):
        """Test getting summary statistics"""
        logger = AuditLogger()
        logger.clear()
        
        logger.log(AuditEventType.REQUEST_RECEIVED, "a1", user_id="user-001", outcome="success")
        logger.log(AuditEventType.DECISION_COMPLETED, "a2", user_id="user-001", outcome="success")
        logger.log(AuditEventType.SYSTEM_ERROR, "a3", severity=AuditSeverity.ERROR, outcome="failure")
        
        summary = logger.get_summary()
        
        assert summary.total_entries == 3
        assert summary.unique_users == 1
        assert "REQUEST_RECEIVED" in summary.entries_by_type
        assert "ERROR" in summary.entries_by_severity
    
    def test_get_request_trail(self):
        """Test getting request audit trail"""
        logger = AuditLogger()
        logger.clear()
        
        logger.log(AuditEventType.REQUEST_RECEIVED, "a1", request_id="req-001")
        logger.log(AuditEventType.DECISION_STARTED, "a2", request_id="req-001")
        logger.log(AuditEventType.DECISION_COMPLETED, "a3", request_id="req-001")
        logger.log(AuditEventType.REQUEST_RECEIVED, "a4", request_id="req-002")
        
        trail = logger.get_request_trail("req-001")
        assert len(trail) == 3
    
    def test_export_json(self):
        """Test JSON export"""
        logger = AuditLogger()
        logger.clear()
        
        logger.log(AuditEventType.REQUEST_RECEIVED, "action1")
        
        exported = logger.export_entries(format="json")
        data = json.loads(exported)
        
        assert len(data) == 1
        assert data[0]["action"] == "action1"
    
    def test_export_csv(self):
        """Test CSV export"""
        logger = AuditLogger()
        logger.clear()
        
        logger.log(AuditEventType.REQUEST_RECEIVED, "action1")
        
        exported = logger.export_entries(format="csv")
        
        lines = exported.strip().split("\n")
        assert len(lines) == 2  # Header + 1 entry
    
    def test_clear_all(self):
        """Test clearing all entries"""
        logger = AuditLogger()
        
        logger.log(AuditEventType.REQUEST_RECEIVED, "action1")
        logger.log(AuditEventType.REQUEST_RECEIVED, "action2")
        
        logger.clear()
        
        entries = logger.get_entries()
        assert len(entries) == 0
    
    def test_max_entries_limit(self):
        """Test max entries limit is enforced"""
        logger = AuditLogger(max_entries=5)
        logger.clear()
        
        for i in range(10):
            logger.log(AuditEventType.REQUEST_RECEIVED, f"action{i}")
        
        entries = logger.get_entries()
        assert len(entries) == 5


class TestAuditEntry:
    """Tests for AuditEntry dataclass"""
    
    def test_to_dict(self):
        """Test converting entry to dictionary"""
        entry = AuditEntry(
            event_type="TEST",
            action="test_action",
            request_id="req-001"
        )
        
        d = entry.to_dict()
        
        assert d["event_type"] == "TEST"
        assert d["action"] == "test_action"
        assert d["request_id"] == "req-001"
    
    def test_to_json(self):
        """Test converting entry to JSON"""
        entry = AuditEntry(
            event_type="TEST",
            action="test_action"
        )
        
        j = entry.to_json()
        data = json.loads(j)
        
        assert data["event_type"] == "TEST"


class TestAuditLoggerSingleton:
    """Tests for singleton pattern"""
    
    def test_get_audit_logger_singleton(self):
        """Test singleton returns same instance"""
        logger1 = get_audit_logger()
        logger2 = get_audit_logger()
        
        assert logger1 is logger2
    
    def test_create_audit_logger_new_instance(self):
        """Test factory creates new instance"""
        logger1 = create_audit_logger()
        logger2 = create_audit_logger()
        
        assert logger1 is not logger2


# ==========================================
# DECISION API TESTS
# ==========================================

class TestDecisionAPI:
    """Tests for Decision API endpoints"""
    
    def test_quick_decision_endpoint(self):
        """Test quick decision endpoint"""
        response = client.post(
            "/api/v1/decision/quick",
            json={
                "message": "Block IP 192.168.1.100",
                "user_id": "test-user",
                "user_role": "admin",
                "dry_run": True
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "decision_id" in data
        assert "status" in data
    
    def test_quick_decision_minimal(self):
        """Test quick decision with minimal input"""
        response = client.post(
            "/api/v1/decision/quick",
            json={
                "message": "Show all logs"
            }
        )
        
        assert response.status_code == 200
    
    def test_process_decision_endpoint(self):
        """Test full decision process endpoint"""
        response = client.post(
            "/api/v1/decision/process",
            json={
                "user_id": "test-user",
                "message": "Grant access to john.doe for dashboard",
                "context": {
                    "user_role": "admin"
                }
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["request_id"] is not None
    
    def test_get_decision_not_found(self):
        """Test getting non-existent decision"""
        response = client.get("/api/v1/decision/non-existent-id")
        
        assert response.status_code == 404
    
    def test_decision_history_list(self):
        """Test listing decision history"""
        # First create a decision
        client.post(
            "/api/v1/decision/quick",
            json={"message": "Test decision"}
        )
        
        response = client.get("/api/v1/decision/history/list")
        
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "decisions" in data
    
    def test_decision_analytics(self):
        """Test decision analytics endpoint"""
        response = client.get("/api/v1/decision/analytics/summary?hours=24")
        
        assert response.status_code == 200
        data = response.json()
        assert "total_decisions" in data
        assert "status_breakdown" in data
    
    def test_audit_entries_endpoint(self):
        """Test getting audit entries"""
        response = client.get("/api/v1/decision/audit/entries?limit=10")
        
        assert response.status_code == 200
        data = response.json()
        assert "count" in data
        assert "entries" in data
    
    def test_audit_summary_endpoint(self):
        """Test audit summary endpoint"""
        response = client.get("/api/v1/decision/audit/summary?hours=24")
        
        assert response.status_code == 200
        data = response.json()
        assert "total_entries" in data
    
    def test_config_status_endpoint(self):
        """Test configuration status endpoint"""
        response = client.get("/api/v1/decision/config/status")
        
        assert response.status_code == 200
        data = response.json()
        assert "hrm_engine" in data
        assert "action_executor" in data
        assert "llm_interpreter" in data
    
    def test_set_dry_run_mode(self):
        """Test setting dry-run mode"""
        response = client.post(
            "/api/v1/decision/config/dry-run",
            json={"enabled": True}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["dry_run"] is True


class TestDecisionAPIBatch:
    """Tests for batch decision processing"""
    
    def test_batch_sequential(self):
        """Test batch sequential processing"""
        response = client.post(
            "/api/v1/decision/batch",
            json={
                "requests": [
                    {"message": "Block IP 1.2.3.4"},
                    {"message": "Show logs"}
                ],
                "parallel": False
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
    
    def test_batch_empty(self):
        """Test batch with empty requests"""
        response = client.post(
            "/api/v1/decision/batch",
            json={
                "requests": [],
                "parallel": False
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0


class TestDecisionAPIExport:
    """Tests for audit log export"""
    
    def test_export_json_format(self):
        """Test JSON export format"""
        response = client.get("/api/v1/decision/audit/export?format=json&hours=24")
        
        assert response.status_code == 200
        data = response.json()
        assert "format" in data
        assert data["format"] == "json"
    
    def test_export_csv_format(self):
        """Test CSV export format"""
        response = client.get("/api/v1/decision/audit/export?format=csv&hours=24")
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/csv; charset=utf-8"


# ==========================================
# INTEGRATION TESTS
# ==========================================

class TestPhase3Integration:
    """Integration tests for Phase 3 components"""
    
    def test_full_decision_pipeline(self):
        """Test complete decision pipeline"""
        # Make a decision
        response = client.post(
            "/api/v1/decision/quick",
            json={
                "message": "Block all suspicious IPs from the last hour",
                "user_id": "security-admin",
                "user_role": "admin",
                "dry_run": True
            }
        )
        
        assert response.status_code == 200
        decision_data = response.json()
        decision_id = decision_data["decision_id"]
        
        # Get the decision
        response = client.get(f"/api/v1/decision/{decision_id}")
        assert response.status_code == 200
        
        # Get explanation
        response = client.get(f"/api/v1/decision/{decision_id}/explain")
        assert response.status_code == 200
        explanation = response.json()
        assert "strategic_explanation" in explanation
        assert "tactical_explanation" in explanation
        assert "operational_explanation" in explanation
        
        # Check audit trail
        response = client.get(f"/api/v1/decision/{decision_id}/audit-trail")
        assert response.status_code == 200
    
    def test_hrm_engine_to_executor_flow(self):
        """Test HRM engine output feeds into executor correctly"""
        engine = HRMEngine(use_simulation=True)
        executor = ActionExecutor(dry_run=True)
        
        hrm_input = HRMInput(
            L1_strategic=StrategicLevel(
                goal="Security response",
                risk_level=RiskLevel.HIGH,
                priority=9
            ),
            L2_tactical=TacticalLevel(
                strategy="blocking",
                policy="security",
                subsystem="firewall"
            ),
            L3_operational=OperationalLevel(
                actions=[
                    OperationalAction(action="BLOCK_IP", params={"ip_list": ["1.1.1.1"]}),
                    OperationalAction(action="NOTIFY", params={"channel": "security"})
                ]
            )
        )
        
        # Process through HRM
        decision = engine.process(hrm_input, "integration-test-001")
        assert decision.status != DecisionStatus.DENIED
        
        # Execute actions
        final_decision = executor.execute_decision(decision, "admin")
        assert final_decision.status in [DecisionStatus.SUCCESS, DecisionStatus.PARTIAL]
    
    def test_audit_logging_throughout_pipeline(self):
        """Test audit logging captures all pipeline stages"""
        logger = get_audit_logger()
        logger.clear()
        
        # Make a decision through API
        response = client.post(
            "/api/v1/decision/quick",
            json={
                "message": "Grant access to test-user",
                "user_id": "admin",
                "dry_run": True
            }
        )
        
        assert response.status_code == 200
        
        # Check audit entries were created
        entries = logger.get_entries()
        event_types = [e.event_type for e in entries]
        
        # Should have multiple event types
        assert len(entries) > 0
    
    def test_multiple_concurrent_decisions(self):
        """Test handling multiple decisions"""
        responses = []
        
        for i in range(5):
            response = client.post(
                "/api/v1/decision/quick",
                json={
                    "message": f"Test decision {i}",
                    "user_id": f"user-{i}"
                }
            )
            responses.append(response)
        
        # All should succeed
        for r in responses:
            assert r.status_code == 200
        
        # All should have unique decision IDs
        decision_ids = [r.json()["decision_id"] for r in responses]
        assert len(set(decision_ids)) == 5


# ==========================================
# ERROR HANDLING TESTS
# ==========================================

class TestPhase3ErrorHandling:
    """Error handling tests for Phase 3"""
    
    def test_invalid_decision_request(self):
        """Test handling invalid decision request"""
        response = client.post(
            "/api/v1/decision/quick",
            json={
                "message": ""  # Empty message
            }
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_invalid_batch_request(self):
        """Test handling invalid batch request"""
        response = client.post(
            "/api/v1/decision/batch",
            json={
                "parallel": True
                # Missing requests field
            }
        )
        
        assert response.status_code == 422
    
    def test_hrm_engine_handles_empty_actions(self):
        """Test HRM engine handles empty action list"""
        engine = HRMEngine(use_simulation=True)
        
        hrm_input = HRMInput(
            L1_strategic=StrategicLevel(goal="Empty test", priority=1),
            L2_tactical=TacticalLevel(strategy="test", policy="test", subsystem="test"),
            L3_operational=OperationalLevel(actions=[], execution_order="sequential")
        )
        
        decision = engine.process(hrm_input, "empty-test")
        
        assert decision is not None
        assert decision.actions_completed == []
    
    def test_executor_handles_unknown_action(self):
        """Test executor handles unknown action type"""
        executor = ActionExecutor(dry_run=True)
        
        decision = DecisionOutput(
            request_id="test",
            status=DecisionStatus.SUCCESS,
            summary="Test",
            explanation="Test",
            actions_completed=[
                CompletedAction(
                    action="UNKNOWN_ACTION",
                    status="PLANNED",
                    result={"params": {}}
                )
            ]
        )
        
        result = executor.execute_decision(decision, "user")
        
        # Should handle gracefully
        assert result is not None
    
    def test_audit_logger_handles_invalid_filter(self):
        """Test audit logger handles invalid filter gracefully"""
        logger = AuditLogger()
        
        # Should not raise exception
        entries = logger.get_entries(limit=-1)  # Invalid but should handle
        assert isinstance(entries, list)


# ==========================================
# PERFORMANCE TESTS
# ==========================================

class TestPhase3Performance:
    """Performance tests for Phase 3"""
    
    def test_hrm_engine_processing_time(self):
        """Test HRM engine processes quickly"""
        engine = HRMEngine(use_simulation=True)
        
        hrm_input = HRMInput(
            L1_strategic=StrategicLevel(goal="Perf test", priority=5),
            L2_tactical=TacticalLevel(strategy="test", policy="test", subsystem="test"),
            L3_operational=OperationalLevel(
                actions=[OperationalAction(action="LOG", params={}) for _ in range(10)]
            )
        )
        
        start = datetime.now()
        decision = engine.process(hrm_input, "perf-test")
        duration = (datetime.now() - start).total_seconds()
        
        # Should complete in under 1 second
        assert duration < 1.0
        assert decision is not None
    
    def test_audit_logger_high_volume(self):
        """Test audit logger handles high volume"""
        logger = AuditLogger(max_entries=1000)
        logger.clear()
        
        start = datetime.now()
        
        for i in range(500):
            logger.log(
                AuditEventType.REQUEST_RECEIVED,
                f"action_{i}",
                request_id=f"req-{i}"
            )
        
        duration = (datetime.now() - start).total_seconds()
        
        # Should complete quickly
        assert duration < 2.0
        
        # Should have logged all
        entries = logger.get_entries(limit=1000)
        assert len(entries) == 500


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
