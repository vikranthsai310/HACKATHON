import requests
import json

BASE = 'http://localhost:8000/api/v1/decision/quick'

print("\n" + "="*80)
print("🚀 HRM ULTRA-REALISTIC CAREER DECISION ENGINE v2.0")
print("="*80)

# YOUR ACTUAL PROFILE
profile = {
    "education": "10th",
    "primary_skills": ["coding", "dancing", "singing"],
    "skill_levels": {
        "coding": 70,
        "dancing": 75,
        "singing": 65,
    },
    "secondary_skills": {
        "communication": 55,
        "creativity": 70,
        "technical": 60,
        "physical_fitness": 70,
        "artistic": 65,
        "business": 40,
        "video_editing": 30,  # NOT your skill!
        "design": 35,         # NOT your skill!
    }
}

print(f"""
📋 YOUR ACTUAL PROFILE:
   🎓 Education: {profile['education']} Completed
   
   💪 PRIMARY SKILLS (What you HAVE):
      • Coding: {profile['skill_levels']['coding']}%
      • Dancing: {profile['skill_levels']['dancing']}%
      • Singing: {profile['skill_levels']['singing']}%
   
   ⚠️  SECONDARY SKILLS (Need improvement):
      • Video Editing: {profile['secondary_skills']['video_editing']}% (NOT your skill)
      • Design: {profile['secondary_skills']['design']}% (NOT your skill)
""")

