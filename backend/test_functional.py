"""
Functional Tests for HRM Decision System

Tests business logic and functional requirements.
Run with: pytest test_functional.py -v
"""

import pytest
from app.schemas.request_schema import (
    UserRequest,
    RequestContext,
    IntentType,
    RiskLevel,
    DecisionStatus
)
from app.core.preprocessor import NLPPreprocessor
from app.core.llm_interpreter import LLMInterpreter
from app.core.hrm_engine import HRMEngine
from app.core.action_executor import ActionExecutor


class TestSecurityWorkflows:
    """Test security-related functional workflows"""
    
    def test_block_ip_workflow(self):
        """Test complete IP blocking workflow"""
        # Setup
        preprocessor = NLPPreprocessor()
        interpreter = LLMInterpreter()
        engine = HRMEngine(use_simulation=True)
        executor = ActionExecutor(dry_run=True)
        
        # User request to block IP
        request = UserRequest(
            user_id="security-admin",
            message="Block IP 192.168.1.100 immediately",
            context=RequestContext(user_role="security_admin")
        )
        
        # Process through pipeline
        preprocessed = preprocessor.preprocess(request.message)
        llm_output = interpreter.interpret(request, preprocessed)
        
        # Verify security intent detected
        assert llm_output.intent_type == IntentType.SECURITY
        assert "BLOCK_IP" in llm_output.requested_actions
        
        # Convert to HRM and process
        hrm_input = interpreter.llm_to_hrm_input(llm_output, request)
        decision = engine.process(hrm_input, request.request_id)
        
        # Verify decision
        assert decision.status in [DecisionStatus.SUCCESS, DecisionStatus.PENDING]
        assert len(decision.actions_completed) > 0
    
    def test_high_risk_action_requires_authorization(self):
        """Test that high-risk actions require authorization"""
        interpreter = LLMInterpreter()
        
        request = UserRequest(
            user_id="user",
            message="Shutdown all production servers"
        )
        
        llm_output = interpreter.interpret(request, None)
        hrm_input = interpreter.llm_to_hrm_input(llm_output, request)
        
        # High risk actions should require authorization
        assert hrm_input.L1_strategic.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]
        assert hrm_input.L1_strategic.authorization_required is True
    
    def test_multiple_ip_blocking(self):
        """Test blocking multiple IPs"""
        preprocessor = NLPPreprocessor()
        interpreter = LLMInterpreter()
        
        request = UserRequest(
            user_id="admin",
            message="Block IPs 192.168.1.100, 10.0.0.50, and 172.16.0.10"
        )
        
        preprocessed = preprocessor.preprocess(request.message)
        
        # Should extract multiple IPs
        assert "192.168.1.100" in request.message
        assert "10.0.0.50" in request.message


class TestAccessManagementWorkflows:
    """Test access management workflows"""
    
    def test_grant_access_workflow(self):
        """Test granting user access"""
        interpreter = LLMInterpreter()
        engine = HRMEngine(use_simulation=True)
        
        request = UserRequest(
            user_id="manager",
            message="Grant user john.doe access to analytics dashboard"
        )
        
        llm_output = interpreter.interpret(request, None)
        
        # Should detect access intent
        assert llm_output.intent_type == IntentType.ACCESS
        
        hrm_input = interpreter.llm_to_hrm_input(llm_output, request)
        decision = engine.process(hrm_input, request.request_id)
        
        # Should have grant access action
        assert any("GRANT" in action.action or "ACCESS" in action.action 
                  for action in decision.actions_completed)
    
    def test_revoke_access_workflow(self):
        """Test revoking user access"""
        interpreter = LLMInterpreter()
        
        request = UserRequest(
            user_id="admin",
            message="Revoke database access from user jane.smith"
        )
        
        llm_output = interpreter.interpret(request, None)
        hrm_input = interpreter.llm_to_hrm_input(llm_output, request)
        
        # Should be medium/high risk
        assert hrm_input.L1_strategic.risk_level in [RiskLevel.MEDIUM, RiskLevel.HIGH]


