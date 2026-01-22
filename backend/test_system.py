"""
Test Script for HRM Decision System

Quick test to verify all components are working correctly.
Run this to test the complete pipeline without starting the API server.
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.schemas.request_schema import UserRequest, RequestContext
from app.core.preprocessor import NLPPreprocessor
from app.core.llm_interpreter import LLMInterpreter
from app.core.hrm_engine import HRMEngine
from app.core.action_executor import ActionExecutor
from datetime import datetime
import json


def print_section(title: str):
    """Print a section header"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60 + "\n")


def test_complete_pipeline():
    """Test the complete decision pipeline"""
    
    print_section("HRM DECISION SYSTEM - PIPELINE TEST")
    
    # Initialize components
    print("Initializing components...")
    preprocessor = NLPPreprocessor()
    llm_interpreter = LLMInterpreter()
    hrm_engine = HRMEngine(use_simulation=True)
    action_executor = ActionExecutor(dry_run=True)
    print("✓ All components initialized\n")
    
    # Create test request
    print_section("STEP 1: USER REQUEST")
    
    user_request = UserRequest(
        user_id="test-admin",
        message="Block all suspicious IP addresses from the last 24 hours",
        context=RequestContext(
            session_id="test-session-001",
            user_role="security_admin",
            user_permissions=["read", "write", "execute"]
        )
    )
    
    print(f"User: {user_request.user_id}")
    print(f"Role: {user_request.context.user_role}")
    print(f"Message: \"{user_request.message}\"")
    
    # Step 1: Preprocess
    print_section("STEP 2: PREPROCESSING")
    
    preprocessed = preprocessor.preprocess(user_request.message)
    print(f"Original: {user_request.message}")
    print(f"Normalized: {preprocessed.get('normalized_text', 'N/A')}")
    print(f"Tags: {preprocessed.get('tags', [])}")
    print(f"Keywords: {preprocessed.get('keywords', [])}")
    
    # Step 2: LLM Interpretation
    print_section("STEP 3: LLM INTERPRETATION")
    
    llm_output = llm_interpreter.interpret(user_request, preprocessed)
    print(f"Intent Type: {llm_output.intent_type.value}")
    print(f"Goal: {llm_output.goal}")
    print(f"Confidence: {llm_output.confidence:.2f}")
    print(f"Actions: {', '.join(llm_output.requested_actions)}")
    print(f"Reasoning: {llm_output.reasoning}")
    
    # Step 3: Convert to HRM Input
    print_section("STEP 4: HRM INPUT GENERATION")
    
    hrm_input = llm_interpreter.llm_to_hrm_input(llm_output, user_request)
    
    print("L1 STRATEGIC LEVEL:")
    print(f"  Goal: {hrm_input.L1_strategic.goal}")
    print(f"  Risk Level: {hrm_input.L1_strategic.risk_level.value}")
    print(f"  Priority: {hrm_input.L1_strategic.priority}/10")
    print(f"  Authorization Required: {hrm_input.L1_strategic.authorization_required}")
    
    print("\nL2 TACTICAL LEVEL:")
    print(f"  Strategy: {hrm_input.L2_tactical.strategy}")
    print(f"  Policy: {hrm_input.L2_tactical.policy}")
    print(f"  Subsystem: {hrm_input.L2_tactical.subsystem}")
    
    print("\nL3 OPERATIONAL LEVEL:")
    print(f"  Actions: {len(hrm_input.L3_operational.actions)}")
    for i, action in enumerate(hrm_input.L3_operational.actions, 1):
        print(f"    {i}. {action.action}")
        print(f"       Params: {action.params}")
    
    # Step 4: HRM Reasoning
    print_section("STEP 5: HRM REASONING")
    
    decision = hrm_engine.process(hrm_input, user_request.request_id)
    
    print(f"Decision ID: {decision.decision_id}")
    print(f"Status: {decision.status.value}")
    print(f"Summary: {decision.summary}")
    print(f"Confidence: {decision.confidence:.2f}")
    print(f"\nActions Completed: {len(decision.actions_completed)}")
    
    for action in decision.actions_completed:
        print(f"  - {action.action}: {action.status}")
    
    # Step 5: Execute Actions
    print_section("STEP 6: ACTION EXECUTION")
    
    final_decision = action_executor.execute_decision(decision, user_request.user_id)
    
    print(f"Final Status: {final_decision.status.value}")
    print(f"\nExecution Results:")
    for action in final_decision.actions_completed:
        print(f"  - {action.action}: {action.status}")
        if action.result:
            msg = action.result.get('message', 'N/A')
            print(f"    {msg}")
    
    # Show audit logs
    print_section("STEP 7: AUDIT TRAIL")
    
    audit_logs = action_executor.get_audit_logs(user_request.request_id)
    print(f"Total Audit Logs: {len(audit_logs)}")
    
    for log in audit_logs:
        print(f"\n  [{log.timestamp.strftime('%H:%M:%S')}] {log.event_type}")
        print(f"    Actor: {log.actor}")
        print(f"    Action: {log.action}")
        print(f"    Outcome: {log.outcome}")
    
    # Show complete decision explanation
    print_section("FINAL DECISION EXPLANATION")
    print(final_decision.explanation)
    
    # Show audit trail
    print_section("COMPLETE AUDIT TRAIL (JSON)")
    print(json.dumps(final_decision.audit_trail, indent=2, default=str))
    
    print_section("TEST COMPLETED SUCCESSFULLY! ✓")
    
    return final_decision


