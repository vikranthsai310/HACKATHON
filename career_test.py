import requests
import json

BASE = 'http://localhost:8000/api/v1/decision/quick'

print("\n" + "="*70)
print("🎓 HRM CAREER DECISION ANALYSIS")
print("="*70)

# Define 10 study options with 2 career paths each
study_options = [
    {
        "field": "Computer Science",
        "careers": [
            {"name": "Software Developer", "success_rate": 85, "failure_rate": 15},
            {"name": "Data Scientist", "success_rate": 78, "failure_rate": 22}
        ],
        "skills_match": 90
    },
    {
        "field": "Artificial Intelligence",
        "careers": [
            {"name": "ML Engineer", "success_rate": 82, "failure_rate": 18},
            {"name": "AI Researcher", "success_rate": 70, "failure_rate": 30}
        ],
        "skills_match": 85
    },
    {
        "field": "Business Administration",
        "careers": [
            {"name": "Business Analyst", "success_rate": 75, "failure_rate": 25},
            {"name": "Management Consultant", "success_rate": 68, "failure_rate": 32}
        ],
        "skills_match": 60
    },
    {
        "field": "Finance",
        "careers": [
            {"name": "Financial Analyst", "success_rate": 72, "failure_rate": 28},
            {"name": "Investment Banker", "success_rate": 65, "failure_rate": 35}
        ],
        "skills_match": 55
    },
    {
        "field": "Cybersecurity",
        "careers": [
            {"name": "Security Engineer", "success_rate": 88, "failure_rate": 12},
            {"name": "Penetration Tester", "success_rate": 80, "failure_rate": 20}
        ],
        "skills_match": 88
    },
    {
        "field": "Cloud Computing",
        "careers": [
            {"name": "Cloud Architect", "success_rate": 83, "failure_rate": 17},
            {"name": "DevOps Engineer", "success_rate": 86, "failure_rate": 14}
        ],
        "skills_match": 82
    },
    {
        "field": "Healthcare IT",
        "careers": [
            {"name": "Health Informatics Specialist", "success_rate": 70, "failure_rate": 30},
            {"name": "Medical Software Developer", "success_rate": 75, "failure_rate": 25}
        ],
        "skills_match": 65
    },
    {
        "field": "Digital Marketing",
        "careers": [
            {"name": "SEO Specialist", "success_rate": 68, "failure_rate": 32},
            {"name": "Growth Hacker", "success_rate": 62, "failure_rate": 38}
        ],
        "skills_match": 45
    },
    {
        "field": "Product Management",
        "careers": [
            {"name": "Product Manager", "success_rate": 74, "failure_rate": 26},
            {"name": "Technical Product Owner", "success_rate": 78, "failure_rate": 22}
        ],
        "skills_match": 70
    },
    {
        "field": "Robotics & Automation",
        "careers": [
            {"name": "Robotics Engineer", "success_rate": 76, "failure_rate": 24},
            {"name": "Automation Specialist", "success_rate": 80, "failure_rate": 20}
        ],
        "skills_match": 75
    }
]

# Calculate weighted scores
def calculate_score(option):
    avg_success = sum(c["success_rate"] for c in option["careers"]) / len(option["careers"])
    skill_weight = option["skills_match"] / 100
    return avg_success * skill_weight

# Sort by calculated score
ranked_options = sorted(study_options, key=calculate_score, reverse=True)

print("\n📊 Your Study Options Analysis:")
print("-"*70)

# Send each option to HRM for decision
results = []
for i, opt in enumerate(ranked_options, 1):
    # Build message for HRM
    career_info = " or ".join([f"{c['name']} ({c['success_rate']}% success)" for c in opt['careers']])
    message = f"Analyze career decision: Study {opt['field']} for careers {career_info}. My skill match is {opt['skills_match']}%."
    
    # Send to HRM
    r = requests.post(BASE, json={'message': message})
    d = r.json()
    
    # Calculate local score
    score = calculate_score(opt)
    
    # Get HRM confidence
    hrm_confidence = d.get('confidence', 0)
    l1 = d.get('audit_trail', {}).get('L1_strategic', {})
    
    results.append({
        'rank': i,
        'field': opt['field'],
        'careers': opt['careers'],
        'skills_match': opt['skills_match'],
        'calculated_score': score,
        'hrm_confidence': hrm_confidence,
        'hrm_risk': l1.get('risk_level', 'UNKNOWN'),
        'hrm_goal': l1.get('goal', '')
    })
    
    print(f"\n{i}. 📚 {opt['field']}")
    print(f"   Career 1: {opt['careers'][0]['name']}")
    print(f"      ✅ Success: {opt['careers'][0]['success_rate']}% | ❌ Failure: {opt['careers'][0]['failure_rate']}%")
    print(f"   Career 2: {opt['careers'][1]['name']}")
    print(f"      ✅ Success: {opt['careers'][1]['success_rate']}% | ❌ Failure: {opt['careers'][1]['failure_rate']}%")
    print(f"   🎯 Your Skill Match: {opt['skills_match']}%")
    print(f"   📈 Weighted Score: {score:.1f}")
    print(f"   🤖 HRM Confidence: {hrm_confidence}")
    print(f"   ⚠️  HRM Risk Level: {l1.get('risk_level', 'N/A')}")

print("\n" + "="*70)
print("🏆 TOP 3 RECOMMENDATIONS BY HRM")
print("="*70)

# Sort by combined score (weighted average of calculated + HRM confidence)
for r in results:
    r['combined_score'] = (r['calculated_score'] * 0.6) + (r['hrm_confidence'] * 40)

top3 = sorted(results, key=lambda x: x['combined_score'], reverse=True)[:3]

for i, rec in enumerate(top3, 1):
    print(f"\n🥇🥈🥉"[i-1:i] + f" #{i}: {rec['field']}")
    print(f"   Best Career: {rec['careers'][0]['name']} ({rec['careers'][0]['success_rate']}% success)")
    print(f"   Your Skills Match: {rec['skills_match']}%")
    print(f"   Combined Score: {rec['combined_score']:.1f}")
    print(f"   HRM Recommendation: {'STRONGLY RECOMMENDED' if rec['hrm_confidence'] > 0.9 else 'RECOMMENDED' if rec['hrm_confidence'] > 0.8 else 'CONSIDER'}")

print("\n" + "="*70)
print("📋 FINAL HRM DECISION")
print("="*70)

best = top3[0]
print(f"""
Based on the Hierarchical Reasoning Model analysis:

🎯 RECOMMENDED PATH: {best['field']}

📊 Analysis Summary:
   • Primary Career: {best['careers'][0]['name']}
     - Success Rate: {best['careers'][0]['success_rate']}%
     - Failure Rate: {best['careers'][0]['failure_rate']}%
   
   • Secondary Career: {best['careers'][1]['name']}
     - Success Rate: {best['careers'][1]['success_rate']}%
     - Failure Rate: {best['careers'][1]['failure_rate']}%

   • Your Skill Alignment: {best['skills_match']}%
   • HRM Confidence: {best['hrm_confidence']}
   • Risk Assessment: {best['hrm_risk']}

💡 REASONING:
   This field has the highest combined score considering:
   1. Career success rates
   2. Your current skill match
   3. Market demand analysis
   4. Risk-adjusted confidence

🚀 ACTION ITEMS:
   1. Focus on strengthening skills for {best['careers'][0]['name']}
   2. Consider {best['careers'][1]['name']} as backup option
   3. Expected success probability: {best['careers'][0]['success_rate'] * best['skills_match'] / 100:.1f}%
""")

print("="*70)
