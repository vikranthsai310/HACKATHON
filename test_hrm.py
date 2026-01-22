"""
Test script for HRM Decision System
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def print_result(title, response):
    print("\n" + "="*60)
    print(f"TEST: {title}")
    print("="*60)
    print(f"Status: {response.status_code}")
    try:
        data = response.json()
        print(json.dumps(data, indent=2, default=str))
    except:
        print(response.text)
    print()

# Test 1: Health Check
print("\n🏥 Checking API Health...")
try:
    r = requests.get(f"{BASE_URL.replace('/api/v1', '')}/health")
    print_result("Health Check", r)
except Exception as e:
    print(f"Error: {e}")

# Test 2: Budget Approval Request
print("\n💰 Test: Budget Approval Request")
try:
    r = requests.post(f"{BASE_URL}/decision/quick", json={
        "message": "I need to approve a $50000 budget request for new office equipment from marketing"
    })
    print_result("Budget Approval", r)
except Exception as e:
    print(f"Error: {e}")

# Test 3: Employee Termination (High Risk)
print("\n👤 Test: Employee Termination Request (High Risk)")
try:
    r = requests.post(f"{BASE_URL}/decision/quick", json={
        "message": "Terminate employee John Smith from engineering department for performance issues"
    })
    print_result("Employee Termination", r)
except Exception as e:
    print(f"Error: {e}")

# Test 4: Schedule Meeting (Low Risk)
print("\n📅 Test: Schedule Meeting Request (Low Risk)")
try:
    r = requests.post(f"{BASE_URL}/decision/quick", json={
        "message": "Schedule a team meeting for next Monday at 10 AM"
    })
    print_result("Schedule Meeting", r)
except Exception as e:
    print(f"Error: {e}")

# Test 5: Full Decision Pipeline
print("\n🔄 Test: Full Decision Pipeline")
try:
    r = requests.post(f"{BASE_URL}/decision/process", json={
        "message": "Create a new project called AI Integration with budget of $100000 and assign 5 engineers",
        "context": {
            "user_role": "manager",
            "department": "technology"
        }
    })
    print_result("Full Decision Pipeline", r)
except Exception as e:
    print(f"Error: {e}")

# Test 6: Chat Message
print("\n💬 Test: Chat Message")
try:
    r = requests.post(f"{BASE_URL}/chat", json={
        "message": "What can you help me with?",
        "session_id": "test-session-001"
    })
    print_result("Chat Message", r)
except Exception as e:
    print(f"Error: {e}")

# Test 7: System Query
print("\n❓ Test: System Query")
try:
    r = requests.post(f"{BASE_URL}/decision/quick", json={
        "message": "What is the status of pending approvals in the finance department?"
    })
    print_result("System Query", r)
except Exception as e:
    print(f"Error: {e}")

# Test 8: Generate Report
print("\n📊 Test: Generate Report")
try:
    r = requests.post(f"{BASE_URL}/decision/quick", json={
        "message": "Generate a quarterly sales report for Q4 2025"
    })
    print_result("Generate Report", r)
except Exception as e:
    print(f"Error: {e}")

print("\n" + "="*60)
print("✅ ALL TESTS COMPLETED")
print("="*60)