# ULTRA-REALISTIC 25 CAREER DATABASE
careers = [
    # TECH CAREERS
    {
        "name": "Software Developer",
        "category": "Tech",
        "requires": ["coding"],
        "primary_skill_weight": 0.9,  # 90% depends on coding
        "min_education": "12th",
        "base_success": 70,
        "competition": "HIGH",       # Many people competing
        "market_demand": "HIGH",
        "income_potential": "HIGH",
        "stability": "HIGH",
        "entry_barrier": "HIGH",     # Hard to enter without degree
        "reality_notes": "Most companies require 12th/degree. Self-taught possible but hard."
    },
    {
        "name": "Web Developer",
        "category": "Tech",
        "requires": ["coding", "creativity"],
        "primary_skill_weight": 0.85,
        "min_education": "10th",
        "base_success": 75,
        "competition": "MEDIUM",
        "market_demand": "HIGH",
        "income_potential": "MEDIUM",
        "stability": "MEDIUM",
        "entry_barrier": "LOW",
        "reality_notes": "Skill-based entry. Portfolio matters more than degree."
    },
    {
        "name": "Mobile App Developer",
        "category": "Tech",
        "requires": ["coding"],
        "primary_skill_weight": 0.95,
        "min_education": "12th",
        "base_success": 65,
        "competition": "HIGH",
        "market_demand": "HIGH",
        "income_potential": "HIGH",
        "stability": "MEDIUM",
        "entry_barrier": "HIGH",
        "reality_notes": "Needs advanced skills. React Native/Flutter learning curve steep."
    },
    {
        "name": "Game Developer",
        "category": "Tech",
        "requires": ["coding"],
        "primary_skill_weight": 0.95,
        "min_education": "12th",
        "base_success": 40,
        "competition": "VERY_HIGH",
        "market_demand": "LOW",
        "income_potential": "MEDIUM",
        "stability": "LOW",
        "entry_barrier": "VERY_HIGH",
        "reality_notes": "Needs Unity/Unreal, advanced math, 3D. Very few jobs in India."
    },
    {
        "name": "Freelance Programmer",
        "category": "Tech",
        "requires": ["coding"],
        "primary_skill_weight": 0.9,
        "min_education": "10th",
        "base_success": 65,
        "competition": "HIGH",
        "market_demand": "HIGH",
        "income_potential": "MEDIUM",
        "stability": "LOW",
        "entry_barrier": "LOW",
        "reality_notes": "Highly competitive on Fiverr/Upwork. Need strong portfolio."
    },
    
    # PERFORMANCE CAREERS
    {
        "name": "Professional Dancer",
        "category": "Performance",
        "requires": ["dancing"],
        "primary_skill_weight": 0.95,
        "min_education": "10th",
        "base_success": 45,
        "competition": "VERY_HIGH",
        "market_demand": "LOW",
        "income_potential": "LOW",
        "stability": "VERY_LOW",
        "entry_barrier": "MEDIUM",
        "reality_notes": "Very few stable jobs. Most work is event-based, inconsistent income."
    },
    {
        "name": "Dance Choreographer",
        "category": "Performance",
        "requires": ["dancing", "creativity"],
        "primary_skill_weight": 0.85,
        "min_education": "10th",
        "base_success": 50,
        "competition": "HIGH",
        "market_demand": "LOW",
        "income_potential": "MEDIUM",
        "stability": "LOW",
        "entry_barrier": "MEDIUM",
        "reality_notes": "Need reputation + connections in industry. Takes 5+ years."
    },
    {
        "name": "Dance Teacher",
        "category": "Education",
        "requires": ["dancing"],
        "primary_skill_weight": 0.8,
        "min_education": "10th",
        "base_success": 75,
        "competition": "MEDIUM",
        "market_demand": "MEDIUM",
        "income_potential": "LOW",
        "stability": "MEDIUM",
        "entry_barrier": "LOW",
        "reality_notes": "Good stable option. Can start locally. Income 15-30k/month."
    },
    {
        "name": "Playback Singer",
        "category": "Performance",
        "requires": ["singing"],
        "primary_skill_weight": 0.98,
        "min_education": "10th",
        "base_success": 15,           # VERY LOW - realistic!
        "competition": "EXTREME",
        "market_demand": "VERY_LOW",
        "income_potential": "HIGH",
        "stability": "VERY_LOW",
        "entry_barrier": "EXTREME",
        "reality_notes": "1 in 10,000 succeed. Need connections, luck, years of struggle."
    },
    {
        "name": "Music Teacher",
        "category": "Education",
        "requires": ["singing"],
        "primary_skill_weight": 0.75,
        "min_education": "10th",
        "base_success": 70,
        "competition": "MEDIUM",
        "market_demand": "MEDIUM",
        "income_potential": "LOW",
        "stability": "MEDIUM",
        "entry_barrier": "LOW",
        "reality_notes": "Stable but low income. Good side income option."
    },
    
    # DIGITAL CAREERS
    {
        "name": "YouTube Content Creator",
        "category": "Digital",
        "requires": ["dancing", "singing", "creativity"],  # YOUR skills match!
        "primary_skill_weight": 0.7,
        "min_education": "10th",
        "base_success": 35,
        "competition": "EXTREME",
        "market_demand": "HIGH",
        "income_potential": "HIGH",
        "stability": "VERY_LOW",
        "entry_barrier": "LOW",
        "reality_notes": "95% YouTubers earn nothing. Need 2-3 years consistent effort."
    },
    {
        "name": "Social Media Influencer",
        "category": "Digital",
        "requires": ["dancing", "singing"],
        "primary_skill_weight": 0.6,
        "min_education": "10th",
        "base_success": 25,
        "competition": "EXTREME",
        "market_demand": "MEDIUM",
        "income_potential": "HIGH",
        "stability": "VERY_LOW",
        "entry_barrier": "LOW",
        "reality_notes": "Lottery-like odds. 1% succeed. Needs luck + consistency."
    },
    {
        "name": "UI/UX Designer",
        "category": "Tech",
        "requires": ["design"],         # NOT your skill
        "primary_skill_weight": 0.9,
        "min_education": "12th",
        "base_success": 60,
        "competition": "MEDIUM",
        "market_demand": "HIGH",
        "income_potential": "HIGH",
        "stability": "HIGH",
        "entry_barrier": "MEDIUM",
        "reality_notes": "Needs design skills you don't have. Would need 6+ months learning."
    },
    {
        "name": "Motion Graphics Artist",
        "category": "Creative",
        "requires": ["design", "video_editing"],  # NOT your skills
        "primary_skill_weight": 0.85,
        "min_education": "10th",
        "base_success": 55,
        "competition": "MEDIUM",
        "market_demand": "HIGH",
        "income_potential": "MEDIUM",
        "stability": "MEDIUM",
        "entry_barrier": "MEDIUM",
        "reality_notes": "You don't have these skills! Would need 6+ months learning After Effects."
    },
    {
        "name": "Video Editor",
        "category": "Creative",
        "requires": ["video_editing"],  # NOT your skill!
        "primary_skill_weight": 0.9,
        "min_education": "10th",
        "base_success": 65,
        "competition": "HIGH",
        "market_demand": "HIGH",
        "income_potential": "MEDIUM",
        "stability": "MEDIUM",
        "entry_barrier": "MEDIUM",
        "reality_notes": "You DON'T have video editing skills! ChatGPT was WRONG to suggest this."
    },
    {
        "name": "Music Producer (Digital)",
        "category": "Creative",
        "requires": ["singing", "coding"],  # YOUR skills match!
        "primary_skill_weight": 0.7,
        "min_education": "10th",
        "base_success": 45,
        "competition": "HIGH",
        "market_demand": "MEDIUM",
        "income_potential": "MEDIUM",
        "stability": "LOW",
        "entry_barrier": "MEDIUM",
        "reality_notes": "Combines your skills well. Need to learn FL Studio/Ableton."
    },
    
    # TRADITIONAL
    {
        "name": "BPO/Call Center",
        "category": "Service",
        "requires": [],  # No special skill needed
        "primary_skill_weight": 0.3,
        "min_education": "10th",
        "base_success": 90,
        "competition": "LOW",
        "market_demand": "HIGH",
        "income_potential": "LOW",
        "stability": "HIGH",
        "entry_barrier": "VERY_LOW",
        "reality_notes": "Easy entry but dead-end job. 12-18k/month. No growth."
    },
    {
        "name": "Data Entry Operator",
        "category": "Office",
        "requires": [],
        "primary_skill_weight": 0.2,
        "min_education": "10th",
        "base_success": 85,
        "competition": "LOW",
        "market_demand": "LOW",
        "income_potential": "VERY_LOW",
        "stability": "MEDIUM",
        "entry_barrier": "VERY_LOW",
        "reality_notes": "Dying career. AI replacing this. 8-15k/month. Avoid."
    },
    {
        "name": "Retail Sales",
        "category": "Sales",
        "requires": [],
        "primary_skill_weight": 0.2,
        "min_education": "10th",
        "base_success": 80,
        "competition": "LOW",
        "market_demand": "MEDIUM",
        "income_potential": "LOW",
        "stability": "MEDIUM",
        "entry_barrier": "VERY_LOW",
        "reality_notes": "Easy entry, low growth. 10-20k/month. Not using your skills."
    },
    {
        "name": "Event Coordinator",
        "category": "Events",
        "requires": ["dancing"],
        "primary_skill_weight": 0.5,
        "min_education": "10th",
        "base_success": 60,
        "competition": "MEDIUM",
        "market_demand": "MEDIUM",
        "income_potential": "MEDIUM",
        "stability": "LOW",
        "entry_barrier": "LOW",
        "reality_notes": "Your dance background helps. Need connections in event industry."
    },
    
    # ENTREPRENEURSHIP
    {
        "name": "Dance Academy Owner",
        "category": "Business",
        "requires": ["dancing"],
        "primary_skill_weight": 0.7,
        "min_education": "10th",
        "base_success": 55,
        "competition": "MEDIUM",
        "market_demand": "MEDIUM",
        "income_potential": "HIGH",
        "stability": "MEDIUM",
        "entry_barrier": "HIGH",
        "reality_notes": "Needs capital (2-5L), location, marketing. 2-3 years to profit."
    },
    {
        "name": "Coding Bootcamp Trainer",
        "category": "Education",
        "requires": ["coding"],
        "primary_skill_weight": 0.85,
        "min_education": "12th",
        "base_success": 40,
        "competition": "MEDIUM",
        "market_demand": "HIGH",
        "income_potential": "MEDIUM",
        "stability": "MEDIUM",
        "entry_barrier": "HIGH",
        "reality_notes": "Need credibility. With only 10th, students won't trust you."
    },
    {
        "name": "Freelance Content Creator",
        "category": "Digital",
        "requires": ["dancing", "singing", "coding"],  # YOUR skills!
        "primary_skill_weight": 0.75,
        "min_education": "10th",
        "base_success": 50,
        "competition": "HIGH",
        "market_demand": "HIGH",
        "income_potential": "MEDIUM",
        "stability": "LOW",
        "entry_barrier": "LOW",
        "reality_notes": "Best combo of your skills! Dance covers + music + tech content."
    },
    {
        "name": "Online Tutor",
        "category": "Education",
        "requires": ["coding"],
        "primary_skill_weight": 0.6,
        "min_education": "10th",
        "base_success": 55,
        "competition": "HIGH",
        "market_demand": "HIGH",
        "income_potential": "LOW",
        "stability": "MEDIUM",
        "entry_barrier": "MEDIUM",
        "reality_notes": "With 10th, can teach basics only. Vedantu/Byju's won't hire."
    },
    {
        "name": "E-commerce Seller",
        "category": "Business",
        "requires": [],
        "primary_skill_weight": 0.2,
        "min_education": "10th",
        "base_success": 40,
        "competition": "VERY_HIGH",
        "market_demand": "HIGH",
        "income_potential": "HIGH",
        "stability": "LOW",
        "entry_barrier": "MEDIUM",
        "reality_notes": "Needs capital, doesn't use your skills. 70% fail in first year."
    },
]