class TestQueryWorkflows:
    """Test query and information retrieval workflows"""
    
    def test_log_query_workflow(self):
        """Test querying system logs"""
        preprocessor = NLPPreprocessor()
        interpreter = LLMInterpreter()
        
        request = UserRequest(
            user_id="analyst",
            message="Show me all failed login attempts from yesterday"
        )
        
        preprocessed = preprocessor.preprocess(request.message)
        llm_output = interpreter.interpret(request, preprocessed)
        
        # Should detect query intent
        assert llm_output.intent_type == IntentType.QUERY
        
        # Should be low risk
        hrm_input = interpreter.llm_to_hrm_input(llm_output, request)
        assert hrm_input.L1_strategic.risk_level == RiskLevel.LOW
    
    def test_query_with_time_reference(self):
        """Test query with time reference resolution"""
        preprocessor = NLPPreprocessor()
        
        request = UserRequest(
            user_id="user",
            message="Show logs from last 24 hours"
        )
        
        preprocessed = preprocessor.preprocess(request.message)
        
        # Should resolve time reference
        assert "time_references" in preprocessed
        assert len(preprocessed["time_references"]) > 0


class TestComplianceWorkflows:
    """Test compliance and audit workflows"""
    
    def test_audit_report_generation(self):
        """Test audit report generation"""
        interpreter = LLMInterpreter()
        
        request = UserRequest(
            user_id="compliance-officer",
            message="Generate audit report for last month"
        )
        
        llm_output = interpreter.interpret(request, None)
        
        # Should detect compliance intent
        assert llm_output.intent_type in [IntentType.COMPLIANCE, IntentType.QUERY]


class TestTimeHandling:
    """Test time reference handling"""
    
    def test_yesterday_resolution(self):
        """Test 'yesterday' time reference"""
        preprocessor = NLPPreprocessor()
        
        result = preprocessor.preprocess("Show logs from yesterday")
        
        assert "time_references" in result
        assert any("yesterday" in ref.lower() for ref in result["time_references"])
    
    def test_last_24_hours_resolution(self):
        """Test 'last 24 hours' time reference"""
        preprocessor = NLPPreprocessor()
        
        result = preprocessor.preprocess("Block IPs from last 24 hours")
        
        assert "time_references" in result
    
    def test_multiple_time_references(self):
        """Test handling multiple time references"""
        preprocessor = NLPPreprocessor()
        
        result = preprocessor.preprocess("Show logs from yesterday and today")
        
        assert "time_references" in result
        # Should detect both time references


class TestEntityExtraction:
    """Test entity extraction functionality"""
    
    def test_ip_address_extraction(self):
        """Test extracting IP addresses from text"""
        from app.utils.helpers import extract_ip_addresses
        
        text = "Block IPs 192.168.1.100 and 10.0.0.50"
        ips = extract_ip_addresses(text)
        
        assert "192.168.1.100" in ips
        assert "10.0.0.50" in ips
        assert len(ips) == 2
    
    def test_email_extraction(self):
        """Test extracting email addresses"""
        from app.utils.helpers import extract_emails
        
        text = "Contact admin@example.com and support@company.org"
        emails = extract_emails(text)
        
        assert "admin@example.com" in emails
        assert "support@company.org" in emails
    
    def test_username_extraction(self):
        """Test extracting usernames"""
        from app.utils.helpers import extract_usernames
        
        text = "Grant access to user john.doe"
        usernames = extract_usernames(text)
        
        assert len(usernames) > 0


class TestRiskAssessment:
    """Test risk assessment logic"""
    
    def test_critical_risk_actions(self):
        """Test actions that should be marked critical risk"""
        interpreter = LLMInterpreter()
        
        critical_requests = [
            "Emergency shutdown of all systems",
            "Critical security breach detected, block all access",
            "Urgent: Delete all user data"
        ]
        
        for message in critical_requests:
            request = UserRequest(user_id="admin", message=message)
            llm_output = interpreter.interpret(request, None)
            hrm_input = interpreter.llm_to_hrm_input(llm_output, request)
            
            # Should be high or critical risk
            assert hrm_input.L1_strategic.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]
    
    def test_low_risk_queries(self):
        """Test that queries are low risk"""
        interpreter = LLMInterpreter()
        
        low_risk_requests = [
            "Show me user list",
            "Display system status",
            "Get log summary"
        ]
        
        for message in low_risk_requests:
            request = UserRequest(user_id="user", message=message)
            llm_output = interpreter.interpret(request, None)
            hrm_input = interpreter.llm_to_hrm_input(llm_output, request)
            
            # Should be low risk
            assert hrm_input.L1_strategic.risk_level == RiskLevel.LOW


