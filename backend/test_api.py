"""
API Integration Tests for HRM Decision System

Tests actual API endpoints using FastAPI TestClient.
Run with: pytest test_api.py -v
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

# Create test client
client = TestClient(app)


class TestHealthEndpoints:
    """Test health and status endpoints"""
    
    def test_root_endpoint(self):
        """Test root endpoint returns correct info"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert data["status"] == "running"
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "components" in data


class TestDecisionEndpoint:
    """Test main decision endpoint"""
    
    def test_decision_endpoint_valid_request(self):
        """Test decision endpoint with valid request"""
        request_data = {
            "user_id": "test-user",
            "message": "Block IP 192.168.1.100"
        }
        
        response = client.post("/api/v1/decision", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "decision_id" in data
        assert "status" in data
        assert "summary" in data
        assert "actions_completed" in data
        assert "explanation" in data
    
    def test_decision_endpoint_security_request(self):
        """Test security-related decision"""
        request_data = {
            "user_id": "admin",
            "message": "Block all suspicious IP addresses from the last 24 hours",
            "context": {
                "user_role": "security_admin"
            }
        }
        
        response = client.post("/api/v1/decision", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] in ["SUCCESS", "DENIED", "PARTIAL", "PENDING"]
    
    def test_decision_endpoint_access_request(self):
        """Test access management decision"""
        request_data = {
            "user_id": "manager",
            "message": "Grant user john.doe access to analytics dashboard"
        }
        
        response = client.post("/api/v1/decision", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "decision_id" in data
        assert len(data["actions_completed"]) > 0
    
    def test_decision_endpoint_query_request(self):
        """Test query/information request"""
        request_data = {
            "user_id": "analyst",
            "message": "Show me all login attempts from yesterday"
        }
        
        response = client.post("/api/v1/decision", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "explanation" in data
    
    def test_decision_endpoint_missing_fields(self):
        """Test decision endpoint with missing required fields"""
        request_data = {
            "user_id": "test-user"
            # Missing 'message' field
        }
        
        response = client.post("/api/v1/decision", json=request_data)
        assert response.status_code == 422  # Validation error


class TestComponentEndpoints:
    """Test individual component endpoints"""
    
    def test_preprocess_endpoint(self):
        """Test preprocessing endpoint"""
        response = client.post(
            "/api/v1/preprocess",
            params={"message": "Block suspicious activity from yesterday"}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "original" in data
        assert "preprocessed" in data
    
    def test_interpret_endpoint(self):
        """Test LLM interpretation endpoint"""
        request_data = {
            "user_id": "test-user",
            "message": "Block IP 192.168.1.100"
        }
        
        response = client.post("/api/v1/interpret", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "intent_type" in data
        assert "goal" in data
        assert "confidence" in data
        assert 0 <= data["confidence"] <= 1
    
    def test_hrm_input_endpoint(self):
        """Test HRM input generation endpoint"""
        request_data = {
            "user_id": "test-user",
            "message": "Grant access to user john"
        }
        
        response = client.post("/api/v1/hrm-input", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "L1_strategic" in data
        assert "L2_tactical" in data
        assert "L3_operational" in data
        
        # Verify structure
        assert "goal" in data["L1_strategic"]
        assert "risk_level" in data["L1_strategic"]
        assert "strategy" in data["L2_tactical"]
        assert "actions" in data["L3_operational"]


class TestAuditEndpoints:
    """Test audit and monitoring endpoints"""
    
    def test_get_audit_logs(self):
        """Test retrieving audit logs"""
        response = client.get("/api/v1/audit-logs")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_audit_logs_filtered(self):
        """Test retrieving audit logs filtered by request_id"""
        # First make a decision to create logs
        request_data = {
            "user_id": "test-user",
            "message": "Test action"
        }
        decision_response = client.post("/api/v1/decision", json=request_data)
        request_id = decision_response.json().get("request_id")
        
        # Get logs for that request
        response = client.get(f"/api/v1/audit-logs?request_id={request_id}")
        assert response.status_code == 200


class TestConfigurationEndpoints:
    """Test configuration endpoints"""
    
    def test_get_executor_mode(self):
        """Test getting executor mode"""
        response = client.get("/api/v1/config/executor-mode")
        assert response.status_code == 200
        
        data = response.json()
        assert "dry_run" in data
        assert "mode" in data
        assert data["mode"] in ["DRY-RUN", "LIVE"]
    
    def test_set_executor_mode(self):
        """Test setting executor mode"""
        response = client.post("/api/v1/config/executor-mode?dry_run=true")
        assert response.status_code == 200
        
        data = response.json()
        assert data["dry_run"] is True
        assert data["mode"] == "DRY-RUN"
    
    def test_get_hrm_mode(self):
        """Test getting HRM mode"""
        response = client.get("/api/v1/config/hrm-mode")
        assert response.status_code == 200
        
        data = response.json()
        assert "simulation" in data
        assert "mode" in data
    
    def test_get_llm_mode(self):
        """Test getting LLM mode"""
        response = client.get("/api/v1/config/llm-mode")
        assert response.status_code == 200
        
        data = response.json()
        assert "mock" in data
        assert "mode" in data


class TestExamplesEndpoint:
    """Test examples endpoint"""
    
    def test_get_examples(self):
        """Test getting example requests"""
        response = client.get("/api/v1/examples")
        assert response.status_code == 200
        
        data = response.json()
        assert "examples" in data
        assert len(data["examples"]) > 0
        
        # Verify example structure
        example = data["examples"][0]
        assert "name" in example
        assert "request" in example


class TestErrorHandling:
    """Test error handling"""
    
    def test_invalid_endpoint(self):
        """Test accessing non-existent endpoint"""
        response = client.get("/api/v1/nonexistent")
        assert response.status_code == 404
    
    def test_invalid_method(self):
        """Test using wrong HTTP method"""
        response = client.get("/api/v1/decision")  # Should be POST
        assert response.status_code == 405
    
    def test_malformed_json(self):
        """Test sending malformed JSON"""
        response = client.post(
            "/api/v1/decision",
            data="not valid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422


class TestCORS:
    """Test CORS configuration"""
    
    def test_cors_headers(self):
        """Test CORS headers are present"""
        response = client.options("/api/v1/decision")
        # CORS headers should be present
        # Note: TestClient might not fully simulate CORS


class TestEndToEnd:
    """End-to-end API workflow tests"""
    
    def test_complete_workflow(self):
        """Test complete decision workflow through API"""
        
        # Step 1: Make a decision request
        request_data = {
            "user_id": "workflow-test-user",
            "message": "Block IP 10.0.0.1"
        }
        
        decision_response = client.post("/api/v1/decision", json=request_data)
        assert decision_response.status_code == 200
        
        decision = decision_response.json()
        assert "request_id" in decision
        assert "decision_id" in decision
        
        # Step 2: Check audit logs for this request
        request_id = decision["request_id"]
        logs_response = client.get(f"/api/v1/audit-logs?request_id={request_id}")
        assert logs_response.status_code == 200
        
        # Step 3: Verify we can still get configuration
        config_response = client.get("/api/v1/config/executor-mode")
        assert config_response.status_code == 200


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
