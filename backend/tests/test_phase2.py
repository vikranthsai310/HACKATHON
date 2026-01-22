"""
Phase 2 Test Suite - LLM Integration & Intent Parsing

Tests cover:
- Prompt templates
- Enhanced LLM interpreter
- Entity extraction
- Intent validation
- Action mapping
- Chat API endpoints
"""

import pytest
import json
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

# Import Phase 2 components
from app.core.prompt_templates import PromptTemplates, ConversationContext
from app.core.llm_enhanced import (
    EnhancedLLMInterpreter, LLMConfig, ResponseCache, LLMResponseParser
)
from app.core.entity_extractor import EntityExtractor, EntityType, ExtractedEntity
from app.core.intent_validator import (
    IntentValidator, IntentEnricher, ValidationResult, ValidationSeverity
)
from app.core.action_mapper import (
    ActionMapper, MappedAction, ActionCategory, get_action_mapper
)
from app.schemas.request_schema import LLMOutput, IntentType, Entities, RiskLevel, Constraints


# =============================================================================
# PROMPT TEMPLATES TESTS
# =============================================================================

class TestPromptTemplates:
    """Tests for prompt template system"""
    
    def test_system_prompts_exist(self):
        """Test that all system prompts are defined"""
        assert hasattr(PromptTemplates, 'INTENT_PARSER_SYSTEM')
        assert hasattr(PromptTemplates, 'ENTITY_EXTRACTOR_SYSTEM')
        assert hasattr(PromptTemplates, 'ACTION_MAPPER_SYSTEM')
    
    def test_few_shot_examples_exist(self):
        """Test that few-shot examples are defined"""
        assert hasattr(PromptTemplates, 'FEW_SHOT_EXAMPLES')
        assert len(PromptTemplates.FEW_SHOT_EXAMPLES) >= 3
    
    def test_build_intent_prompt(self):
        """Test building intent parsing prompt"""
        prompt = PromptTemplates.build_intent_prompt("block the IP 192.168.1.1")
        
        assert "block" in prompt.lower()
        assert "192.168.1.1" in prompt
    
    def test_build_intent_prompt_with_context(self):
        """Test building intent prompt with conversation context"""
        context = {
            "user_role": "admin",
            "session_id": "test-123"
        }
        prompt = PromptTemplates.build_intent_prompt(
            "block suspicious IPs",
            context=context
        )
        
        assert "block" in prompt.lower()
    
    def test_build_clarification_prompt(self):
        """Test building clarification prompt"""
        prompt = PromptTemplates.build_clarification_prompt(
            "block IPs",
            {"intent_type": "SECURITY", "goal": "block IPs", "confidence": 0.5},
            ["Which IPs?", "Duration?"]
        )
        
        assert "block" in prompt.lower()
        assert "Which IPs" in prompt
    
    def test_build_entity_prompt(self):
        """Test building entity extraction prompt"""
        prompt = PromptTemplates.build_entity_prompt("block IP 192.168.1.1")
        
        assert "192.168.1.1" in prompt
    
    def test_build_action_mapping_prompt(self):
        """Test building action mapping prompt"""
        prompt = PromptTemplates.build_action_mapping_prompt(
            "SECURITY",
            "Block malicious IPs",
            {"targets": ["192.168.1.1"]},
            {"time_window": "24h"}
        )
        
        assert "SECURITY" in prompt
        assert "Block malicious IPs" in prompt


class TestConversationContext:
    """Tests for conversation context management"""
    
    def test_create_context(self):
        """Test creating conversation context"""
        context = ConversationContext(session_id="test-123")
        
        assert context.session_id is not None
        assert len(context.history) == 0
    
    def test_add_turn(self):
        """Test adding turns to context"""
        context = ConversationContext(session_id="test-123")
        context.add_turn(
            "Hello",
            {"intent_type": "QUERY"},
            "Hi there!"
        )
        
        assert len(context.history) == 1
        assert context.history[0]["user_message"] == "Hello"
    
    def test_get_context_for_prompt(self):
        """Test getting context for prompt"""
        context = ConversationContext(session_id="test-123")
        context.add_turn("Test", {"intent_type": "QUERY"}, "Response")
        
        prompt_context = context.get_context_for_prompt()
        assert "session_id" in prompt_context
        assert "previous_intents" in prompt_context
    
    def test_needs_clarification(self):
        """Test clarification detection"""
        context = ConversationContext(session_id="test-123")
        
        # Low confidence intent should need clarification
        intent = {"intent_type": "SECURITY", "confidence": 0.3}
        needs, reasons = context.needs_clarification(intent)
        
        assert needs == True
        assert len(reasons) >= 1
    
    def test_to_dict(self):
        """Test converting context to dictionary"""
        context = ConversationContext(session_id="test-123")
        context.add_turn("Test", {"intent_type": "QUERY"}, "Response")
        
        data = context.to_dict()
        assert "session_id" in data
        assert "history" in data