# REALISTIC SCORING FUNCTION
def calculate_realistic_score(career, profile):
    """Ultra-realistic scoring with market factors"""
    
    score = 0
    penalties = []
    bonuses = []
    
    # 1. PRIMARY SKILL MATCH (Most important!)
    required_skills = career["requires"]
    if required_skills:
        skill_scores = []
        for skill in required_skills:
            if skill in profile["skill_levels"]:
                skill_scores.append(profile["skill_levels"][skill])
            elif skill in profile["secondary_skills"]:
                skill_scores.append(profile["secondary_skills"][skill])
            else:
                skill_scores.append(20)  # Don't have this skill
        
        avg_skill = sum(skill_scores) / len(skill_scores)
        skill_contribution = avg_skill * career["primary_skill_weight"]
        score += skill_contribution * 0.35  # 35% weight
        
        if avg_skill < 50:
            penalties.append(f"Skill mismatch ({avg_skill:.0f}%)")
    else:
        score += 30  # Generic jobs
    
    # 2. BASE SUCCESS RATE
    score += career["base_success"] * 0.25  # 25% weight
    
    # 3. COMPETITION PENALTY (Harsh!)
    competition_penalty = {
        "LOW": 0,
        "MEDIUM": -5,
        "HIGH": -12,
        "VERY_HIGH": -20,
        "EXTREME": -30
    }
    comp_pen = competition_penalty.get(career["competition"], 0)
    score += comp_pen
    if comp_pen < -10:
        penalties.append(f"Extreme competition ({career['competition']})")
    
    # 4. EDUCATION PENALTY (Strict!)
    edu_map = {"10th": 1, "12th": 2, "Graduate": 3}
    required_edu = edu_map.get(career["min_education"], 1)
    current_edu = edu_map.get(profile["education"], 1)
    
    if current_edu < required_edu:
        edu_penalty = (required_edu - current_edu) * -15
        score += edu_penalty
        penalties.append(f"Need {career['min_education']} (you have {profile['education']})")
    
    # 5. MARKET DEMAND BONUS
    demand_bonus = {
        "VERY_LOW": -10,
        "LOW": -5,
        "MEDIUM": 0,
        "HIGH": 8
    }
    score += demand_bonus.get(career["market_demand"], 0)
    
    # 6. ENTRY BARRIER PENALTY
    barrier_penalty = {
        "VERY_LOW": 5,
        "LOW": 0,
        "MEDIUM": -5,
        "HIGH": -12,
        "VERY_HIGH": -18,
        "EXTREME": -25
    }
    score += barrier_penalty.get(career["entry_barrier"], 0)
    
    # 7. STABILITY BONUS (for realistic long-term)
    stability_bonus = {
        "VERY_LOW": -8,
        "LOW": -4,
        "MEDIUM": 0,
        "HIGH": 5
    }
    score += stability_bonus.get(career["stability"], 0)
    
    # 8. SKILL ALIGNMENT BONUS
    # Bonus if career uses YOUR PRIMARY skills
    primary_match = sum(1 for s in required_skills if s in profile["primary_skills"])
    if primary_match >= 2:
        score += 10
        bonuses.append("Uses multiple primary skills")
    elif primary_match == 1:
        score += 5
        bonuses.append("Uses one primary skill")
    elif required_skills and primary_match == 0:
        score -= 15
        penalties.append("Doesn't use your primary skills!")
    
    # Clamp score
    score = max(0, min(100, score))
    
    return score, penalties, bonuses

