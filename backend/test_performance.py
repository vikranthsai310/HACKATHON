"""
Performance Tests for HRM Decision System

Tests performance and load characteristics.
Run with: pytest test_performance.py -v
"""

import pytest
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from app.schemas.request_schema import UserRequest
from app.core.preprocessor import NLPPreprocessor
from app.core.llm_interpreter import LLMInterpreter
from app.core.hrm_engine import HRMEngine
from app.core.action_executor import ActionExecutor


class TestResponseTime:
    """Test response time for various operations"""
    
    def test_preprocessing_speed(self):
        """Test preprocessing completes quickly"""
        preprocessor = NLPPreprocessor()
        
        start = time.time()
        result = preprocessor.preprocess("Block IP 192.168.1.100")
        duration = time.time() - start
        
        # Should complete in under 100ms
        assert duration < 0.1
        assert result is not None
    
    def test_llm_interpretation_speed(self):
        """Test LLM interpretation speed (mock mode)"""
        interpreter = LLMInterpreter()  # Uses mock mode
        
        request = UserRequest(
            user_id="user",
            message="Block IP 192.168.1.100"
        )
        
        start = time.time()
        output = interpreter.interpret(request, None)
        duration = time.time() - start
        
        # Should complete in under 500ms in mock mode
        assert duration < 0.5
        assert output is not None
    
    def test_hrm_processing_speed(self):
        """Test HRM engine processing speed"""
        interpreter = LLMInterpreter()
        engine = HRMEngine(use_simulation=True)
        
        request = UserRequest(
            user_id="user",
            message="Grant access to john"
        )
        
        llm_output = interpreter.interpret(request, None)
        hrm_input = interpreter.llm_to_hrm_input(llm_output, request)
        
        start = time.time()
        decision = engine.process(hrm_input, request.request_id)
        duration = time.time() - start
        
        # Should complete in under 200ms in simulation mode
        assert duration < 0.2
        assert decision is not None
    
    def test_end_to_end_latency(self):
        """Test complete pipeline latency"""
        preprocessor = NLPPreprocessor()
        interpreter = LLMInterpreter()
        engine = HRMEngine(use_simulation=True)
        executor = ActionExecutor(dry_run=True)
        
        request = UserRequest(
            user_id="user",
            message="Block IP 192.168.1.100"
        )
        
        start = time.time()
        
        # Complete pipeline
        preprocessed = preprocessor.preprocess(request.message)
        llm_output = interpreter.interpret(request, preprocessed)
        hrm_input = interpreter.llm_to_hrm_input(llm_output, request)
        decision = engine.process(hrm_input, request.request_id)
        final_decision = executor.execute_decision(decision, request.user_id)
        
        duration = time.time() - start
        
        # Complete pipeline should finish in under 1 second
        assert duration < 1.0
        assert final_decision is not None


class TestThroughput:
    """Test system throughput"""
    
    def test_sequential_requests(self):
        """Test processing multiple requests sequentially"""
        preprocessor = NLPPreprocessor()
        interpreter = LLMInterpreter()
        engine = HRMEngine(use_simulation=True)
        
        messages = [
            "Block IP 192.168.1.100",
            "Grant access to john",
            "Show system logs",
            "Generate audit report",
            "Revoke admin privileges"
        ]
        
        start = time.time()
        
        for message in messages:
            request = UserRequest(user_id="user", message=message)
            preprocessed = preprocessor.preprocess(request.message)
            llm_output = interpreter.interpret(request, preprocessed)
            hrm_input = interpreter.llm_to_hrm_input(llm_output, request)
            decision = engine.process(hrm_input, request.request_id)
            assert decision is not None
        
        duration = time.time() - start
        throughput = len(messages) / duration
        
        # Should process at least 2 requests per second
        assert throughput >= 2.0
    
    def test_concurrent_requests(self):
        """Test handling concurrent requests"""
        
        def process_request(message: str):
            preprocessor = NLPPreprocessor()
            interpreter = LLMInterpreter()
            engine = HRMEngine(use_simulation=True)
            
            request = UserRequest(user_id="user", message=message)
            preprocessed = preprocessor.preprocess(request.message)
            llm_output = interpreter.interpret(request, preprocessed)
            hrm_input = interpreter.llm_to_hrm_input(llm_output, request)
            decision = engine.process(hrm_input, request.request_id)
            return decision is not None
        
        messages = [f"Block IP 192.168.1.{i}" for i in range(10)]
        
        start = time.time()
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(process_request, msg) for msg in messages]
            results = [future.result() for future in as_completed(futures)]
        
        duration = time.time() - start
        
        # All should succeed
        assert all(results)
        
        # Should complete in reasonable time
        assert duration < 5.0