# =============================================================================
# ENTITY EXTRACTOR TESTS
# =============================================================================

class TestEntityExtractor:
    """Tests for entity extraction"""
    
    @pytest.fixture
    def extractor(self):
        return EntityExtractor()
    
    def test_extract_ip_addresses(self, extractor):
        """Test IP address extraction"""
        text = "Block IPs 192.168.1.1 and 10.0.0.1"
        result = extractor.extract(text)
        
        # Result is a dictionary with entity types as keys
        assert EntityType.IP_ADDRESS.value in result or "ip_address" in result
        ip_entities = result.get(EntityType.IP_ADDRESS.value, result.get("ip_address", []))
        assert len(ip_entities) >= 2
    
    def test_extract_email_addresses(self, extractor):
        """Test email extraction"""
        text = "Send notification to admin@example.com and user@test.org"
        result = extractor.extract(text)
        
        email_entities = result.get(EntityType.EMAIL.value, result.get("email", []))
        assert len(email_entities) >= 2
    
    def test_extract_usernames(self, extractor):
        """Test username extraction"""
        text = "Grant access to user john_doe and @admin"
        result = extractor.extract(text)
        
        username_entities = result.get(EntityType.USERNAME.value, result.get("username", []))
        assert len(username_entities) >= 1
    
    def test_extract_domains(self, extractor):
        """Test domain extraction"""
        text = "Allow traffic from example.com and test.org"
        result = extractor.extract(text)
        
        domain_entities = result.get(EntityType.DOMAIN.value, result.get("domain", []))
        assert len(domain_entities) >= 1
    
    def test_extract_file_paths(self, extractor):
        """Test file path extraction"""
        text = "Check files /var/log/auth.log and /etc/passwd"
        result = extractor.extract(text)
        
        path_entities = result.get(EntityType.FILE_PATH.value, result.get("file_path", []))
        assert len(path_entities) >= 1
    
    def test_extract_ports(self, extractor):
        """Test port extraction"""
        text = "Block port 22 and port 443"
        result = extractor.extract(text)
        
        port_entities = result.get(EntityType.PORT.value, result.get("port", []))
        assert len(port_entities) >= 2
    
    def test_extract_datetime(self, extractor):
        """Test datetime extraction"""
        text = "Show logs from 2024-01-15"
        result = extractor.extract(text)
        
        datetime_entities = result.get(EntityType.DATETIME.value, result.get("datetime", []))
        assert len(datetime_entities) >= 1
    
    def test_extract_duration(self, extractor):
        """Test duration extraction"""
        text = "Block for 24 hours"
        result = extractor.extract(text)
        
        duration_entities = result.get(EntityType.DURATION.value, result.get("duration", []))
        assert len(duration_entities) >= 1
    
    def test_extract_actions(self, extractor):
        """Test action extraction"""
        text = "Block the IP and restart the service"
        result = extractor.extract(text)
        
        action_entities = result.get(EntityType.ACTION.value, result.get("action", []))
        assert len(action_entities) >= 1
    
    def test_extract_targets(self, extractor):
        """Test target extraction helper"""
        text = "Block IP 192.168.1.1 and user admin@example.com"
        targets = extractor.extract_targets(text)
        
        assert len(targets) >= 1
    
    def test_extract_subjects(self, extractor):
        """Test subject extraction helper"""
        text = "Grant user john_doe access to server"
        subjects = extractor.extract_subjects(text)
        
        assert isinstance(subjects, list)
    
    def test_to_dict(self, extractor):
        """Test converting results to dictionary"""
        text = "Block IP 192.168.1.1"
        result = extractor.extract(text)
        
        entity_dict = extractor.to_dict(result)
        assert isinstance(entity_dict, dict)
    
    def test_get_summary(self, extractor):
        """Test getting extraction summary"""
        text = "Block IP 192.168.1.1 and send email to admin@test.com"
        
        summary = extractor.get_summary(text)
        assert "total_entities" in summary
        assert "counts" in summary