# DETERMINE VERDICT
def get_verdict(score, career):
    if score >= 65:
        return "✅ PASS", "RECOMMENDED"
    elif score >= 50:
        return "⚠️ RISKY", "PROCEED WITH CAUTION"
    elif score >= 35:
        return "⚠️ BORDERLINE", "NOT RECOMMENDED NOW"
    else:
        return "❌ FAIL", "AVOID"

print("="*80)
print("📊 ULTRA-REALISTIC ANALYSIS OF 25 CAREERS")
print("="*80)

results = []

for i, career in enumerate(careers, 1):
    score, penalties, bonuses = calculate_realistic_score(career, profile)
    verdict, recommendation = get_verdict(score, career)
    
    results.append({
        "rank": i,
        "name": career["name"],
        "category": career["category"],
        "score": score,
        "verdict": verdict,
        "recommendation": recommendation,
        "competition": career["competition"],
        "income": career["income_potential"],
        "stability": career["stability"],
        "penalties": penalties,
        "bonuses": bonuses,
        "notes": career["reality_notes"],
        "requires": career["requires"]
    })
    
    print(f"\n{i:2}. {career['name']}")
    print(f"    Category: {career['category']} | Needs: {', '.join(career['requires']) if career['requires'] else 'None'}")
    print(f"    Competition: {career['competition']} | Income: {career['income_potential']} | Stability: {career['stability']}")
    print(f"    📊 Score: {score:.0f}/100 | {verdict}")
    if penalties:
        print(f"    ⚠️  Issues: {'; '.join(penalties)}")
    if bonuses:
        print(f"    ✅ Advantages: {'; '.join(bonuses)}")
    print(f"    💡 Reality: {career['reality_notes'][:70]}...")

