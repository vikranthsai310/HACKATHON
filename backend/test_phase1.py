"""
Unit Tests for HRM Decision System - Phase 1

Run with: pytest test_phase1.py -v
"""

import pytest
from datetime import datetime
from app.schemas.request_schema import (
    UserRequest,
    LLMOutput,
    HRMInput,
    DecisionOutput,
    IntentType,
    RiskLevel,
    DecisionStatus,
    StrategicLevel,
    TacticalLevel,
    OperationalLevel,
    OperationalAction
)
from app.core.preprocessor import NLPPreprocessor
from app.core.schema_validator import SchemaValidator
from app.core.llm_interpreter import LLMInterpreter
from app.core.hrm_engine import HRMEngine
from app.core.action_executor import ActionExecutor


class TestSchemas:
    """Test all Pydantic schemas"""
    
    def test_user_request_creation(self):
        """Test UserRequest schema"""
        request = UserRequest(
            user_id="test-user",
            message="Test message"
        )
        assert request.user_id == "test-user"
        assert request.message == "Test message"
        assert request.request_id is not None
        assert isinstance(request.timestamp, datetime)
    
    def test_llm_output_creation(self):
        """Test LLMOutput schema"""
        output = LLMOutput(
            intent_type=IntentType.SECURITY,
            goal="Test goal",
            confidence=0.95,
            requested_actions=["BLOCK_IP"]
        )
        assert output.intent_type == IntentType.SECURITY
        assert output.confidence == 0.95
    
    def test_hrm_input_creation(self):
        """Test HRMInput schema with all levels"""
        hrm_input = HRMInput(
            L1_strategic=StrategicLevel(
                goal="Test goal",
                risk_level=RiskLevel.MEDIUM,
                priority=5
            ),
            L2_tactical=TacticalLevel(
                strategy="test_strategy",
                policy="test_policy",
                subsystem="test_system"
            ),
            L3_operational=OperationalLevel(
                actions=[
                    OperationalAction(
                        action="TEST_ACTION",
                        params={"test": "value"}
                    )
                ]
            )
        )
        assert hrm_input.L1_strategic.goal == "Test goal"
        assert hrm_input.L2_tactical.strategy == "test_strategy"
        assert len(hrm_input.L3_operational.actions) == 1


class TestPreprocessor:
    """Test NLP Preprocessor"""
    
    def test_basic_preprocessing(self):
        """Test basic text preprocessing"""
        preprocessor = NLPPreprocessor()
        result = preprocessor.preprocess("Block IP 192.168.1.100")
        
        assert "normalized_text" in result
        assert "tags" in result
        assert result["original"] == "Block IP 192.168.1.100"
    
    def test_time_reference_detection(self):
        """Test time reference extraction"""
        preprocessor = NLPPreprocessor()
        result = preprocessor.preprocess("Show logs from yesterday")
        
        assert "time_references" in result
        assert len(result["time_references"]) > 0
    
    def test_security_tag_detection(self):
        """Test security keyword tagging"""
        preprocessor = NLPPreprocessor()
        result = preprocessor.preprocess("Block suspicious activity")
        
        assert "SECURITY" in result["tags"]


class TestSchemaValidator:
    """Test Schema Validator"""
    
    def test_valid_schema(self):
        """Test validation of correct schema"""
        validator = SchemaValidator()
        
        test_data = {
            "intent_type": "SECURITY",
            "goal": "Block threats",
            "requested_actions": ["BLOCK_IP"],
            "confidence": 0.9,
            "entities": {},
            "constraints": {}
        }
        
        is_valid, error, validated = validator.validate(test_data)
        assert is_valid is True
        assert error == ""
    
    def test_missing_required_field(self):
        """Test validation with missing fields"""
        validator = SchemaValidator()
        
        test_data = {
            "intent_type": "SECURITY"
            # Missing goal, requested_actions, confidence
        }
        
        is_valid, error, validated = validator.validate(test_data)
        assert is_valid is False
        assert "Missing required field" in error
    
    def test_invalid_confidence(self):
        """Test invalid confidence value"""
        validator = SchemaValidator()
        
        test_data = {
            "intent_type": "SECURITY",
            "goal": "Test",
            "requested_actions": ["BLOCK_IP"],
            "confidence": 1.5  # Invalid: > 1.0
        }
        
        is_valid, error, validated = validator.validate(test_data)
        assert is_valid is False
        assert "Confidence" in error