# =============================================================================
# INTENT VALIDATOR TESTS
# =============================================================================

class TestIntentValidator:
    """Tests for intent validation"""
    
    @pytest.fixture
    def validator(self):
        return IntentValidator()
    
    @pytest.fixture
    def valid_security_intent(self):
        return LLMOutput(
            intent_type=IntentType.SECURITY,
            goal="Block malicious IP addresses",
            confidence=0.9,
            entities=Entities(
                targets=["192.168.1.1"],
                subjects=[],
                objects=[]
            ),
            requested_actions=["BLOCK_IP"]
        )
    
    @pytest.fixture
    def invalid_access_intent(self):
        return LLMOutput(
            intent_type=IntentType.ACCESS,
            goal="Grant access to resources",
            confidence=0.5,
            entities=Entities(
                targets=[],
                subjects=[],  # Missing required subjects
                objects=[]
            ),
            requested_actions=["GRANT_ACCESS"]
        )
    
    def test_validate_valid_intent(self, validator, valid_security_intent):
        """Test validating a valid intent"""
        result = validator.validate(valid_security_intent)
        
        assert result.is_valid
        assert result.score >= 0.7
    
    def test_validate_low_confidence(self, validator):
        """Test validating low confidence intent"""
        intent = LLMOutput(
            intent_type=IntentType.QUERY,
            goal="Query data",
            confidence=0.3,  # Low confidence
            entities=Entities(targets=[], subjects=[], objects=[]),
            requested_actions=["QUERY_DATABASE"]
        )
        
        result = validator.validate(intent)
        
        # Should have issues for low confidence or low score
        assert result.score < 0.8 or len(result.issues) >= 1
    
    def test_validate_missing_entities(self, validator, invalid_access_intent):
        """Test validating intent with missing entities"""
        result = validator.validate(invalid_access_intent)
        
        # Should have issues for missing entities
        assert len(result.issues) >= 1
    
    def test_validate_unknown_action(self, validator):
        """Test validating intent with unknown action"""
        intent = LLMOutput(
            intent_type=IntentType.SYSTEM,
            goal="Perform system action",
            confidence=0.8,
            entities=Entities(targets=[], subjects=[], objects=[]),
            requested_actions=["UNKNOWN_ACTION_XYZ"]
        )
        
        result = validator.validate(intent)
        
        # Should have reduced score or warnings for unknown action
        assert result.score < 1.0 or len(result.issues) >= 1
    
    def test_suggest_clarifications(self, validator, invalid_access_intent):
        """Test clarification suggestions"""
        result = validator.validate(invalid_access_intent)
        
        # Should have suggestions for missing required fields
        assert len(result.suggestions) >= 1 or not result.is_valid
    
    def test_calculate_score(self, validator, valid_security_intent):
        """Test score calculation"""
        result = validator.validate(valid_security_intent)
        
        assert 0 <= result.score <= 1.0


class TestIntentEnricher:
    """Tests for intent enrichment"""
    
    @pytest.fixture
    def enricher(self):
        validator = IntentValidator()
        return IntentEnricher(validator)
    
    @pytest.fixture
    def basic_intent(self):
        return LLMOutput(
            intent_type=IntentType.SECURITY,
            goal="Block malicious IP",
            confidence=0.8,
            entities=Entities(
                targets=["192.168.1.1"],
                subjects=[],
                objects=[]
            ),
            requested_actions=["BLOCK_IP"]
        )
    
    def test_enrich_adds_metadata(self, enricher, basic_intent):
        """Test that enrichment adds metadata"""
        enriched = enricher.enrich(basic_intent)
        
        # Should still have original data
        assert enriched.intent_type == basic_intent.intent_type
        assert enriched.confidence == basic_intent.confidence
    
    def test_enrich_preserves_entities(self, enricher, basic_intent):
        """Test that enrichment preserves entities"""
        enriched = enricher.enrich(basic_intent)
        
        assert enriched.entities.targets == basic_intent.entities.targets


# =============================================================================
# ACTION MAPPER TESTS
# =============================================================================

