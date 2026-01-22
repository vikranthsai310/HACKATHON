import requests
import json
import random
import sys
from typing import Dict, List
import time

BASE = 'http://localhost:8000/api/v1/decision/quick'

# Check if HRM backend is running
try:
    test_response = requests.get('http://localhost:8000/health', timeout=2)
except:
    print("\n❌ ERROR: HRM backend is not running!")
    print("Please start the backend first: python -m uvicorn app.main:app --host 127.0.0.1 --port 8000")
    sys.exit(1)

print("\n" + "="*80)
print("🎯 HRM PERSONALIZED CAREER DECISION ANALYSIS")
print("="*80)

# Your Profile
profile = {
    "education": "10th Grade Completed",
    "skills": ["Coding", "Dancing", "Singing"],
    "skill_levels": {
        "coding": 75,      # Assumed moderate coding skills
        "dancing": 70,     # Good dancing skills
        "singing": 65,     # Decent singing skills
        "communication": 60,
        "creativity": 80,
        "technical": 70,
        "physical_fitness": 75,
        "artistic": 75
    }
}

print(f"""
📋 YOUR PROFILE:
   🎓 Education: {profile['education']}
   💡 Skills: {', '.join(profile['skills'])}
""")

# 25 Career Options with skill requirements
careers = [
    # Tech Careers (Coding focused)
    {"name": "Software Developer", "category": "Tech", "requires": ["coding", "technical"], "min_education": "12th", "success_base": 80, "growth": "High", "salary_range": "₹4-15 LPA", "timeframe": "2-3 years"},
    {"name": "Web Developer", "category": "Tech", "requires": ["coding", "creativity"], "min_education": "10th", "success_base": 85, "growth": "High", "salary_range": "₹3-12 LPA", "timeframe": "1-2 years"},
    {"name": "Mobile App Developer", "category": "Tech", "requires": ["coding", "technical"], "min_education": "12th", "success_base": 78, "growth": "High", "salary_range": "₹5-18 LPA", "timeframe": "2-4 years"},
    {"name": "Game Developer", "category": "Tech", "requires": ["coding", "creativity"], "min_education": "12th", "success_base": 70, "growth": "Medium", "salary_range": "₹3-10 LPA", "timeframe": "3-5 years"},
    {"name": "Freelance Programmer", "category": "Tech", "requires": ["coding"], "min_education": "10th", "success_base": 75, "growth": "Medium", "salary_range": "₹2-8 LPA", "timeframe": "1-2 years"},
    
    # Creative/Performance Careers
    {"name": "Professional Dancer", "category": "Performance", "requires": ["dancing", "physical_fitness"], "min_education": "10th", "success_base": 60, "growth": "Medium", "salary_range": "₹1-6 LPA", "timeframe": "3-5 years"},
    {"name": "Dance Choreographer", "category": "Performance", "requires": ["dancing", "creativity"], "min_education": "10th", "success_base": 55, "growth": "Medium", "salary_range": "₹2-8 LPA", "timeframe": "4-6 years"},
    {"name": "Dance Teacher", "category": "Education", "requires": ["dancing", "communication"], "min_education": "10th", "success_base": 70, "growth": "Stable", "salary_range": "₹2-5 LPA", "timeframe": "1-2 years"},
    {"name": "Playback Singer", "category": "Performance", "requires": ["singing", "artistic"], "min_education": "10th", "success_base": 40, "growth": "Low", "salary_range": "₹1-10 LPA", "timeframe": "5-10 years"},
    {"name": "Music Teacher", "category": "Education", "requires": ["singing", "communication"], "min_education": "10th", "success_base": 72, "growth": "Stable", "salary_range": "₹2-4 LPA", "timeframe": "1-2 years"},
    {"name": "YouTube Content Creator", "category": "Digital", "requires": ["singing", "dancing", "creativity"], "min_education": "10th", "success_base": 50, "growth": "High", "salary_range": "₹0-20 LPA", "timeframe": "2-4 years"},
    {"name": "Social Media Influencer", "category": "Digital", "requires": ["creativity", "communication"], "min_education": "10th", "success_base": 45, "growth": "Medium", "salary_range": "₹0-15 LPA", "timeframe": "1-3 years"},
    
    # Hybrid Careers (Tech + Creative)
    {"name": "UI/UX Designer", "category": "Tech", "requires": ["coding", "creativity", "artistic"], "min_education": "12th", "success_base": 75, "growth": "High", "salary_range": "₹4-12 LPA", "timeframe": "2-3 years"},
    {"name": "Motion Graphics Artist", "category": "Creative", "requires": ["coding", "creativity", "artistic"], "min_education": "10th", "success_base": 70, "growth": "High", "salary_range": "₹3-10 LPA", "timeframe": "2-4 years"},
    {"name": "Video Editor", "category": "Creative", "requires": ["creativity", "technical"], "min_education": "10th", "success_base": 72, "growth": "High", "salary_range": "₹2-8 LPA", "timeframe": "1-3 years"},
    {"name": "Music Producer (Digital)", "category": "Creative", "requires": ["singing", "coding", "creativity"], "min_education": "10th", "success_base": 65, "growth": "Medium", "salary_range": "₹2-12 LPA", "timeframe": "3-5 years"},
    
    # Traditional Careers
    {"name": "BPO/Call Center", "category": "Service", "requires": ["communication"], "min_education": "10th", "success_base": 80, "growth": "Low", "salary_range": "₹2-4 LPA", "timeframe": "0-1 year"},
    {"name": "Data Entry Operator", "category": "Office", "requires": ["technical"], "min_education": "10th", "success_base": 85, "growth": "Low", "salary_range": "₹1-3 LPA", "timeframe": "0-6 months"},
    {"name": "Retail Sales", "category": "Sales", "requires": ["communication"], "min_education": "10th", "success_base": 75, "growth": "Low", "salary_range": "₹1-3 LPA", "timeframe": "0-1 year"},
    {"name": "Event Coordinator", "category": "Events", "requires": ["communication", "creativity"], "min_education": "10th", "success_base": 68, "growth": "Medium", "salary_range": "₹2-6 LPA", "timeframe": "1-3 years"},
    
    # Entrepreneurship
    {"name": "Dance Academy Owner", "category": "Business", "requires": ["dancing", "communication"], "min_education": "10th", "success_base": 55, "growth": "Medium", "salary_range": "₹3-15 LPA", "timeframe": "3-5 years"},
    {"name": "Coding Bootcamp Trainer", "category": "Education", "requires": ["coding", "communication"], "min_education": "12th", "success_base": 65, "growth": "High", "salary_range": "₹3-8 LPA", "timeframe": "2-3 years"},
    {"name": "Freelance Content Creator", "category": "Digital", "requires": ["creativity", "coding"], "min_education": "10th", "success_base": 60, "growth": "High", "salary_range": "₹2-10 LPA", "timeframe": "1-3 years"},
    {"name": "Online Tutor", "category": "Education", "requires": ["communication", "technical"], "min_education": "10th", "success_base": 75, "growth": "High", "salary_range": "₹2-6 LPA", "timeframe": "0-1 year"},
    {"name": "E-commerce Seller", "category": "Business", "requires": ["technical", "communication"], "min_education": "10th", "success_base": 60, "growth": "Medium", "salary_range": "₹1-8 LPA", "timeframe": "1-2 years"},
]