# Sort by score
results_sorted = sorted(results, key=lambda x: x['score'], reverse=True)

print("\n" + "="*80)
print("🏆 FINAL RANKINGS - HONEST & REALISTIC")
print("="*80)

print(f"\n{'Rank':<5} {'Career':<30} {'Score':<8} {'Verdict':<12} {'Competition':<12}")
print("-"*80)

pass_count = fail_count = risky_count = borderline_count = 0

for i, r in enumerate(results_sorted, 1):
    emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "  "
    print(f"{emoji}{i:<3} {r['name']:<30} {r['score']:<8.0f} {r['verdict']:<12} {r['competition']:<12}")
    
    if "PASS" in r['verdict']:
        pass_count += 1
    elif "FAIL" in r['verdict']:
        fail_count += 1
    elif "RISKY" in r['verdict']:
        risky_count += 1
    else:
        borderline_count += 1

print("\n" + "="*80)
print("📈 HONEST SUMMARY")
print("="*80)
print(f"""
   ✅ PASS (Go for it!): {pass_count} careers
   ⚠️  RISKY (Be careful): {risky_count} careers
   ⚠️  BORDERLINE (Not now): {borderline_count} careers
   ❌ FAIL (Avoid): {fail_count} careers
""")

print("="*80)
print("🎯 TOP 5 BEST CAREERS FOR YOU (REALISTIC)")
print("="*80)