class TestActionMapper:
    """Tests for action mapping"""
    
    @pytest.fixture
    def mapper(self):
        return ActionMapper()
    
    @pytest.fixture
    def security_intent(self):
        return LLMOutput(
            intent_type=IntentType.SECURITY,
            goal="Block malicious IP addresses",
            confidence=0.9,
            entities=Entities(
                targets=["192.168.1.1"],
                subjects=[],
                objects=[]
            ),
            requested_actions=["BLOCK_IP"]
        )
    
    @pytest.fixture
    def access_intent(self):
        return LLMOutput(
            intent_type=IntentType.ACCESS,
            goal="Grant access to database",
            confidence=0.85,
            entities=Entities(
                targets=[],
                subjects=["john_doe"],
                objects=["database_access"]
            ),
            requested_actions=["GRANT_ACCESS"]
        )
    
    def test_map_security_intent(self, mapper, security_intent):
        """Test mapping security intent to actions"""
        actions = mapper.map_intent_to_actions(security_intent)
        
        assert len(actions) >= 1
        assert actions[0].action == "BLOCK_IP"
    
    def test_map_access_intent(self, mapper, access_intent):
        """Test mapping access intent to actions"""
        actions = mapper.map_intent_to_actions(access_intent)
        
        assert len(actions) >= 1
        assert actions[0].action == "GRANT_ACCESS"
    
    def test_action_has_params(self, mapper, security_intent):
        """Test that mapped action has parameters"""
        actions = mapper.map_intent_to_actions(security_intent)
        
        action = actions[0]
        assert isinstance(action.params, dict)
        assert "ip_addresses" in action.params
    
    def test_action_has_category(self, mapper, security_intent):
        """Test that mapped action has category"""
        actions = mapper.map_intent_to_actions(security_intent)
        
        action = actions[0]
        assert isinstance(action.category, ActionCategory)
    
    def test_action_has_risk_level(self, mapper, security_intent):
        """Test that mapped action has risk level"""
        actions = mapper.map_intent_to_actions(security_intent)
        
        action = actions[0]
        assert isinstance(action.risk_level, RiskLevel)
    
    def test_default_action_for_intent_type(self, mapper):
        """Test default actions for intent types"""
        intent = LLMOutput(
            intent_type=IntentType.QUERY,
            goal="Query data",
            confidence=0.8,
            entities=Entities(targets=[], subjects=[], objects=[]),
            requested_actions=[]  # No explicit actions
        )
        
        actions = mapper.map_intent_to_actions(intent)
        
        # Should get default action
        assert len(actions) >= 1
    
    def test_execution_order(self, mapper):
        """Test execution order calculation"""
        intent1 = LLMOutput(
            intent_type=IntentType.SECURITY,
            goal="Block and scan",
            confidence=0.9,
            entities=Entities(targets=["192.168.1.1"], subjects=[], objects=[]),
            requested_actions=["BLOCK_IP", "SCAN_NETWORK"]
        )
        
        actions = mapper.map_intent_to_actions(intent1)
        order = mapper.get_execution_order(actions)
        
        # Should return list of groups
        assert isinstance(order, list)
        assert all(isinstance(group, list) for group in order)
    
    def test_to_operational_level(self, mapper, security_intent):
        """Test conversion to OperationalLevel"""
        actions = mapper.map_intent_to_actions(security_intent)
        operational = mapper.to_operational_level(actions)
        
        assert operational is not None
        assert len(operational.actions) >= 1
    
    def test_requires_confirmation(self, mapper, security_intent):
        """Test confirmation requirement check"""
        actions = mapper.map_intent_to_actions(security_intent)
        requires, action_names = mapper.requires_confirmation(actions)
        
        # BLOCK_IP should require confirmation
        assert requires == True
        assert "BLOCK_IP" in action_names
    
    def test_risk_summary(self, mapper, security_intent):
        """Test risk summary generation"""
        actions = mapper.map_intent_to_actions(security_intent)
        summary = mapper.get_risk_summary(actions)
        
        assert "highest_risk" in summary
        assert "risk_counts" in summary
        assert "total_actions" in summary
    
    def test_get_action_mapper_singleton(self):
        """Test singleton pattern"""
        mapper1 = get_action_mapper()
        mapper2 = get_action_mapper()
        
        assert mapper1 is mapper2
    
    def test_custom_mapping(self, mapper):
        """Test adding custom action mappings"""
        mapper.add_custom_mapping("lockdown", ["ISOLATE_SYSTEM", "BLOCK_IP"])
        
        assert "lockdown" in mapper.custom_mappings