def calculate_skill_match(career, skill_levels):
    """Calculate how well skills match career requirements"""
    skill_map = {
        "coding": skill_levels["coding"],
        "dancing": skill_levels.get("dancing", 50),
        "singing": skill_levels.get("singing", 50),
        "communication": skill_levels["communication"],
        "creativity": skill_levels["creativity"],
        "technical": skill_levels["technical"],
        "physical_fitness": skill_levels["physical_fitness"],
        "artistic": skill_levels["artistic"]
    }
    
    required_skills = career["requires"]
    total = sum(skill_map.get(s, 50) for s in required_skills)
    return total / len(required_skills)

def check_education(career, current_edu):
    """Check if education requirement is met"""
    edu_levels = {"10th": 1, "12th": 2, "Graduate": 3}
    required = edu_levels.get(career["min_education"], 1)
    current = edu_levels.get(current_edu, 1)
    return current >= required

print("="*80)
print("📊 ANALYZING 25 CAREER OPTIONS WITH HRM...")
print("="*80)

results = []
start_time = time.time()

for i, career in enumerate(careers, 1):
    # Progress bar
    progress = int((i / len(careers)) * 40)
    bar = '█' * progress + '░' * (40 - progress)
    print(f"\rProgress: [{bar}] {i}/{len(careers)} - {career['name'][:25]:<25}", end='', flush=True)
    # Calculate metrics
    skill_match = calculate_skill_match(career, profile["skill_levels"])
    edu_met = check_education(career, "10th")
    
    # Build HRM query
    message = f"""Analyze career decision for student with coding, dancing, singing skills (10th pass):
    Career: {career['name']}
    Category: {career['category']}
    Required Skills: {', '.join(career['requires'])}
    Skill Match: {skill_match:.0f}%
    Education Met: {'Yes' if edu_met else 'No - needs {}'.format(career['min_education'])}
    Base Success Rate: {career['success_base']}%
    Growth Potential: {career['growth']}
    Should this career path be pursued? Predict PASS or FAIL."""
    
    # Send to HRM with error handling
    try:
        r = requests.post(BASE, json={'message': message}, timeout=10)
        r.raise_for_status()
        d = r.json()
    except requests.exceptions.RequestException as e:
        print(f"\n⚠️ API Error for {career['name']}: {e}")
        d = {'confidence': 0.5, 'audit_trail': {'L1_strategic': {'risk_level': 'HIGH'}}}
    
    hrm_confidence = d.get('confidence', 0.5)
    l1 = d.get('audit_trail', {}).get('L1_strategic', {})
    risk_level = l1.get('risk_level', 'MEDIUM')
    
    # Calculate final score
    edu_penalty = 0 if edu_met else -15
    risk_bonus = {"LOW": 10, "MEDIUM": 0, "HIGH": -10, "CRITICAL": -20}.get(risk_level, 0)
    
    final_score = (
        (skill_match * 0.4) +
        (career['success_base'] * 0.3) +
        (hrm_confidence * 30) +
        edu_penalty +
        risk_bonus
    )
    
    # Determine PASS/FAIL
    if final_score >= 65:
        verdict = "✅ PASS"
        recommendation = "RECOMMENDED"
    elif final_score >= 50:
        verdict = "⚠️ RISKY"
        recommendation = "CONSIDER WITH CAUTION"
    else:
        verdict = "❌ FAIL"
        recommendation = "NOT RECOMMENDED"
    
    results.append({
        "rank": i,
        "name": career["name"],
        "category": career["category"],
        "skill_match": skill_match,
        "edu_met": edu_met,
        "hrm_confidence": hrm_confidence,
        "risk": risk_level,
        "final_score": final_score,
        "verdict": verdict,
        "recommendation": recommendation,
        "growth": career["growth"],
        "salary_range": career.get("salary_range", "N/A"),
        "timeframe": career.get("timeframe", "N/A")
    })