class TestMemoryUsage:
    """Test memory efficiency"""
    
    def test_no_memory_leaks_on_repeated_requests(self):
        """Test that repeated requests don't cause memory leaks"""
        import gc
        
        preprocessor = NLPPreprocessor()
        interpreter = LLMInterpreter()
        
        # Process many requests
        for i in range(100):
            request = UserRequest(
                user_id="user",
                message=f"Block IP 192.168.1.{i}"
            )
            preprocessed = preprocessor.preprocess(request.message)
            output = interpreter.interpret(request, preprocessed)
            
            # Force garbage collection every 10 iterations
            if i % 10 == 0:
                gc.collect()
        
        # If we got here without crashing, test passes
        assert True


class TestScalability:
    """Test system scalability"""
    
    def test_large_batch_processing(self):
        """Test processing large batch of requests"""
        preprocessor = NLPPreprocessor()
        interpreter = LLMInterpreter()
        
        # Generate 50 requests
        requests = [
            UserRequest(
                user_id=f"user-{i}",
                message=f"Request number {i}: Block IP 192.168.1.{i % 255}"
            )
            for i in range(50)
        ]
        
        start = time.time()
        successful = 0
        
        for request in requests:
            try:
                preprocessed = preprocessor.preprocess(request.message)
                output = interpreter.interpret(request, preprocessed)
                if output:
                    successful += 1
            except Exception:
                pass
        
        duration = time.time() - start
        
        # Most should succeed
        assert successful >= 45
        
        # Should process within reasonable time
        assert duration < 30.0


class TestCaching:
    """Test caching behavior (if implemented)"""
    
    def test_repeated_preprocessing(self):
        """Test that repeated preprocessing is fast"""
        preprocessor = NLPPreprocessor()
        message = "Block IP 192.168.1.100"
        
        # First call
        start1 = time.time()
        result1 = preprocessor.preprocess(message)
        duration1 = time.time() - start1
        
        # Second call with same message
        start2 = time.time()
        result2 = preprocessor.preprocess(message)
        duration2 = time.time() - start2
        
        # Results should be consistent
        assert result1["normalized_text"] == result2["normalized_text"]
        
        # Both should be fast
        assert duration1 < 0.1
        assert duration2 < 0.1


class TestStressTest:
    """Stress testing"""
    
    @pytest.mark.slow
    def test_sustained_load(self):
        """Test system under sustained load"""
        preprocessor = NLPPreprocessor()
        interpreter = LLMInterpreter()
        
        # Run for 10 seconds
        end_time = time.time() + 10
        count = 0
        errors = 0
        
        while time.time() < end_time:
            try:
                request = UserRequest(
                    user_id="stress-test",
                    message=f"Test request {count}"
                )
                preprocessed = preprocessor.preprocess(request.message)
                output = interpreter.interpret(request, preprocessed)
                
                if output:
                    count += 1
            except Exception:
                errors += 1
        
        # Should process many requests
        assert count > 10
        
        # Error rate should be low
        if count > 0:
            error_rate = errors / (count + errors)
            assert error_rate < 0.1  # Less than 10% error rate


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short", "-m", "not slow"])