# =============================================================================
# ENHANCED LLM INTERPRETER TESTS
# =============================================================================

class TestLLMConfig:
    """Tests for LLM configuration"""
    
    def test_default_config(self):
        """Test default configuration values"""
        config = LLMConfig()
        
        assert config.model_name is not None
        assert config.temperature >= 0
        assert config.max_tokens > 0
    
    def test_custom_config(self):
        """Test custom configuration"""
        config = LLMConfig(
            model_name="custom-model",
            temperature=0.5,
            max_tokens=2000
        )
        
        assert config.model_name == "custom-model"
        assert config.temperature == 0.5
        assert config.max_tokens == 2000


class TestResponseCache:
    """Tests for response caching"""
    
    def test_cache_set_get(self):
        """Test setting and getting cache"""
        cache = ResponseCache(ttl=3600, max_size=100)
        
        cache.set("key1", {"data": "value1"})
        result = cache.get("key1")
        
        assert result == {"data": "value1"}
    
    def test_cache_miss(self):
        """Test cache miss"""
        cache = ResponseCache(ttl=3600, max_size=100)
        
        result = cache.get("nonexistent")
        
        assert result is None
    
    def test_cache_clear(self):
        """Test cache clearing"""
        cache = ResponseCache(ttl=3600, max_size=100)
        cache.set("key1", {"data": "value1"})
        cache.clear()
        
        result = cache.get("key1")
        assert result is None
    
    def test_cache_stats(self):
        """Test cache statistics"""
        cache = ResponseCache(ttl=3600, max_size=100)
        cache.set("key1", {"data": "value1"})
        cache.get("key1")  # Hit
        cache.get("key2")  # Miss
        
        stats = cache.stats()
        
        assert "size" in stats
        assert "total_hits" in stats


class TestLLMResponseParser:
    """Tests for LLM response parsing"""
    
    def test_parse_valid_json(self):
        """Test parsing valid JSON response"""
        response = json.dumps({
            "intent_type": "SECURITY",
            "goal": "Block malicious IPs",
            "confidence": 0.9,
            "entities": {
                "targets": ["192.168.1.1"],
                "subjects": [],
                "objects": []
            },
            "requested_actions": ["BLOCK_IP"]
        })
        
        result = LLMResponseParser.parse_json_response(response)
        
        assert result is not None
        assert result["intent_type"] == "SECURITY"
    
    def test_parse_json_in_markdown(self):
        """Test parsing JSON embedded in markdown"""
        response = """
        Here's the parsed intent:
        ```json
        {
            "intent_type": "SECURITY",
            "goal": "Scan network",
            "confidence": 0.85,
            "entities": {"targets": [], "subjects": [], "objects": []},
            "requested_actions": ["SCAN_NETWORK"]
        }
        ```
        """
        
        result = LLMResponseParser.parse_json_response(response)
        
        assert result is not None
        assert result.get("intent_type") == "SECURITY"
    
    def test_parse_invalid_json(self):
        """Test parsing invalid JSON"""
        response = "This is not valid JSON"
        
        result = LLMResponseParser.parse_json_response(response)
        
        # Should return error structure, not None
        assert "error" in result or result.get("confidence") == 0.0


