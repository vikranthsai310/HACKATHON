import requests
import json

BASE = 'http://localhost:8000/api/v1/decision/quick'

# New unique test scenarios
new_tests = [
    'Grant admin access to user Alice for the production database',
    'Schedule emergency maintenance for tonight at 2 AM',
    'Revoke all permissions for contractor Bob immediately',
    'Create backup of all customer data before migration',
    'Scan network for potential vulnerabilities',
    'Approve budget of 25000 dollars for marketing campaign',
]

print('\n' + '='*70)
print('🧪 NEW TEST SCENARIOS - RUN 1')
print('='*70)

run1_results = []
for i, t in enumerate(new_tests, 1):
    r = requests.post(BASE, json={'message': t})
    d = r.json()
    l1 = d.get('audit_trail', {}).get('L1_strategic', {})
    l2 = d.get('audit_trail', {}).get('L2_tactical', {})
    l3 = d.get('audit_trail', {}).get('L3_operational', {})
    
    # Store result
    run1_results.append(d.get('confidence'))
    
    # Get action details
    actions = d.get('actions_completed', [])
    details = []
    for act in actions[:2]:  # First 2 actions
        result = act.get('result', {})
        msg = result.get('message', '')[:40]
        if msg:
            details.append(msg)
    
    print(f'\n{i}. "{t}"')
    print(f'   🎯 Goal: {l1.get("goal")}')
    print(f'   ⚠️  Risk: {l1.get("risk_level")} | 💯 Confidence: {d.get("confidence")}')
    print(f'   📊 Strategy: {l2.get("strategy")}')
    print(f'   🔧 Actions: {l3.get("actions", [])}')
    if details:
        print(f'   📝 Details: {details[0]}')

print('\n' + '='*70)
print('🔄 RUNNING SAME TESTS AGAIN - RUN 2 (checking for variance)')
print('='*70)

run2_results = []
for i, t in enumerate(new_tests, 1):
    r = requests.post(BASE, json={'message': t})
    d = r.json()
    run2_results.append(d.get('confidence'))
    print(f'{i}. Confidence: {d.get("confidence")} | Status: {d.get("status")}')

print('\n' + '='*70)
print('📊 COMPARISON: RUN 1 vs RUN 2')
print('='*70)
print(f'{"Test":<6} {"Run 1":<10} {"Run 2":<10} {"Changed?":<10}')
print('-'*40)
for i, (r1, r2) in enumerate(zip(run1_results, run2_results), 1):
    changed = "✅ YES" if r1 != r2 else "❌ No"
    print(f'{i:<6} {r1:<10} {r2:<10} {changed:<10}')

print('\n' + '='*70)
print('🔍 CONCLUSION')
print('='*70)
different = sum(1 for r1, r2 in zip(run1_results, run2_results) if r1 != r2)
if different > 0:
    print(f'✅ {different}/{len(new_tests)} tests showed DIFFERENT confidence values!')
    print('   This proves the system is computing REAL values, not static mocks.')
else:
    print('⚠️  All values were the same. System may be deterministic for same inputs.')