print(f"\rProgress: [{'█' * 40}] {len(careers)}/{len(careers)} - Complete!{' ' * 25}")
elapsed = time.time() - start_time
print(f"\n✅ Analysis complete in {elapsed:.1f} seconds\n")

# Sort by final score
results_sorted = sorted(results, key=lambda x: x['final_score'], reverse=True)

print("\n" + "="*80)
print("🏆 FINAL RANKINGS - BEST TO WORST")
print("="*80)

print(f"\n{'Rank':<5} {'Career':<25} {'Score':<7} {'Salary':<12} {'Time':<10} {'Verdict':<10}")
print("-"*80)

pass_count = 0
fail_count = 0
risky_count = 0

for i, r in enumerate(results_sorted, 1):
    emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "  "
    print(f"{emoji}{i:<3} {r['name']:<25} {r['final_score']:<7.1f} {r['salary_range']:<12} {r['timeframe']:<10} {r['verdict']:<10}")
    
    if "PASS" in r['verdict']:
        pass_count += 1
    elif "FAIL" in r['verdict']:
        fail_count += 1
    else:
        risky_count += 1

print("\n" + "="*80)
print("📈 SUMMARY STATISTICS")
print("="*80)
print(f"""
   ✅ PASS (Recommended): {pass_count} careers
   ⚠️  RISKY (Consider): {risky_count} careers  
   ❌ FAIL (Avoid): {fail_count} careers
""")