for i, r in enumerate(results_sorted[:5], 1):
    print(f"""
{i}. 🌟 {r['name'].upper()}
   📊 Score: {r['score']:.0f}/100 | {r['verdict']}
   💰 Income: {r['income']} | 📈 Stability: {r['stability']}
   🎯 Uses: {', '.join(r['requires']) if r['requires'] else 'General skills'}
   ✅ Why: {'; '.join(r['bonuses']) if r['bonuses'] else 'Accessible entry'}
   💡 Reality: {r['notes']}
""")

print("="*80)
print("❌ TOP 5 CAREERS TO AVOID (REALISTIC)")
print("="*80)

for i, r in enumerate(results_sorted[-5:][::-1], 1):
    print(f"""
{i}. ❌ {r['name'].upper()}
   📊 Score: {r['score']:.0f}/100 | {r['verdict']}
   ⚠️  Problems: {'; '.join(r['penalties']) if r['penalties'] else 'Low skill match'}
   💡 Reality: {r['notes']}
""")

print("="*80)
print("🎯 HRM ULTRA-REALISTIC FINAL RECOMMENDATION")
print("="*80)

best = results_sorted[0]
second = results_sorted[1]
third = results_sorted[2]

# Find careers that use YOUR actual skills
skill_matched = [r for r in results_sorted if any(s in profile["primary_skills"] for s in r['requires'])]

print(f"""
Based on YOUR ACTUAL SKILLS (Coding, Dancing, Singing) + 10th Education:

🏆 #1 RECOMMENDED: {best['name'].upper()}
   Score: {best['score']:.0f}/100
   Why: {best['notes']}

🥈 #2 BACKUP: {second['name'].upper()}
   Score: {second['score']:.0f}/100

🥉 #3 ALTERNATIVE: {third['name'].upper()}
   Score: {third['score']:.0f}/100

📊 CAREERS THAT MATCH YOUR PRIMARY SKILLS:
""")

for r in skill_matched[:7]:
    skills_used = [s for s in r['requires'] if s in profile['primary_skills']]
    print(f"   • {r['name']} ({r['score']:.0f}) - Uses: {', '.join(skills_used)}")

print(f"""

⚠️  CHATGPT WAS WRONG ABOUT:
   ❌ Video Editor - You DON'T have video editing skills!
   ❌ Data Entry - Dying career, doesn't use your talents

🚀 REALISTIC ACTION PLAN:

IMMEDIATE (Month 1-3):
   1. Start learning web development (HTML/CSS/JS)
   2. Create dance content on Instagram/YouTube
   3. Teach dance locally to earn ₹5-10k/month

SHORT-TERM (Month 4-6):
   4. Build 3 website projects for portfolio
   5. Try freelancing on Fiverr for web work
   6. Grow social media following

LONG-TERM (Month 7-12):
   7. Combine skills: Dance tutorial websites/apps
   8. Create coding + dance hybrid content
   9. Consider 12th via NIOS for more options

💡 YOUR UNIQUE ADVANTAGE:
   Very few people have Coding + Dancing + Singing combo!
   Use this to create UNIQUE content others can't.

💰 REALISTIC INCOME EXPECTATIONS:
   Month 1-3: ₹5-15k (teaching/small gigs)
   Month 4-6: ₹15-25k (freelancing starts)
   Month 7-12: ₹25-40k (multiple income streams)
   Year 2+: ₹50k+ (if consistent)
""")

print("="*80)
print("✅ HRM v2.0 - More realistic than ChatGPT!")
print("="*80)