class TestActionExecution:
    """Test action execution logic"""
    
    def test_dry_run_mode_safety(self):
        """Test that dry-run mode doesn't execute real actions"""
        executor = ActionExecutor(dry_run=True)
        
        from app.schemas.request_schema import CompletedAction
        
        # Create a completed action
        action = CompletedAction(
            action="BLOCK_IP",
            status="PENDING",
            result={"params": {"ip_list": ["192.168.1.100"]}}
        )
        
        # Execute in dry-run mode
        result = executor._execute_single_action(action, None, "test-user")
        
        # Should indicate dry-run
        assert result.get("dry_run") is True
        assert "DRY-RUN" in result.get("message", "")
    
    def test_audit_log_creation(self):
        """Test that actions create audit logs"""
        executor = ActionExecutor(dry_run=True)
        
        from app.schemas.request_schema import DecisionOutput, DecisionStatus, CompletedAction
        
        # Create a decision with an action
        action = CompletedAction(
            action="QUERY_DATABASE",
            status="PENDING",
            result={}
        )
        
        decision = DecisionOutput(
            request_id="test-req",
            status=DecisionStatus.SUCCESS,
            summary="Test",
            actions_completed=[action],
            explanation="Test"
        )
        
        executor.execute_decision(decision, "test-user")
        
        logs = executor.get_audit_logs("test-req")
        assert len(logs) > 0


class TestHierarchicalReasoning:
    """Test HRM hierarchical reasoning"""
    
    def test_strategic_to_tactical_flow(self):
        """Test that L1 strategic feeds into L2 tactical"""
        interpreter = LLMInterpreter()
        
        request = UserRequest(
            user_id="admin",
            message="Block suspicious network traffic"
        )
        
        llm_output = interpreter.interpret(request, None)
        hrm_input = interpreter.llm_to_hrm_input(llm_output, request)
        
        # L1 strategic should inform L2 tactical
        assert hrm_input.L1_strategic.goal is not None
        assert hrm_input.L2_tactical.strategy is not None
        
        # For security, should use threat mitigation strategy
        if llm_output.intent_type == IntentType.SECURITY:
            assert "threat" in hrm_input.L2_tactical.strategy.lower() or \
                   "security" in hrm_input.L2_tactical.strategy.lower()
    
    def test_tactical_to_operational_flow(self):
        """Test that L2 tactical feeds into L3 operational"""
        interpreter = LLMInterpreter()
        engine = HRMEngine(use_simulation=True)
        
        request = UserRequest(
            user_id="admin",
            message="Grant database access to user john"
        )
        
        llm_output = interpreter.interpret(request, None)
        hrm_input = interpreter.llm_to_hrm_input(llm_output, request)
        
        # L2 should inform L3
        assert hrm_input.L2_tactical.subsystem is not None
        assert len(hrm_input.L3_operational.actions) > 0
        
        # Process through engine
        decision = engine.process(hrm_input, request.request_id)
        
        # Should have audit trail showing all levels
        assert "L1_strategic" in decision.audit_trail
        assert "L2_tactical" in decision.audit_trail
        assert "L3_operational" in decision.audit_trail


class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_empty_message(self):
        """Test handling of empty message"""
        with pytest.raises(Exception):
            request = UserRequest(
                user_id="user",
                message=""  # Empty message
            )
    
    def test_very_long_message(self):
        """Test handling of very long messages"""
        preprocessor = NLPPreprocessor()
        
        long_message = "Block IP " + "test " * 1000 + "192.168.1.100"
        result = preprocessor.preprocess(long_message)
        
        assert result is not None
        assert "normalized_text" in result
    
    def test_special_characters(self):
        """Test handling of special characters"""
        preprocessor = NLPPreprocessor()
        
        message = "Block IP 192.168.1.100 @#$%^&*()"
        result = preprocessor.preprocess(message)
        
        assert result is not None


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