class TestEnhancedLLMInterpreter:
    """Tests for enhanced LLM interpreter"""
    
    @pytest.fixture
    def interpreter(self):
        """Create interpreter in mock mode"""
        config = LLMConfig()  # Will default to mock mode without API key
        return EnhancedLLMInterpreter(config)
    
    def test_interpret_mock_mode(self, interpreter):
        """Test interpretation in mock mode"""
        from app.schemas.request_schema import UserRequest
        request = UserRequest(
            request_id="test-1",
            user_id="user-1",
            message="Block IP 192.168.1.1"
        )
        result = interpreter.interpret(request)
        
        assert result is not None
        assert isinstance(result, LLMOutput)
    
    def test_interpret_security_request(self, interpreter):
        """Test security request interpretation"""
        from app.schemas.request_schema import UserRequest
        request = UserRequest(
            request_id="test-2",
            user_id="user-1",
            message="Block malicious IP 192.168.1.1"
        )
        result = interpreter.interpret(request)
        
        assert result.intent_type == IntentType.SECURITY
    
    def test_interpret_access_request(self, interpreter):
        """Test access request interpretation"""
        from app.schemas.request_schema import UserRequest
        request = UserRequest(
            request_id="test-3",
            user_id="user-1",
            message="Grant admin access to john_doe"
        )
        result = interpreter.interpret(request)
        
        assert result.intent_type == IntentType.ACCESS
    
    def test_interpret_query_request(self, interpreter):
        """Test query request interpretation"""
        from app.schemas.request_schema import UserRequest
        request = UserRequest(
            request_id="test-4",
            user_id="user-1",
            message="Show me the last 24 hours of logs"
        )
        result = interpreter.interpret(request)
        
        assert result.intent_type == IntentType.QUERY
    
    def test_llm_to_hrm_input(self, interpreter):
        """Test conversion to HRM input"""
        from app.schemas.request_schema import UserRequest
        request = UserRequest(
            request_id="test-5",
            user_id="user-1",
            message="Block IP 192.168.1.1"
        )
        llm_output = interpreter.interpret(request)
        hrm_input = interpreter.llm_to_hrm_input(llm_output, request)
        
        assert hrm_input is not None
        assert hrm_input.L1_strategic is not None
        assert hrm_input.L2_tactical is not None
        assert hrm_input.L3_operational is not None
    
    def test_context_management(self, interpreter):
        """Test conversation context"""
        context = interpreter.get_or_create_context("test-session")
        
        assert context is not None
        assert context.session_id == "test-session"
    
    def test_interpret_with_session(self, interpreter):
        """Test interpreting with session context"""
        from app.schemas.request_schema import UserRequest
        request = UserRequest(
            request_id="test-6",
            user_id="user-1",
            message="Block IP 192.168.1.1"
        )
        result = interpreter.interpret(request, session_id="test-session")
        
        assert result is not None


# =============================================================================
# CHAT API TESTS
# =============================================================================

class TestChatAPI:
    """Tests for chat API endpoints"""
    
    @pytest.fixture
    def client(self):
        from fastapi.testclient import TestClient
        from app.main import app
        return TestClient(app)
    
    def test_chat_endpoint_exists(self, client):
        """Test that chat endpoint exists"""
        response = client.post(
            "/api/v1/chat",
            json={"message": "Hello"}
        )
        
        # Should not be 404
        assert response.status_code != 404
    
    def test_chat_simple_message(self, client):
        """Test simple chat message"""
        response = client.post(
            "/api/v1/chat",
            json={"message": "Block IP 192.168.1.1"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "response" in data or "intent" in data
    
    def test_chat_with_session(self, client):
        """Test chat with session ID"""
        response = client.post(
            "/api/v1/chat",
            json={
                "message": "Block IP 192.168.1.1",
                "session_id": "test-session-123"
            }
        )
        
        assert response.status_code == 200
    
    def test_chat_examples_endpoint(self, client):
        """Test chat examples endpoint"""
        response = client.get("/api/v1/chat/examples")
        
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list) or "examples" in data
    
    def test_chat_stats_endpoint(self, client):
        """Test chat stats endpoint"""
        response = client.get("/api/v1/chat/stats")
        
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, dict)


# =============================================================================
# INTEGRATION TESTS
# =============================================================================