def test_multiple_scenarios():
    """Test multiple request scenarios"""
    
    print_section("TESTING MULTIPLE SCENARIOS")
    
    scenarios = [
        {
            "name": "Security: Block IPs",
            "message": "Block all suspicious IP addresses from the last 24 hours",
            "user_role": "security_admin"
        },
        {
            "name": "Access: Grant Permissions",
            "message": "Grant user john.doe access to the analytics dashboard",
            "user_role": "manager"
        },
        {
            "name": "Query: Fetch Logs",
            "message": "Show me all login attempts from yesterday",
            "user_role": "analyst"
        },
        {
            "name": "Compliance: Audit Report",
            "message": "Generate an audit report for the last month",
            "user_role": "compliance_officer"
        }
    ]
    
    llm = LLMInterpreter()
    hrm = HRMEngine(use_simulation=True)
    
    results = []
    
    for scenario in scenarios:
        print(f"\nScenario: {scenario['name']}")
        print(f"Message: \"{scenario['message']}\"")
        
        request = UserRequest(
            user_id="test-user",
            message=scenario['message'],
            context=RequestContext(user_role=scenario['user_role'])
        )
        
        # Quick pipeline
        llm_output = llm.interpret(request, None)
        hrm_input = llm.llm_to_hrm_input(llm_output, request)
        decision = hrm.process(hrm_input, request.request_id)
        
        print(f"  Intent: {llm_output.intent_type.value}")
        print(f"  Status: {decision.status.value}")
        print(f"  Actions: {len(decision.actions_completed)}")
        
        results.append({
            "scenario": scenario['name'],
            "intent": llm_output.intent_type.value,
            "status": decision.status.value
        })
    
    print_section("SCENARIO TEST RESULTS")
    for result in results:
        print(f"✓ {result['scenario']}")
        print(f"    Intent: {result['intent']}, Status: {result['status']}")
    
    print("\n✓ All scenarios tested successfully!")


if __name__ == "__main__":
    try:
        # Run complete pipeline test
        test_complete_pipeline()
        
        # Test multiple scenarios
        test_multiple_scenarios()
        
        print("\n" + "="*60)
        print("  ALL TESTS PASSED! ✓")
        print("="*60)
        print("\nYou can now start the API server with:")
        print("  python -m app.main")
        print("\nOr:")
        print("  uvicorn app.main:app --reload")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
