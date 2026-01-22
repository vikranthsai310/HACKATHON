import requests
import json

BASE = 'http://localhost:8000/api/v1/decision/quick'

tests = [
    # HR Scenarios
    'Approve vacation request for 5 days',
    'Hire a new software developer named John Smith',
    'Terminate employee access for security violation',
    'Update employee salary by 10 percent',
    
    # System Operations
    'Send email to team about project deadline',
    'Delete old backup files from server',
    'Restart the database server',
    'Deploy new version of the application',
    
    # Security Scenarios
    'Block suspicious IP address 192.168.1.100',
    'Investigate security breach in the network',
    'Update firewall rules to block port 445',
    
    # Query & Reports
    'Show system status and health check',
    'Generate quarterly compliance report',
    'Check audit logs for last 24 hours',
]

print("\n" + "="*70)
print("🧪 HRM COMPREHENSIVE SCENARIO TESTS")
print("="*70)

for i, t in enumerate(tests, 1):
    print(f'\n📥 TEST {i}: "{t}"')
    print('-' * 70)
    try:
        r = requests.post(BASE, json={'message': t})
        d = r.json()
        
        l1 = d.get('audit_trail', {}).get('L1_strategic', {})
        l2 = d.get('audit_trail', {}).get('L2_tactical', {})
        l3 = d.get('audit_trail', {}).get('L3_operational', {})
        
        # Get first action result for details
        actions = d.get('actions_completed', [])
        action_detail = ""
        if actions and len(actions) > 0:
            first_result = actions[0].get('result', {})
            action_detail = first_result.get('message', '')[:50]
        
        print(f'✅ Status: {d.get("status")}')
        print(f'🎯 Goal: {l1.get("goal")}')
        print(f'⚠️  Risk: {l1.get("risk_level")}')
        print(f'📊 Strategy: {l2.get("strategy")}')
        print(f'🔧 Actions: {l3.get("actions", [])}')
        print(f'💯 Confidence: {d.get("confidence")}')
        if action_detail:
            print(f'📝 Detail: {action_detail}')
    except Exception as e:
        print(f'❌ Error: {e}')

print("\n" + "="*70)
print("✅ ALL TESTS COMPLETE")
print("="*70)