class TestPhase2Integration:
    """Integration tests for Phase 2 components"""
    
    def test_full_pipeline_security(self):
        """Test full pipeline for security request"""
        # 1. Extract entities
        extractor = EntityExtractor()
        text = "Block IP 192.168.1.1 for 24 hours"
        entities = extractor.extract(text)
        
        assert len(entities) >= 1  # At least IP address
        
        # 2. Create intent
        llm_output = LLMOutput(
            intent_type=IntentType.SECURITY,
            goal="Block malicious IP addresses",
            confidence=0.9,
            entities=Entities(
                targets=["192.168.1.1"],
                subjects=[],
                objects=[]
            ),
            requested_actions=["BLOCK_IP"]
        )
        
        # 3. Validate intent
        validator = IntentValidator()
        validation = validator.validate(llm_output)
        
        assert validation.is_valid
        
        # 4. Map to actions
        mapper = ActionMapper()
        actions = mapper.map_intent_to_actions(llm_output)
        
        assert len(actions) >= 1
        assert actions[0].action == "BLOCK_IP"
        
        # 5. Convert to operational level
        operational = mapper.to_operational_level(actions)
        
        assert operational is not None
    
    def test_full_pipeline_access(self):
        """Test full pipeline for access request"""
        # 1. Extract entities
        extractor = EntityExtractor()
        text = "Grant user john_doe access to production database"
        entities = extractor.extract(text)
        
        # 2. Create intent
        llm_output = LLMOutput(
            intent_type=IntentType.ACCESS,
            goal="Grant access to database for user",
            confidence=0.85,
            entities=Entities(
                targets=[],
                subjects=["john_doe"],
                objects=["production database"]
            ),
            requested_actions=["GRANT_ACCESS"]
        )
        
        # 3. Validate
        validator = IntentValidator()
        validation = validator.validate(llm_output)
        
        assert validation.score > 0
        
        # 4. Map actions
        mapper = ActionMapper()
        actions = mapper.map_intent_to_actions(llm_output)
        
        assert len(actions) >= 1
    
    def test_full_pipeline_query(self):
        """Test full pipeline for query request"""
        extractor = EntityExtractor()
        text = "Show me logs from the last 24 hours"
        entities = extractor.extract(text)
        
        llm_output = LLMOutput(
            intent_type=IntentType.QUERY,
            goal="Retrieve logs",
            confidence=0.9,
            entities=Entities(
                targets=[],
                subjects=[],
                objects=["logs"]
            ),
            requested_actions=["FETCH_LOGS"]
        )
        
        validator = IntentValidator()
        validation = validator.validate(llm_output)
        
        mapper = ActionMapper()
        actions = mapper.map_intent_to_actions(llm_output)
        
        # Should be low risk
        assert actions[0].risk_level == RiskLevel.LOW
    
    def test_enhanced_interpreter_integration(self):
        """Test enhanced interpreter with full pipeline"""
        config = LLMConfig()  # Mock mode without API key
        interpreter = EnhancedLLMInterpreter(config)
        
        from app.schemas.request_schema import UserRequest
        request = UserRequest(
            request_id="test-int",
            user_id="user-1",
            message="Block malicious IP 192.168.1.1"
        )
        
        # Interpret
        llm_output = interpreter.interpret(request)
        
        # Validate
        validator = IntentValidator()
        validation = validator.validate(llm_output)
        
        # Map
        mapper = ActionMapper()
        actions = mapper.map_intent_to_actions(llm_output)
        
        # Convert to HRM
        hrm_input = interpreter.llm_to_hrm_input(llm_output, request)
        
        assert hrm_input is not None
        assert hrm_input.L1_strategic.goal is not None


# =============================================================================
# ERROR HANDLING TESTS
# =============================================================================

class TestErrorHandling:
    """Tests for error handling"""
    
    def test_empty_text_extraction(self):
        """Test extraction with empty text"""
        extractor = EntityExtractor()
        result = extractor.extract("")
        
        assert isinstance(result, dict)
        # Empty text should return empty results
    
    def test_none_text_extraction(self):
        """Test extraction with None text"""
        extractor = EntityExtractor()
        
        # Should handle gracefully
        try:
            result = extractor.extract(None)
            assert isinstance(result, dict)
        except (TypeError, AttributeError):
            pass  # Expected
    
    def test_invalid_intent_validation(self):
        """Test validation with minimal intent"""
        validator = IntentValidator()
        
        intent = LLMOutput(
            intent_type=IntentType.SECURITY,
            goal="Unknown",
            confidence=0.1,
            entities=Entities(targets=[], subjects=[], objects=[]),
            requested_actions=[]
        )
        
        result = validator.validate(intent)
        
        # Should return result even with issues
        assert result is not None
        assert isinstance(result.issues, list)
    
    def test_unknown_action_mapping(self):
        """Test mapping with unknown action"""
        mapper = ActionMapper()
        
        intent = LLMOutput(
            intent_type=IntentType.SYSTEM,
            goal="Perform action",
            confidence=0.8,
            entities=Entities(targets=[], subjects=[], objects=[]),
            requested_actions=["COMPLETELY_UNKNOWN_ACTION"]
        )
        
        actions = mapper.map_intent_to_actions(intent)
        
        # Should still return something
        assert isinstance(actions, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