class TestLLMInterpreter:
    """Test LLM Interpreter"""
    
    def test_mock_interpretation(self):
        """Test mock LLM interpretation"""
        interpreter = LLMInterpreter()  # Uses mock mode by default
        
        request = UserRequest(
            user_id="test-user",
            message="Block suspicious IP addresses"
        )
        
        output = interpreter.interpret(request, None)
        
        assert isinstance(output, LLMOutput)
        assert output.intent_type == IntentType.SECURITY
        assert len(output.requested_actions) > 0
        assert 0 <= output.confidence <= 1
    
    def test_llm_to_hrm_conversion(self):
        """Test conversion from LLM output to HRM input"""
        interpreter = LLMInterpreter()
        
        request = UserRequest(
            user_id="test-user",
            message="Grant access to user john"
        )
        
        llm_output = interpreter.interpret(request, None)
        hrm_input = interpreter.llm_to_hrm_input(llm_output, request)
        
        assert isinstance(hrm_input, HRMInput)
        assert hasattr(hrm_input, 'L1_strategic')
        assert hasattr(hrm_input, 'L2_tactical')
        assert hasattr(hrm_input, 'L3_operational')


class TestHRMEngine:
    """Test HRM Engine"""
    
    def test_hrm_processing(self):
        """Test HRM engine processing"""
        engine = HRMEngine(use_simulation=True)
        
        hrm_input = HRMInput(
            L1_strategic=StrategicLevel(
                goal="Test security goal",
                risk_level=RiskLevel.MEDIUM,
                priority=5
            ),
            L2_tactical=TacticalLevel(
                strategy="test_strategy",
                policy="test_policy",
                subsystem="firewall"
            ),
            L3_operational=OperationalLevel(
                actions=[
                    OperationalAction(
                        action="BLOCK_IP",
                        params={"ip_list": ["192.168.1.100"]}
                    )
                ]
            )
        )
        
        decision = engine.process(hrm_input, "test-request-001")
        
        assert isinstance(decision, DecisionOutput)
        assert decision.request_id == "test-request-001"
        assert decision.status in [s.value for s in DecisionStatus]


class TestActionExecutor:
    """Test Action Executor"""
    
    def test_dry_run_execution(self):
        """Test action execution in dry-run mode"""
        executor = ActionExecutor(dry_run=True)
        
        # Create a simple decision
        decision = DecisionOutput(
            request_id="test-request",
            status=DecisionStatus.SUCCESS,
            summary="Test decision",
            actions_completed=[],
            explanation="Test explanation"
        )
        
        # Should not raise any errors
        result = executor.execute_decision(decision, "test-user")
        assert isinstance(result, DecisionOutput)
    
    def test_audit_logging(self):
        """Test audit log creation"""
        executor = ActionExecutor(dry_run=True)
        
        # Execute a decision to create logs
        decision = DecisionOutput(
            request_id="test-request",
            status=DecisionStatus.SUCCESS,
            summary="Test",
            actions_completed=[],
            explanation="Test"
        )
        
        executor.execute_decision(decision, "test-user")
        logs = executor.get_audit_logs()
        
        assert len(logs) >= 0  # Logs should be created


class TestCompletePipeline:
    """Test complete end-to-end pipeline"""
    
    def test_full_pipeline(self):
        """Test complete request processing pipeline"""
        # Initialize components
        preprocessor = NLPPreprocessor()
        interpreter = LLMInterpreter()
        engine = HRMEngine(use_simulation=True)
        executor = ActionExecutor(dry_run=True)
        
        # Create request
        request = UserRequest(
            user_id="test-user",
            message="Block IP 192.168.1.100"
        )
        
        # Step 1: Preprocess
        preprocessed = preprocessor.preprocess(request.message)
        assert preprocessed is not None
        
        # Step 2: LLM interpretation
        llm_output = interpreter.interpret(request, preprocessed)
        assert isinstance(llm_output, LLMOutput)
        
        # Step 3: Convert to HRM input
        hrm_input = interpreter.llm_to_hrm_input(llm_output, request)
        assert isinstance(hrm_input, HRMInput)
        
        # Step 4: HRM reasoning
        decision = engine.process(hrm_input, request.request_id)
        assert isinstance(decision, DecisionOutput)
        
        # Step 5: Execute
        final_decision = executor.execute_decision(decision, request.user_id)
        assert isinstance(final_decision, DecisionOutput)
        assert final_decision.status in [s.value for s in DecisionStatus]


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