# Category-wise analysis
category_stats = {}
for r in results_sorted:
    cat = r['category']
    if cat not in category_stats:
        category_stats[cat] = {'count': 0, 'avg_score': 0, 'total': 0}
    category_stats[cat]['count'] += 1
    category_stats[cat]['total'] += r['final_score']

print("\n📊 CATEGORY-WISE PERFORMANCE:")
for cat, stats in sorted(category_stats.items(), key=lambda x: x[1]['total']/x[1]['count'], reverse=True):
    avg = stats['total'] / stats['count']
    print(f"   {cat:<15} - Avg Score: {avg:.1f} ({stats['count']} careers)")

print("="*80)
print("🎯 TOP 5 RECOMMENDED CAREERS FOR YOU")
print("="*80)

for i, r in enumerate(results_sorted[:5], 1):
    print(f"""
{i}. 🌟 {r['name'].upper()}
   📊 Final Score: {r['final_score']:.1f}/100
   🎯 Skill Match: {r['skill_match']:.0f}%
   📈 Growth: {r['growth']} | Category: {r['category']}
   💰 Salary Range: {r['salary_range']}
   ⏱️  Time to Success: {r['timeframe']}
   💯 HRM Confidence: {r['hrm_confidence']} | Risk: {r['risk']}
   ✅ Verdict: {r['recommendation']}
""")

print("="*80)
print("⚠️ TOP 5 CAREERS TO AVOID")
print("="*80)

for i, r in enumerate(results_sorted[-5:], 1):
    print(f"   {i}. ❌ {r['name']} (Score: {r['final_score']:.1f})")

print("\n" + "="*80)
print("💡 HRM FINAL RECOMMENDATION")
print("="*80)

best = results_sorted[0]
print(f"""
Based on your skills (Coding, Dancing, Singing) and 10th grade education:

🏆 BEST CAREER CHOICE: {best['name'].upper()}

📊 Why this is best for you:
   • Skill Match: {best['skill_match']:.0f}%
   • Final Score: {best['final_score']:.1f}/100
   • Growth Potential: {best['growth']}
   • Risk Level: {best['risk']}

🚀 ACTION PLAN:
   1. Focus on improving your coding skills
   2. Build a portfolio showcasing your work
   3. Consider online courses/certifications
   4. Start freelancing to gain experience
   5. Use your creative skills (dance/singing) for content creation

💡 SMART STRATEGY:
   Combine your unique skill set:
   - Coding + Creativity = Web/App Development
   - Dancing + Tech = YouTube/Social Media
   - Singing + Coding = Music Production/Audio Apps

⚠️ CAREERS TO AVOID (Low Success Probability):
   - {results_sorted[-1]['name']} (Score: {results_sorted[-1]['final_score']:.1f})
   - {results_sorted[-2]['name']} (Score: {results_sorted[-2]['final_score']:.1f})
   - {results_sorted[-3]['name']} (Score: {results_sorted[-3]['final_score']:.1f})
""")
print("="*80)

# Detailed comparison of top 3
print("\n" + "="*80)
print("🔍 DETAILED COMPARISON: TOP 3 CAREERS")
print("="*80)
print(f"\n{'Metric':<25} {'🥇 #1':<25} {'🥈 #2':<25} {'🥉 #3':<25}")
print("-"*100)
metrics = [
    ('Career', 'name'),
    ('Final Score', lambda r: f"{r['final_score']:.1f}/100"),
    ('Salary Range', 'salary_range'),
    ('Timeframe', 'timeframe'),
    ('Growth Potential', 'growth'),
    ('Risk Level', 'risk'),
    ('Category', 'category'),
]
for metric_name, key in metrics:
    values = []
    for r in results_sorted[:3]:
        val = key(r) if callable(key) else r[key]
        values.append(str(val)[:23])
    print(f"{metric_name:<25} {values[0]:<25} {values[1]:<25} {values[2]:<25}")

print("\n" + "="*80)
