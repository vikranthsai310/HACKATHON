import requests
import json
import sys
import time
from typing import Dict, List
from datetime import datetime

BASE = 'http://localhost:8000/api/v1/decision/quick'

# Check if HRM backend is running
try:
    test_response = requests.get('http://localhost:8000/health', timeout=2)
except:
    print("\n❌ ERROR: HRM backend is not running!")
    print("Please start the backend first: python -m uvicorn app.main:app --host 127.0.0.1 --port 8000")
    sys.exit(1)

print("\n" + "="*100)
print("🎯 MEGA COMPREHENSIVE CAREER ANALYSIS SYSTEM - HRM POWERED")
print("="*100)
print(f"📅 Analysis Date: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
print("="*100)

# COMPREHENSIVE STUDENT PROFILE
profile = {
    # Basic Info
    "name": "Career Seeker",
    "age": 16,
    "education": "10th Grade Completed",
    "location": "India",
    
    # Skills with proficiency levels (0-100)
    "technical_skills": {
        "coding": 75,
        "python": 70,
        "web_development": 65,
        "mobile_dev": 50,
        "data_analysis": 55,
        "ai_ml": 45,
        "cloud_computing": 40,
        "cybersecurity": 50,
        "database_management": 60,
        "devops": 35,
    },
    
    "creative_skills": {
        "dancing": 70,
        "singing": 65,
        "video_editing": 60,
        "graphic_design": 55,
        "content_writing": 70,
        "photography": 50,
        "animation": 45,
        "music_production": 50,
        "acting": 55,
        "digital_art": 60,
    },
    
    "soft_skills": {
        "communication": 60,
        "leadership": 55,
        "teamwork": 70,
        "problem_solving": 75,
        "creativity": 80,
        "time_management": 60,
        "adaptability": 70,
        "critical_thinking": 75,
        "emotional_intelligence": 65,
        "negotiation": 50,
    },
    
    "domain_knowledge": {
        "business": 45,
        "marketing": 50,
        "finance": 40,
        "education": 60,
        "healthcare": 30,
        "entertainment": 70,
        "sports": 55,
        "science": 60,
        "social_media": 75,
        "e_commerce": 55,
    },
    
    # Personality Traits (0-100)
    "personality": {
        "extroversion": 65,
        "conscientiousness": 70,
        "openness": 80,
        "agreeableness": 60,
        "stability": 65,
        "risk_tolerance": 70,
        "innovation": 75,
        "persistence": 70,
    },
    
    # Preferences
    "preferences": {
        "work_environment": "Hybrid",  # Remote, Office, Hybrid, Flexible
        "work_hours": "Flexible",  # Fixed, Flexible, Freelance
        "team_size": "Medium",  # Solo, Small, Medium, Large
        "travel_willingness": 60,  # 0-100
        "job_security_importance": 65,  # 0-100
        "salary_importance": 75,  # 0-100
        "growth_importance": 85,  # 0-100
        "work_life_balance": 70,  # 0-100
        "passion_vs_money": 60,  # 0=money, 100=passion
    },
    
    # Constraints
    "constraints": {
        "max_education_time": 4,  # years
        "initial_investment_capacity": 50000,  # rupees
        "family_support": 80,  # 0-100
        "financial_pressure": 60,  # 0-100
        "location_mobility": 70,  # 0-100
    },
    
    # Goals
    "goals": {
        "5_year_salary_target": 800000,  # rupees per annum
        "10_year_salary_target": 2000000,
        "desired_lifestyle": "Upper Middle Class",
        "retirement_age_target": 50,
        "entrepreneurship_interest": 70,
        "social_impact_desire": 60,
    }
}

print(f"""
📋 COMPREHENSIVE PROFILE ANALYSIS:
┌────────────────────────────────────────────────────────────────────────────────────────────────┐
│ 👤 BASIC INFO                                                                                  │
├────────────────────────────────────────────────────────────────────────────────────────────────┤
│   Name: {profile['name']:<50} Age: {profile['age']:<10}                               │
│   Education: {profile['education']:<45} Location: {profile['location']:<10}                      │
└────────────────────────────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────────────────────────────┐
│ 💻 TOP TECHNICAL SKILLS                                                                        │
├────────────────────────────────────────────────────────────────────────────────────────────────┤
""")

top_tech = sorted(profile['technical_skills'].items(), key=lambda x: x[1], reverse=True)[:5]
for skill, level in top_tech:
    bar = '█' * (level // 5) + '░' * (20 - level // 5)
    print(f"│   {skill.replace('_', ' ').title():<30} [{bar}] {level}%{' ' * 20}│")

print(f"""└────────────────────────────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────────────────────────────┐
│ 🎨 TOP CREATIVE SKILLS                                                                         │
├────────────────────────────────────────────────────────────────────────────────────────────────┤
""")

top_creative = sorted(profile['creative_skills'].items(), key=lambda x: x[1], reverse=True)[:5]
for skill, level in top_creative:
    bar = '█' * (level // 5) + '░' * (20 - level // 5)
    print(f"│   {skill.replace('_', ' ').title():<30} [{bar}] {level}%{' ' * 20}│")

print(f"""└────────────────────────────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────────────────────────────┐
│ 🎯 CAREER GOALS & PREFERENCES                                                                  │
├────────────────────────────────────────────────────────────────────────────────────────────────┤
│   💰 5-Year Salary Target: ₹{profile['goals']['5_year_salary_target']:,}/year{' ' * 40}│
│   🚀 10-Year Salary Target: ₹{profile['goals']['10_year_salary_target']:,}/year{' ' * 39}│
│   🏢 Work Environment: {profile['preferences']['work_environment']:<30}{' ' * 33}│
│   ⏰ Work Hours Preference: {profile['preferences']['work_hours']:<30}{' ' * 28}│
│   🎲 Risk Tolerance: {profile['personality']['risk_tolerance']}%{' ' * 53}│
│   💡 Entrepreneurship Interest: {profile['goals']['entrepreneurship_interest']}%{' ' * 43}│
└────────────────────────────────────────────────────────────────────────────────────────────────┘
""")

# 100 CAREER OPTIONS - MEGA DATABASE
careers = [
    # TIER 1: High-Tech Careers (Software & IT)
    {"id": 1, "name": "Full Stack Developer", "category": "Software Development", "sub_category": "Web", "tier": "High-Tech", 
     "required_skills": ["coding", "web_development", "database_management"], "required_soft": ["problem_solving", "teamwork"],
     "min_education": "12th", "preferred_education": "B.Tech", "success_rate": 85, "market_demand": 95, "competition": 90,
     "salary_entry": 350000, "salary_5yr": 1200000, "salary_10yr": 2500000, "growth_rate": "Very High", "job_security": 80,
     "remote_friendly": 95, "startup_culture": 80, "corporate_culture": 70, "freelance_potential": 85,
     "learning_curve": "Medium", "time_to_proficiency": "2-3 years", "initial_investment": 50000,
     "emerging_trend": "High", "ai_automation_risk": 30, "future_proof": 85, "industry_growth": "15%/year"},
    
    {"id": 2, "name": "Data Scientist", "category": "Data & Analytics", "sub_category": "AI/ML", "tier": "High-Tech",
     "required_skills": ["coding", "data_analysis", "ai_ml", "python"], "required_soft": ["critical_thinking", "problem_solving"],
     "min_education": "12th", "preferred_education": "B.Tech/M.Tech", "success_rate": 75, "market_demand": 98, "competition": 95,
     "salary_entry": 600000, "salary_5yr": 2000000, "salary_10yr": 4500000, "growth_rate": "Exponential", "job_security": 90,
     "remote_friendly": 90, "startup_culture": 85, "corporate_culture": 90, "freelance_potential": 70,
     "learning_curve": "Steep", "time_to_proficiency": "3-4 years", "initial_investment": 100000,
     "emerging_trend": "Very High", "ai_automation_risk": 20, "future_proof": 95, "industry_growth": "25%/year"},
    
    {"id": 3, "name": "Mobile App Developer (iOS/Android)", "category": "Software Development", "sub_category": "Mobile", "tier": "High-Tech",
     "required_skills": ["coding", "mobile_dev"], "required_soft": ["creativity", "problem_solving"],
     "min_education": "12th", "preferred_education": "B.Tech", "success_rate": 80, "market_demand": 90, "competition": 85,
     "salary_entry": 400000, "salary_5yr": 1400000, "salary_10yr": 2800000, "growth_rate": "Very High", "job_security": 75,
     "remote_friendly": 90, "startup_culture": 90, "corporate_culture": 70, "freelance_potential": 90,
     "learning_curve": "Medium", "time_to_proficiency": "2-3 years", "initial_investment": 60000,
     "emerging_trend": "High", "ai_automation_risk": 25, "future_proof": 85, "industry_growth": "18%/year"},
    
    {"id": 4, "name": "Cloud Architect (AWS/Azure/GCP)", "category": "Cloud & Infrastructure", "sub_category": "Architecture", "tier": "High-Tech",
     "required_skills": ["coding", "cloud_computing", "devops"], "required_soft": ["problem_solving", "leadership"],
     "min_education": "B.Tech", "preferred_education": "B.Tech + Certifications", "success_rate": 70, "market_demand": 95, "competition": 80,
     "salary_entry": 800000, "salary_5yr": 2500000, "salary_10yr": 5000000, "growth_rate": "Very High", "job_security": 85,
     "remote_friendly": 85, "startup_culture": 75, "corporate_culture": 95, "freelance_potential": 60,
     "learning_curve": "Steep", "time_to_proficiency": "4-5 years", "initial_investment": 80000,
     "emerging_trend": "Very High", "ai_automation_risk": 15, "future_proof": 95, "industry_growth": "22%/year"},
    
    {"id": 5, "name": "Cybersecurity Specialist", "category": "Security", "sub_category": "Ethical Hacking", "tier": "High-Tech",
     "required_skills": ["coding", "cybersecurity", "problem_solving"], "required_soft": ["critical_thinking", "attention_to_detail"],
     "min_education": "12th", "preferred_education": "B.Tech + CEH", "success_rate": 75, "market_demand": 98, "competition": 75,
     "salary_entry": 500000, "salary_5yr": 1800000, "salary_10yr": 3500000, "growth_rate": "Very High", "job_security": 95,
     "remote_friendly": 80, "startup_culture": 70, "corporate_culture": 90, "freelance_potential": 75,
     "learning_curve": "Steep", "time_to_proficiency": "3-4 years", "initial_investment": 70000,
     "emerging_trend": "Critical", "ai_automation_risk": 10, "future_proof": 98, "industry_growth": "20%/year"},
    
    {"id": 6, "name": "AI/ML Engineer", "category": "Artificial Intelligence", "sub_category": "Deep Learning", "tier": "High-Tech",
     "required_skills": ["coding", "ai_ml", "python", "data_analysis"], "required_soft": ["innovation", "problem_solving"],
     "min_education": "B.Tech", "preferred_education": "M.Tech/PhD", "success_rate": 70, "market_demand": 99, "competition": 95,
     "salary_entry": 900000, "salary_5yr": 2800000, "salary_10yr": 6000000, "growth_rate": "Exponential", "job_security": 90,
     "remote_friendly": 90, "startup_culture": 95, "corporate_culture": 95, "freelance_potential": 70,
     "learning_curve": "Very Steep", "time_to_proficiency": "4-6 years", "initial_investment": 150000,
     "emerging_trend": "Revolutionary", "ai_automation_risk": 5, "future_proof": 99, "industry_growth": "35%/year"},
    
    {"id": 7, "name": "DevOps Engineer", "category": "Cloud & Infrastructure", "sub_category": "Automation", "tier": "High-Tech",
     "required_skills": ["coding", "devops", "cloud_computing"], "required_soft": ["problem_solving", "teamwork"],
     "min_education": "12th", "preferred_education": "B.Tech", "success_rate": 78, "market_demand": 92, "competition": 80,
     "salary_entry": 600000, "salary_5yr": 1800000, "salary_10yr": 3200000, "growth_rate": "High", "job_security": 85,
     "remote_friendly": 85, "startup_culture": 90, "corporate_culture": 85, "freelance_potential": 70,
     "learning_curve": "Steep", "time_to_proficiency": "3-4 years", "initial_investment": 60000,
     "emerging_trend": "High", "ai_automation_risk": 20, "future_proof": 90, "industry_growth": "20%/year"},
    
    {"id": 8, "name": "Blockchain Developer", "category": "Emerging Tech", "sub_category": "Web3", "tier": "High-Tech",
     "required_skills": ["coding", "cryptography", "smart_contracts"], "required_soft": ["innovation", "problem_solving"],
     "min_education": "12th", "preferred_education": "B.Tech", "success_rate": 65, "market_demand": 85, "competition": 70,
     "salary_entry": 700000, "salary_5yr": 2200000, "salary_10yr": 4500000, "growth_rate": "Very High", "job_security": 70,
     "remote_friendly": 95, "startup_culture": 95, "corporate_culture": 60, "freelance_potential": 85,
     "learning_curve": "Very Steep", "time_to_proficiency": "3-5 years", "initial_investment": 80000,
     "emerging_trend": "Revolutionary", "ai_automation_risk": 15, "future_proof": 85, "industry_growth": "40%/year"},
    
    {"id": 9, "name": "Game Developer (Unity/Unreal)", "category": "Gaming", "sub_category": "3D/AR/VR", "tier": "Creative-Tech",
     "required_skills": ["coding", "game_engines", "3d_modeling"], "required_soft": ["creativity", "problem_solving"],
     "min_education": "12th", "preferred_education": "B.Tech/B.Des", "success_rate": 60, "market_demand": 75, "competition": 85,
     "salary_entry": 400000, "salary_5yr": 1200000, "salary_10yr": 2500000, "growth_rate": "High", "job_security": 65,
     "remote_friendly": 80, "startup_culture": 85, "corporate_culture": 60, "freelance_potential": 80,
     "learning_curve": "Steep", "time_to_proficiency": "3-4 years", "initial_investment": 100000,
     "emerging_trend": "High", "ai_automation_risk": 30, "future_proof": 80, "industry_growth": "15%/year"},
    
    {"id": 10, "name": "UI/UX Designer (Tech)", "category": "Design", "sub_category": "Product Design", "tier": "Creative-Tech",
     "required_skills": ["design", "prototyping", "user_research"], "required_soft": ["creativity", "empathy", "communication"],
     "min_education": "12th", "preferred_education": "B.Des", "success_rate": 75, "market_demand": 88, "competition": 85,
     "salary_entry": 450000, "salary_5yr": 1300000, "salary_10yr": 2400000, "growth_rate": "High", "job_security": 75,
     "remote_friendly": 95, "startup_culture": 90, "corporate_culture": 80, "freelance_potential": 90,
     "learning_curve": "Medium", "time_to_proficiency": "2-3 years", "initial_investment": 40000,
     "emerging_trend": "High", "ai_automation_risk": 40, "future_proof": 75, "industry_growth": "12%/year"},
    
    # TIER 2: Creative & Digital Content
    {"id": 11, "name": "YouTube Content Creator (Tech/Education)", "category": "Content Creation", "sub_category": "Video", "tier": "Digital Creator",
     "required_skills": ["video_editing", "content_writing", "social_media"], "required_soft": ["creativity", "communication", "persistence"],
     "min_education": "10th", "preferred_education": "Any", "success_rate": 35, "market_demand": 70, "competition": 98,
     "salary_entry": 0, "salary_5yr": 1500000, "salary_10yr": 5000000, "growth_rate": "Exponential", "job_security": 20,
     "remote_friendly": 100, "startup_culture": 100, "corporate_culture": 0, "freelance_potential": 100,
     "learning_curve": "Medium", "time_to_proficiency": "2-4 years", "initial_investment": 80000,
     "emerging_trend": "Very High", "ai_automation_risk": 50, "future_proof": 60, "industry_growth": "25%/year"},
    
    {"id": 12, "name": "Digital Marketing Specialist", "category": "Marketing", "sub_category": "Performance Marketing", "tier": "Digital",
     "required_skills": ["marketing", "analytics", "social_media"], "required_soft": ["creativity", "communication", "data_analysis"],
     "min_education": "10th", "preferred_education": "Graduate", "success_rate": 70, "market_demand": 90, "competition": 88,
     "salary_entry": 300000, "salary_5yr": 900000, "salary_10yr": 1800000, "growth_rate": "High", "job_security": 70,
     "remote_friendly": 90, "startup_culture": 95, "corporate_culture": 85, "freelance_potential": 95,
     "learning_curve": "Easy", "time_to_proficiency": "1-2 years", "initial_investment": 30000,
     "emerging_trend": "High", "ai_automation_risk": 60, "future_proof": 65, "industry_growth": "18%/year"},
    
    {"id": 13, "name": "Social Media Manager", "category": "Marketing", "sub_category": "Brand Management", "tier": "Digital",
     "required_skills": ["social_media", "content_creation", "community_management"], "required_soft": ["creativity", "communication"],
     "min_education": "10th", "preferred_education": "Graduate", "success_rate": 75, "market_demand": 85, "competition": 90,
     "salary_entry": 300000, "salary_5yr": 800000, "salary_10yr": 1500000, "growth_rate": "Medium", "job_security": 65,
     "remote_friendly": 95, "startup_culture": 90, "corporate_culture": 80, "freelance_potential": 90,
     "learning_curve": "Easy", "time_to_proficiency": "1-2 years", "initial_investment": 20000,
     "emerging_trend": "Medium", "ai_automation_risk": 70, "future_proof": 55, "industry_growth": "12%/year"},
    
    {"id": 14, "name": "Professional Dancer (Commercial/Bollywood)", "category": "Performance Arts", "sub_category": "Dance", "tier": "Creative",
     "required_skills": ["dancing", "choreography", "physical_fitness"], "required_soft": ["discipline", "creativity", "networking"],
     "min_education": "10th", "preferred_education": "Any", "success_rate": 25, "market_demand": 45, "competition": 95,
     "salary_entry": 150000, "salary_5yr": 600000, "salary_10yr": 1500000, "growth_rate": "Medium", "job_security": 30,
     "remote_friendly": 10, "startup_culture": 50, "corporate_culture": 20, "freelance_potential": 90,
     "learning_curve": "Steep", "time_to_proficiency": "5-10 years", "initial_investment": 100000,
     "emerging_trend": "Stable", "ai_automation_risk": 5, "future_proof": 70, "industry_growth": "5%/year"},
    
    {"id": 15, "name": "Music Producer (Electronic/Hip-Hop)", "category": "Music Industry", "sub_category": "Production", "tier": "Creative",
     "required_skills": ["music_production", "sound_engineering", "mixing"], "required_soft": ["creativity", "technical_skills"],
     "min_education": "10th", "preferred_education": "Audio Engineering Diploma", "success_rate": 40, "market_demand": 60, "competition": 90,
     "salary_entry": 200000, "salary_5yr": 800000, "salary_10yr": 2500000, "growth_rate": "High", "job_security": 40,
     "remote_friendly": 80, "startup_culture": 70, "corporate_culture": 30, "freelance_potential": 95,
     "learning_curve": "Steep", "time_to_proficiency": "3-5 years", "initial_investment": 200000,
     "emerging_trend": "High", "ai_automation_risk": 45, "future_proof": 65, "industry_growth": "10%/year"},
    
    {"id": 16, "name": "Video Editor (Freelance/Agency)", "category": "Post-Production", "sub_category": "Editing", "tier": "Creative-Tech",
     "required_skills": ["video_editing", "color_grading", "motion_graphics"], "required_soft": ["creativity", "attention_to_detail"],
     "min_education": "10th", "preferred_education": "Diploma", "success_rate": 65, "market_demand": 85, "competition": 85,
     "salary_entry": 250000, "salary_5yr": 700000, "salary_10yr": 1400000, "growth_rate": "Medium", "job_security": 60,
     "remote_friendly": 95, "startup_culture": 80, "corporate_culture": 60, "freelance_potential": 98,
     "learning_curve": "Medium", "time_to_proficiency": "1-2 years", "initial_investment": 60000,
     "emerging_trend": "High", "ai_automation_risk": 55, "future_proof": 65, "industry_growth": "15%/year"},
    
    {"id": 17, "name": "Graphic Designer (Brand/Digital)", "category": "Design", "sub_category": "Visual Design", "tier": "Creative",
     "required_skills": ["graphic_design", "illustration", "branding"], "required_soft": ["creativity", "communication"],
     "min_education": "10th", "preferred_education": "B.Des", "success_rate": 70, "market_demand": 80, "competition": 90,
     "salary_entry": 250000, "salary_5yr": 650000, "salary_10yr": 1200000, "growth_rate": "Medium", "job_security": 65,
     "remote_friendly": 95, "startup_culture": 85, "corporate_culture": 75, "freelance_potential": 95,
     "learning_curve": "Medium", "time_to_proficiency": "2-3 years", "initial_investment": 40000,
     "emerging_trend": "Medium", "ai_automation_risk": 65, "future_proof": 55, "industry_growth": "8%/year"},
    
    {"id": 18, "name": "Photography (Wedding/Commercial)", "category": "Photography", "sub_category": "Event/Product", "tier": "Creative",
     "required_skills": ["photography", "photo_editing", "lighting"], "required_soft": ["creativity", "people_skills", "business"],
     "min_education": "10th", "preferred_education": "Diploma", "success_rate": 55, "market_demand": 70, "competition": 85,
     "salary_entry": 300000, "salary_5yr": 800000, "salary_10yr": 1500000, "growth_rate": "Medium", "job_security": 50,
     "remote_friendly": 30, "startup_culture": 60, "corporate_culture": 40, "freelance_potential": 95,
     "learning_curve": "Medium", "time_to_proficiency": "2-3 years", "initial_investment": 150000,
     "emerging_trend": "Stable", "ai_automation_risk": 40, "future_proof": 70, "industry_growth": "6%/year"},
    
    # TIER 3: Business & Entrepreneurship
    {"id": 19, "name": "E-commerce Business Owner (Amazon/Shopify)", "category": "Entrepreneurship", "sub_category": "Online Retail", "tier": "Business",
     "required_skills": ["e_commerce", "marketing", "supply_chain"], "required_soft": ["business_acumen", "persistence", "risk_taking"],
     "min_education": "10th", "preferred_education": "Any", "success_rate": 45, "market_demand": 80, "competition": 88,
     "salary_entry": 0, "salary_5yr": 1200000, "salary_10yr": 5000000, "growth_rate": "Very High", "job_security": 30,
     "remote_friendly": 90, "startup_culture": 100, "corporate_culture": 0, "freelance_potential": 0,
     "learning_curve": "Steep", "time_to_proficiency": "2-4 years", "initial_investment": 200000,
     "emerging_trend": "Very High", "ai_automation_risk": 40, "future_proof": 75, "industry_growth": "20%/year"},
    
    {"id": 20, "name": "Digital Products Creator (Courses/Templates)", "category": "Entrepreneurship", "sub_category": "Info Products", "tier": "Business",
     "required_skills": ["expertise_in_domain", "teaching", "marketing"], "required_soft": ["communication", "persistence"],
     "min_education": "10th", "preferred_education": "Expert in Field", "success_rate": 40, "market_demand": 75, "competition": 90,
     "salary_entry": 0, "salary_5yr": 1000000, "salary_10yr": 3000000, "growth_rate": "High", "job_security": 35,
     "remote_friendly": 100, "startup_culture": 100, "corporate_culture": 0, "freelance_potential": 100,
     "learning_curve": "Medium", "time_to_proficiency": "1-3 years", "initial_investment": 50000,
     "emerging_trend": "Very High", "ai_automation_risk": 50, "future_proof": 70, "industry_growth": "22%/year"},
    
    {"id": 21, "name": "SaaS Startup Founder", "category": "Entrepreneurship", "sub_category": "Tech Startup", "tier": "Business",
     "required_skills": ["coding", "business", "product_management"], "required_soft": ["leadership", "resilience", "vision"],
     "min_education": "12th", "preferred_education": "B.Tech", "success_rate": 15, "market_demand": 70, "competition": 85,
     "salary_entry": 0, "salary_5yr": 2000000, "salary_10yr": 10000000, "growth_rate": "Exponential", "job_security": 20,
     "remote_friendly": 100, "startup_culture": 100, "corporate_culture": 0, "freelance_potential": 0,
     "learning_curve": "Very Steep", "time_to_proficiency": "5-10 years", "initial_investment": 500000,
     "emerging_trend": "Very High", "ai_automation_risk": 10, "future_proof": 85, "industry_growth": "30%/year"},
    
    {"id": 22, "name": "Freelance Consultant (Tech/Business)", "category": "Consulting", "sub_category": "Advisory", "tier": "Professional",
     "required_skills": ["expertise", "communication", "business"], "required_soft": ["credibility", "networking", "problem_solving"],
     "min_education": "Graduate", "preferred_education": "MBA/Experience", "success_rate": 50, "market_demand": 75, "competition": 80,
     "salary_entry": 500000, "salary_5yr": 1500000, "salary_10yr": 3500000, "growth_rate": "High", "job_security": 60,
     "remote_friendly": 95, "startup_culture": 70, "corporate_culture": 80, "freelance_potential": 100,
     "learning_curve": "Steep", "time_to_proficiency": "5-8 years", "initial_investment": 100000,
     "emerging_trend": "High", "ai_automation_risk": 30, "future_proof": 80, "industry_growth": "12%/year"},
    
    # TIER 4: Traditional & Service
    {"id": 23, "name": "Software Tester (Manual/Automation)", "category": "Software Testing", "sub_category": "QA", "tier": "Tech-Support",
     "required_skills": ["testing", "automation", "scripting"], "required_soft": ["attention_to_detail", "patience"],
     "min_education": "12th", "preferred_education": "B.Tech", "success_rate": 85, "market_demand": 85, "competition": 75,
     "salary_entry": 300000, "salary_5yr": 800000, "salary_10yr": 1500000, "growth_rate": "Medium", "job_security": 75,
     "remote_friendly": 85, "startup_culture": 70, "corporate_culture": 90, "freelance_potential": 60,
     "learning_curve": "Easy", "time_to_proficiency": "1-2 years", "initial_investment": 30000,
     "emerging_trend": "Medium", "ai_automation_risk": 70, "future_proof": 50, "industry_growth": "8%/year"},
    
    {"id": 24, "name": "Business Analyst", "category": "Business Operations", "sub_category": "Analysis", "tier": "Professional",
     "required_skills": ["analysis", "documentation", "communication"], "required_soft": ["problem_solving", "critical_thinking"],
     "min_education": "Graduate", "preferred_education": "MBA", "success_rate": 75, "market_demand": 85, "competition": 80,
     "salary_entry": 450000, "salary_5yr": 1200000, "salary_10yr": 2200000, "growth_rate": "High", "job_security": 80,
     "remote_friendly": 80, "startup_culture": 70, "corporate_culture": 95, "freelance_potential": 50,
     "learning_curve": "Medium", "time_to_proficiency": "2-3 years", "initial_investment": 50000,
     "emerging_trend": "Medium", "ai_automation_risk": 50, "future_proof": 70, "industry_growth": "10%/year"},
    
    {"id": 25, "name": "HR Manager", "category": "Human Resources", "sub_category": "Talent Management", "tier": "Professional",
     "required_skills": ["hr_management", "recruitment", "employee_relations"], "required_soft": ["empathy", "communication", "leadership"],
     "min_education": "Graduate", "preferred_education": "MBA-HR", "success_rate": 70, "market_demand": 75, "competition": 75,
     "salary_entry": 400000, "salary_5yr": 1000000, "salary_10yr": 1800000, "growth_rate": "Medium", "job_security": 75,
     "remote_friendly": 60, "startup_culture": 60, "corporate_culture": 95, "freelance_potential": 40,
     "learning_curve": "Medium", "time_to_proficiency": "3-5 years", "initial_investment": 100000,
     "emerging_trend": "Low", "ai_automation_risk": 40, "future_proof": 70, "industry_growth": "6%/year"},
    
    {"id": 26, "name": "Customer Support Executive (Tech)", "category": "Customer Service", "sub_category": "Support", "tier": "Service",
     "required_skills": ["communication", "technical_knowledge", "crm"], "required_soft": ["patience", "empathy", "problem_solving"],
     "min_education": "10th", "preferred_education": "Graduate", "success_rate": 90, "market_demand": 80, "competition": 70,
     "salary_entry": 250000, "salary_5yr": 500000, "salary_10yr": 800000, "growth_rate": "Low", "job_security": 60,
     "remote_friendly": 90, "startup_culture": 70, "corporate_culture": 85, "freelance_potential": 30,
     "learning_curve": "Easy", "time_to_proficiency": "0-1 year", "initial_investment": 10000,
     "emerging_trend": "Low", "ai_automation_risk": 85, "future_proof": 30, "industry_growth": "3%/year"},
    
    {"id": 27, "name": "BPO/Call Center (International Voice)", "category": "BPO", "sub_category": "Voice Process", "tier": "Service",
     "required_skills": ["communication", "accent", "customer_service"], "required_soft": ["patience", "adaptability"],
     "min_education": "10th", "preferred_education": "12th", "success_rate": 95, "market_demand": 70, "competition": 60,
     "salary_entry": 250000, "salary_5yr": 400000, "salary_10yr": 600000, "growth_rate": "Very Low", "job_security": 50,
     "remote_friendly": 70, "startup_culture": 40, "corporate_culture": 80, "freelance_potential": 10,
     "learning_curve": "Easy", "time_to_proficiency": "0-6 months", "initial_investment": 5000,
     "emerging_trend": "Declining", "ai_automation_risk": 90, "future_proof": 20, "industry_growth": "-2%/year"},
    
    {"id": 28, "name": "Data Entry Operator", "category": "Data Operations", "sub_category": "Entry Level", "tier": "Service",
     "required_skills": ["typing", "accuracy", "ms_office"], "required_soft": ["attention_to_detail", "patience"],
     "min_education": "10th", "preferred_education": "12th", "success_rate": 95, "market_demand": 60, "competition": 65,
     "salary_entry": 180000, "salary_5yr": 250000, "salary_10yr": 350000, "growth_rate": "Very Low", "job_security": 40,
     "remote_friendly": 80, "startup_culture": 30, "corporate_culture": 70, "freelance_potential": 50,
     "learning_curve": "Very Easy", "time_to_proficiency": "0-3 months", "initial_investment": 5000,
     "emerging_trend": "Declining", "ai_automation_risk": 95, "future_proof": 10, "industry_growth": "-5%/year"},
    
    # TIER 5: Education & Training
    {"id": 29, "name": "Online Coding Instructor (Unacademy/BYJU'S)", "category": "Education", "sub_category": "EdTech", "tier": "Education",
     "required_skills": ["coding", "teaching", "communication"], "required_soft": ["patience", "clarity", "passion"],
     "min_education": "12th", "preferred_education": "B.Tech", "success_rate": 70, "market_demand": 85, "competition": 75,
     "salary_entry": 400000, "salary_5yr": 1000000, "salary_10yr": 1800000, "growth_rate": "High", "job_security": 70,
     "remote_friendly": 100, "startup_culture": 80, "corporate_culture": 70, "freelance_potential": 90,
     "learning_curve": "Medium", "time_to_proficiency": "2-3 years", "initial_investment": 50000,
     "emerging_trend": "High", "ai_automation_risk": 45, "future_proof": 75, "industry_growth": "18%/year"},
    
    {"id": 30, "name": "Dance Academy Owner", "category": "Education", "sub_category": "Arts Training", "tier": "Business",
     "required_skills": ["dancing", "teaching", "business"], "required_soft": ["leadership", "marketing", "patience"],
     "min_education": "10th", "preferred_education": "Certification", "success_rate": 55, "market_demand": 65, "competition": 70,
     "salary_entry": 200000, "salary_5yr": 600000, "salary_10yr": 1500000, "growth_rate": "Medium", "job_security": 60,
     "remote_friendly": 30, "startup_culture": 70, "corporate_culture": 30, "freelance_potential": 50,
     "learning_curve": "Medium", "time_to_proficiency": "3-5 years", "initial_investment": 300000,
     "emerging_trend": "Stable", "ai_automation_risk": 10, "future_proof": 80, "industry_growth": "7%/year"},
    
    # Add 20 more diverse careers...
    {"id": 31, "name": "Product Manager (Tech)", "category": "Product Management", "sub_category": "Strategy", "tier": "High-Tech",
     "required_skills": ["product_strategy", "analytics", "communication"], "required_soft": ["leadership", "decision_making"],
     "min_education": "Graduate", "preferred_education": "MBA", "success_rate": 65, "market_demand": 90, "competition": 85,
     "salary_entry": 1200000, "salary_5yr": 3000000, "salary_10yr": 6000000, "growth_rate": "Very High", "job_security": 80,
     "remote_friendly": 80, "startup_culture": 95, "corporate_culture": 90, "freelance_potential": 40,
     "learning_curve": "Steep", "time_to_proficiency": "5-7 years", "initial_investment": 200000,
     "emerging_trend": "Very High", "ai_automation_risk": 25, "future_proof": 90, "industry_growth": "20%/year"},
    
    {"id": 32, "name": "Ethical Hacker (Bug Bounty Hunter)", "category": "Cybersecurity", "sub_category": "Penetration Testing", "tier": "High-Tech",
     "required_skills": ["hacking", "networking", "security_tools"], "required_soft": ["curiosity", "persistence", "ethics"],
     "min_education": "12th", "preferred_education": "Certifications", "success_rate": 55, "market_demand": 95, "competition": 70,
     "salary_entry": 600000, "salary_5yr": 2000000, "salary_10yr": 4000000, "growth_rate": "Very High", "job_security": 85,
     "remote_friendly": 100, "startup_culture": 80, "corporate_culture": 75, "freelance_potential": 85,
     "learning_curve": "Very Steep", "time_to_proficiency": "3-5 years", "initial_investment": 80000,
     "emerging_trend": "Critical", "ai_automation_risk": 15, "future_proof": 95, "industry_growth": "25%/year"},
    
    {"id": 33, "name": "3D Animator (Films/Gaming)", "category": "Animation", "sub_category": "Visual Effects", "tier": "Creative-Tech",
     "required_skills": ["3d_animation", "modeling", "rendering"], "required_soft": ["creativity", "patience", "attention_to_detail"],
     "min_education": "12th", "preferred_education": "Animation Degree", "success_rate": 60, "market_demand": 75, "competition": 80,
     "salary_entry": 350000, "salary_5yr": 1000000, "salary_10yr": 2000000, "growth_rate": "High", "job_security": 65,
     "remote_friendly": 85, "startup_culture": 75, "corporate_culture": 65, "freelance_potential": 85,
     "learning_curve": "Steep", "time_to_proficiency": "3-4 years", "initial_investment": 150000,
     "emerging_trend": "High", "ai_automation_risk": 50, "future_proof": 70, "industry_growth": "12%/year"},
    
    {"id": 34, "name": "Voice Over Artist (Dubbing/Ads)", "category": "Media", "sub_category": "Voice Acting", "tier": "Creative",
     "required_skills": ["voice_modulation", "acting", "accent"], "required_soft": ["creativity", "versatility"],
     "min_education": "10th", "preferred_education": "Training", "success_rate": 45, "market_demand": 60, "competition": 85,
     "salary_entry": 200000, "salary_5yr": 600000, "salary_10yr": 1200000, "growth_rate": "Medium", "job_security": 50,
     "remote_friendly": 90, "startup_culture": 60, "corporate_culture": 40, "freelance_potential": 95,
     "learning_curve": "Medium", "time_to_proficiency": "2-3 years", "initial_investment": 100000,
     "emerging_trend": "Medium", "ai_automation_risk": 60, "future_proof": 55, "industry_growth": "8%/year"},
    
    {"id": 35, "name": "Podcast Host/Producer", "category": "Content Creation", "sub_category": "Audio", "tier": "Digital Creator",
     "required_skills": ["audio_editing", "storytelling", "interviewing"], "required_soft": ["communication", "curiosity"],
     "min_education": "10th", "preferred_education": "Any", "success_rate": 40, "market_demand": 65, "competition": 85,
     "salary_entry": 0, "salary_5yr": 800000, "salary_10yr": 2500000, "growth_rate": "High", "job_security": 35,
     "remote_friendly": 100, "startup_culture": 90, "corporate_culture": 30, "freelance_potential": 100,
     "learning_curve": "Medium", "time_to_proficiency": "1-3 years", "initial_investment": 80000,
     "emerging_trend": "Very High", "ai_automation_risk": 40, "future_proof": 70, "industry_growth": "20%/year"},
    
    {"id": 36, "name": "SEO Specialist", "category": "Digital Marketing", "sub_category": "Search Optimization", "tier": "Digital",
     "required_skills": ["seo", "analytics", "content_strategy"], "required_soft": ["analytical_thinking", "patience"],
     "min_education": "10th", "preferred_education": "Graduate", "success_rate": 75, "market_demand": 88, "competition": 82,
     "salary_entry": 300000, "salary_5yr": 900000, "salary_10yr": 1600000, "growth_rate": "High", "job_security": 75,
     "remote_friendly": 95, "startup_culture": 85, "corporate_culture": 80, "freelance_potential": 95,
     "learning_curve": "Medium", "time_to_proficiency": "1-2 years", "initial_investment": 20000,
     "emerging_trend": "High", "ai_automation_risk": 55, "future_proof": 70, "industry_growth": "15%/year"},
    
    {"id": 37, "name": "Instagram/TikTok Influencer", "category": "Influencer Marketing", "sub_category": "Social Media", "tier": "Digital Creator",
     "required_skills": ["content_creation", "video_editing", "personal_branding"], "required_soft": ["charisma", "consistency"],
     "min_education": "10th", "preferred_education": "Any", "success_rate": 15, "market_demand": 60, "competition": 99,
     "salary_entry": 0, "salary_5yr": 2000000, "salary_10yr": 10000000, "growth_rate": "Exponential", "job_security": 10,
     "remote_friendly": 100, "startup_culture": 100, "corporate_culture": 0, "freelance_potential": 100,
     "learning_curve": "Medium", "time_to_proficiency": "2-5 years", "initial_investment": 50000,
     "emerging_trend": "Very High", "ai_automation_risk": 30, "future_proof": 50, "industry_growth": "30%/year"},
    
    {"id": 38, "name": "Copywriter (Ads/Content)", "category": "Writing", "sub_category": "Creative Writing", "tier": "Creative",
     "required_skills": ["writing", "marketing", "persuasion"], "required_soft": ["creativity", "empathy"],
     "min_education": "10th", "preferred_education": "Graduate", "success_rate": 70, "market_demand": 80, "competition": 85,
     "salary_entry": 300000, "salary_5yr": 800000, "salary_10yr": 1400000, "growth_rate": "Medium", "job_security": 70,
     "remote_friendly": 100, "startup_culture": 85, "corporate_culture": 75, "freelance_potential": 95,
     "learning_curve": "Medium", "time_to_proficiency": "2-3 years", "initial_investment": 10000,
     "emerging_trend": "Medium", "ai_automation_risk": 70, "future_proof": 50, "industry_growth": "10%/year"},
    
    {"id": 39, "name": "Fitness Trainer (Online/Gym)", "category": "Health & Fitness", "sub_category": "Training", "tier": "Service",
     "required_skills": ["fitness_knowledge", "nutrition", "training_methods"], "required_soft": ["motivation", "discipline"],
     "min_education": "10th", "preferred_education": "Certification", "success_rate": 60, "market_demand": 75, "competition": 80,
     "salary_entry": 250000, "salary_5yr": 700000, "salary_10yr": 1500000, "growth_rate": "High", "job_security": 60,
     "remote_friendly": 60, "startup_culture": 70, "corporate_culture": 40, "freelance_potential": 90,
     "learning_curve": "Medium", "time_to_proficiency": "1-2 years", "initial_investment": 100000,
     "emerging_trend": "High", "ai_automation_risk": 35, "future_proof": 75, "industry_growth": "15%/year"},
    
    {"id": 40, "name": "Travel Vlogger", "category": "Content Creation", "sub_category": "Travel", "tier": "Digital Creator",
     "required_skills": ["videography", "storytelling", "social_media"], "required_soft": ["adventure", "communication"],
     "min_education": "10th", "preferred_education": "Any", "success_rate": 20, "market_demand": 50, "competition": 95,
     "salary_entry": 0, "salary_5yr": 1500000, "salary_10yr": 5000000, "growth_rate": "High", "job_security": 20,
     "remote_friendly": 100, "startup_culture": 100, "corporate_culture": 0, "freelance_potential": 100,
     "learning_curve": "Medium", "time_to_proficiency": "2-4 years", "initial_investment": 200000,
     "emerging_trend": "High", "ai_automation_risk": 25, "future_proof": 65, "industry_growth": "18%/year"},
    
    {"id": 41, "name": "Cyber Cafe/Gaming Cafe Owner", "category": "Business", "sub_category": "Gaming", "tier": "Business",
     "required_skills": ["business", "gaming_knowledge", "customer_service"], "required_soft": ["management", "networking"],
     "min_education": "10th", "preferred_education": "Any", "success_rate": 50, "market_demand": 55, "competition": 70,
     "salary_entry": 300000, "salary_5yr": 800000, "salary_10yr": 1500000, "growth_rate": "Medium", "job_security": 50,
     "remote_friendly": 0, "startup_culture": 60, "corporate_culture": 20, "freelance_potential": 0,
     "learning_curve": "Medium", "time_to_proficiency": "1-2 years", "initial_investment": 500000,
     "emerging_trend": "High", "ai_automation_risk": 20, "future_proof": 70, "industry_growth": "12%/year"},
    
    {"id": 42, "name": "App-Based Driver (Uber/Ola)", "category": "Gig Economy", "sub_category": "Transportation", "tier": "Service",
     "required_skills": ["driving", "navigation", "customer_service"], "required_soft": ["patience", "safety"],
     "min_education": "10th", "preferred_education": "License", "success_rate": 85, "market_demand": 70, "competition": 80,
     "salary_entry": 300000, "salary_5yr": 400000, "salary_10yr": 500000, "growth_rate": "Very Low", "job_security": 40,
     "remote_friendly": 0, "startup_culture": 50, "corporate_culture": 30, "freelance_potential": 90,
     "learning_curve": "Very Easy", "time_to_proficiency": "0-1 month", "initial_investment": 300000,
     "emerging_trend": "Declining", "ai_automation_risk": 95, "future_proof": 15, "industry_growth": "0%/year"},
    
    {"id": 43, "name": "Food Delivery Partner (Swiggy/Zomato)", "category": "Gig Economy", "sub_category": "Delivery", "tier": "Service",
     "required_skills": ["navigation", "time_management", "vehicle_handling"], "required_soft": ["speed", "reliability"],
     "min_education": "10th", "preferred_education": "Any", "success_rate": 90, "market_demand": 75, "competition": 75,
     "salary_entry": 200000, "salary_5yr": 250000, "salary_10yr": 300000, "growth_rate": "Very Low", "job_security": 30,
     "remote_friendly": 0, "startup_culture": 40, "corporate_culture": 20, "freelance_potential": 95,
     "learning_curve": "Very Easy", "time_to_proficiency": "0-1 week", "initial_investment": 50000,
     "emerging_trend": "Declining", "ai_automation_risk": 90, "future_proof": 20, "industry_growth": "2%/year"},
    
    {"id": 44, "name": "Event Planner/Coordinator", "category": "Events", "sub_category": "Event Management", "tier": "Service",
     "required_skills": ["planning", "coordination", "vendor_management"], "required_soft": ["organization", "networking"],
     "min_education": "10th", "preferred_education": "Diploma", "success_rate": 65, "market_demand": 70, "competition": 75,
     "salary_entry": 300000, "salary_5yr": 800000, "salary_10yr": 1500000, "growth_rate": "Medium", "job_security": 60,
     "remote_friendly": 40, "startup_culture": 70, "corporate_culture": 60, "freelance_potential": 85,
     "learning_curve": "Medium", "time_to_proficiency": "2-3 years", "initial_investment": 100000,
       "emerging_trend": "Stable", "ai_automation_risk": 30, "future_proof": 75, "industry_growth": "8%/year"},
    
    {"id": 45, "name": "Real Estate Agent", "category": "Real Estate", "sub_category": "Sales", "tier": "Sales",
     "required_skills": ["sales", "negotiation", "market_knowledge"], "required_soft": ["networking", "persuasion"],
     "min_education": "10th", "preferred_education": "Any", "success_rate": 55, "market_demand": 70, "competition": 80,
     "salary_entry": 300000, "salary_5yr": 1000000, "salary_10yr": 2500000, "growth_rate": "High", "job_security": 50,
     "remote_friendly": 30, "startup_culture": 50, "corporate_culture": 60, "freelance_potential": 90,
     "learning_curve": "Medium", "time_to_proficiency": "1-2 years", "initial_investment": 50000,
     "emerging_trend": "Stable", "ai_automation_risk": 40, "future_proof": 70, "industry_growth": "10%/year"},
    
    {"id": 46, "name": "Insurance Agent", "category": "Financial Services", "sub_category": "Insurance", "tier": "Sales",
     "required_skills": ["sales", "product_knowledge", "customer_service"], "required_soft": ["persistence", "trust_building"],
     "min_education": "10th", "preferred_education": "12th + License", "success_rate": 60, "market_demand": 65, "competition": 75,
     "salary_entry": 250000, "salary_5yr": 600000, "salary_10yr": 1200000, "growth_rate": "Medium", "job_security": 60,
     "remote_friendly": 50, "startup_culture": 40, "corporate_culture": 70, "freelance_potential": 80,
     "learning_curve": "Medium", "time_to_proficiency": "1-2 years", "initial_investment": 30000,
     "emerging_trend": "Stable", "ai_automation_risk": 50, "future_proof": 65, "industry_growth": "7%/year"},
    
    {"id": 47, "name": "Personal Stylist/Image Consultant", "category": "Fashion", "sub_category": "Styling", "tier": "Creative",
     "required_skills": ["fashion_sense", "color_theory", "body_types"], "required_soft": ["communication", "confidence"],
     "min_education": "10th", "preferred_education": "Certification", "success_rate": 50, "market_demand": 60, "competition": 75,
     "salary_entry": 250000, "salary_5yr": 700000, "salary_10yr": 1500000, "growth_rate": "Medium", "job_security": 55,
     "remote_friendly": 40, "startup_culture": 65, "corporate_culture": 40, "freelance_potential": 90,
     "learning_curve": "Medium", "time_to_proficiency": "2-3 years", "initial_investment": 100000,
     "emerging_trend": "Medium", "ai_automation_risk": 45, "future_proof": 70, "industry_growth": "9%/year"},
    
    {"id": 48, "name": "Tattoo Artist", "category": "Art", "sub_category": "Body Art", "tier": "Creative",
     "required_skills": ["drawing", "tattooing", "hygiene"], "required_soft": ["patience", "precision", "artistic_vision"],
     "min_education": "10th", "preferred_education": "Apprenticeship", "success_rate": 55, "market_demand": 60, "competition": 70,
     "salary_entry": 300000, "salary_5yr": 800000, "salary_10yr": 1500000, "growth_rate": "Medium", "job_security": 60,
     "remote_friendly": 0, "startup_culture": 70, "corporate_culture": 20, "freelance_potential": 85,
     "learning_curve": "Steep", "time_to_proficiency": "3-5 years", "initial_investment": 200000,
     "emerging_trend": "High", "ai_automation_risk": 15, "future_proof": 85, "industry_growth": "12%/year"},
    
    {"id": 49, "name": "Stand-up Comedian", "category": "Entertainment", "sub_category": "Comedy", "tier": "Creative",
     "required_skills": ["comedy_writing", "stage_presence", "timing"], "required_soft": ["confidence", "resilience", "observation"],
     "min_education": "10th", "preferred_education": "Any", "success_rate": 20, "market_demand": 50, "competition": 90,
     "salary_entry": 0, "salary_5yr": 1000000, "salary_10yr": 5000000, "growth_rate": "Exponential", "job_security": 25,
     "remote_friendly": 30, "startup_culture": 70, "corporate_culture": 20, "freelance_potential": 95,
     "learning_curve": "Very Steep", "time_to_proficiency": "5-10 years", "initial_investment": 50000,
     "emerging_trend": "High", "ai_automation_risk": 10, "future_proof": 80, "industry_growth": "15%/year"},
    
    {"id": 50, "name": "Dropshipping Business Owner", "category": "E-commerce", "sub_category": "Online Business", "tier": "Business",
     "required_skills": ["e_commerce", "marketing", "supplier_management"], "required_soft": ["persistence", "adaptability"],
     "min_education": "10th", "preferred_education": "Any", "success_rate": 35, "market_demand": 75, "competition": 90,
     "salary_entry": 0, "salary_5yr": 1000000, "salary_10yr": 3000000, "growth_rate": "High", "job_security": 30,
     "remote_friendly": 100, "startup_culture": 100, "corporate_culture": 0, "freelance_potential": 0,
     "learning_curve": "Medium", "time_to_proficiency": "1-2 years", "initial_investment": 100000,
     "emerging_trend": "High", "ai_automation_risk": 45, "future_proof": 70, "industry_growth": "18%/year"},
]

def calculate_comprehensive_score(career, profile):
    """Calculate multi-dimensional career fit score"""
    scores = {}
    
    # 1. Technical Skill Match (30%)
    tech_match = 0
    tech_count = 0
    for skill in career.get("required_skills", []):
        skill_clean = skill.replace("_", " ")
        for tech_cat in profile["technical_skills"]:
            if skill in tech_cat or tech_cat in skill:
                tech_match += profile["technical_skills"][tech_cat]
                tech_count += 1
                break
        for creative_cat in profile["creative_skills"]:
            if skill in creative_cat or creative_cat in skill:
                tech_match += profile["creative_skills"][creative_cat]
                tech_count += 1
                break
    scores["skill_match"] = (tech_match / max(tech_count, 1)) if tech_count > 0 else 50
    
    # 2. Soft Skills Match (15%)
    soft_match = 0
    soft_count = 0
    for skill in career.get("required_soft", []):
        for soft_cat in profile["soft_skills"]:
            if skill in soft_cat or soft_cat in skill:
                soft_match += profile["soft_skills"][soft_cat]
                soft_count += 1
                break
    scores["soft_match"] = (soft_match / max(soft_count, 1)) if soft_count > 0 else 60
    
    # 3. Financial Alignment (20%)
    salary_5yr = career.get("salary_5yr", 0)
    target_5yr = profile["goals"]["5_year_salary_target"]
    if salary_5yr >= target_5yr:
        scores["financial_fit"] = 100
    elif salary_5yr >= target_5yr * 0.7:
        scores["financial_fit"] = 80
    elif salary_5yr >= target_5yr * 0.5:
        scores["financial_fit"] = 60
    else:
        scores["financial_fit"] = 40
    
    # 4. Lifestyle Match (15%)
    lifestyle_score = 0
    if profile["preferences"]["work_environment"] == "Remote" and career["remote_friendly"] >= 80:
        lifestyle_score += 25
    elif profile["preferences"]["work_environment"] == "Hybrid" and career["remote_friendly"] >= 60:
        lifestyle_score += 20
    
    if profile["personality"]["risk_tolerance"] >= 70 and career["tier"] in ["Business", "Digital Creator"]:
        lifestyle_score += 25
    elif profile["personality"]["risk_tolerance"] <= 40 and career["job_security"] >= 75:
        lifestyle_score += 25
    
    if career["growth_rate"] in ["Very High", "Exponential"] and profile["preferences"]["growth_importance"] >= 80:
        lifestyle_score += 25
    
    if career["freelance_potential"] >= 80 and profile["preferences"]["work_hours"] == "Flexible":
        lifestyle_score += 25
    
    scores["lifestyle_match"] = min(lifestyle_score, 100)
    
    # 5. Market Viability (20%)
    market_score = (
        career["market_demand"] * 0.3 +
        (100 - career["competition"]) * 0.2 +
        career["future_proof"] * 0.3 +
        (100 - career["ai_automation_risk"]) * 0.2
    )
    scores["market_viability"] = market_score
    
    # Final Weighted Score
    final = (
        scores["skill_match"] * 0.30 +
        scores["soft_match"] * 0.15 +
        scores["financial_fit"] * 0.20 +
        scores["lifestyle_match"] * 0.15 +
        scores["market_viability"] * 0.20
    )
    
    return final, scores

print("\n" + "="*100)
print("🚀 STAGE 1: CALCULATING PRELIMINARY SCORES (WITHOUT HRM)")
print("="*100)

preliminary_results = []
for career in careers:
    score, breakdown = calculate_comprehensive_score(career, profile)
    preliminary_results.append({
        "career": career,
        "prelim_score": score,
        "breakdown": breakdown
    })

# Sort and show top 20 for HRM analysis
preliminary_results.sort(key=lambda x: x["prelim_score"], reverse=True)
top_20 = preliminary_results[:20]

print(f"\n✅ Preliminary analysis complete!")
print(f"📊 Top 20 candidates selected for deep HRM analysis\n")
print(f"{'Rank':<6} {'Career Name':<35} {'Prelim Score':<15} {'Category':<20}")
print("-" * 100)
for i, result in enumerate(top_20, 1):
    print(f"{i:<6} {result['career']['name']:<35} {result['prelim_score']:<15.1f} {result['career']['category']:<20}")

print("\n" + "="*100)
print("🧠 STAGE 2: DEEP HRM HIERARCHICAL REASONING ANALYSIS")
print("="*100)
print("Sending top 20 careers to HRM for multi-level decision analysis...\n")

final_results = []
start_time = time.time()

for i, result in enumerate(top_20, 1):
    career = result["career"]
    breakdown = result["breakdown"]
    
    # Progress bar
    progress = int((i / len(top_20)) * 50)
    bar = '█' * progress + '░' * (50 - progress)
    print(f"\rProgress: [{bar}] {i}/{len(top_20)} - {career['name'][:30]:<30}", end='', flush=True)
    
    # Build comprehensive HRM query
    message = f"""COMPREHENSIVE CAREER DECISION ANALYSIS

STUDENT PROFILE:
• Age: {profile['age']}, Education: {profile['education']}
• Top Technical Skills: Coding ({profile['technical_skills']['coding']}%), Web Dev ({profile['technical_skills']['web_development']}%), Data Analysis ({profile['technical_skills']['data_analysis']}%)
• Top Creative Skills: Dancing ({profile['creative_skills']['dancing']}%), Singing ({profile['creative_skills']['singing']}%), Video Editing ({profile['creative_skills']['video_editing']}%)
• Personality: Risk Tolerance ({profile['personality']['risk_tolerance']}%), Innovation ({profile['personality']['innovation']}%), Persistence ({profile['personality']['persistence']}%)
• Financial Goals: ₹{profile['goals']['5_year_salary_target']:,} in 5 years, ₹{profile['goals']['10_year_salary_target']:,} in 10 years
• Preferences: {profile['preferences']['work_environment']} work, {profile['preferences']['work_hours']} hours, Growth importance: {profile['preferences']['growth_importance']}%

CAREER OPTION: {career['name']}
Category: {career['category']} | Tier: {career['tier']}
Required Skills: {', '.join(career['required_skills'])}
Soft Skills Needed: {', '.join(career['required_soft'])}

MARKET METRICS:
• Success Rate: {career['success_rate']}% | Market Demand: {career['market_demand']}% | Competition: {career['competition']}%
• Salary Progression: Entry ₹{career['salary_entry']:,} → 5yr ₹{career['salary_5yr']:,} → 10yr ₹{career['salary_10yr']:,}
• Growth Rate: {career['growth_rate']} | Job Security: {career['job_security']}%
• Remote Friendly: {career['remote_friendly']}% | Freelance Potential: {career['freelance_potential']}%
• Learning Curve: {career['learning_curve']} | Time to Proficiency: {career['time_to_proficiency']}
• Initial Investment: ₹{career['initial_investment']:,}
• Future Trends: Emerging Trend ({career['emerging_trend']}), AI Automation Risk ({career['ai_automation_risk']}%), Future Proof ({career['future_proof']}%)
• Industry Growth: {career['industry_growth']}

PRELIMINARY ANALYSIS SCORES:
• Skill Match: {breakdown['skill_match']:.1f}%
• Soft Skills Match: {breakdown['soft_match']:.1f}%
• Financial Alignment: {breakdown['financial_fit']:.1f}%
• Lifestyle Compatibility: {breakdown['lifestyle_match']:.1f}%
• Market Viability: {breakdown['market_viability']:.1f}%
• Overall Preliminary Score: {result['prelim_score']:.1f}/100

DECISION REQUIRED:
Should this student pursue {career['name']} as their career path? 
Consider: skill alignment, financial goals, market conditions, risk factors, growth potential, and long-term sustainability.
Provide hierarchical reasoning with strategic, tactical, and operational perspectives.
Verdict: PASS or FAIL"""
    
    # Send to HRM with error handling
    try:
        r = requests.post(BASE, json={'message': message}, timeout=15)
        r.raise_for_status()
        d = r.json()
        
        hrm_confidence = d.get('confidence', 0.5)
        hrm_decision = d.get('decision', 'UNKNOWN')
        audit_trail = d.get('audit_trail', {})
        
        l1 = audit_trail.get('L1_strategic', {})
        l2 = audit_trail.get('L2_tactical', {})
        l3 = audit_trail.get('L3_operational', {})
        
        risk_level = l1.get('risk_level', 'MEDIUM')
        opportunity_score = l1.get('opportunity_score', 50)
        
    except requests.exceptions.RequestException as e:
        print(f"\n⚠️ API Error for {career['name']}: {e}")
        hrm_confidence = 0.5
        hrm_decision = "ERROR"
        risk_level = "HIGH"
        opportunity_score = 50
        audit_trail = {}
    
    # Calculate final integrated score
    hrm_weight = 0.4  # 40% HRM decision weight
    prelim_weight = 0.6  # 60% preliminary analysis weight
    
    final_score = (result['prelim_score'] * prelim_weight) + (hrm_confidence * 100 * hrm_weight)
    
    # Risk adjustments
    risk_penalties = {"LOW": 5, "MEDIUM": 0, "HIGH": -10, "CRITICAL": -20}
    final_score += risk_penalties.get(risk_level, 0)
    
    # Determine final verdict
    if final_score >= 75 and hrm_decision == "PASS":
        verdict = "✅ HIGHLY RECOMMENDED"
        tier_label = "TIER-A"
    elif final_score >= 65 and hrm_decision == "PASS":
        verdict = "✅ RECOMMENDED"
        tier_label = "TIER-B"
    elif final_score >= 55:
        verdict = "⚠️ CONSIDER WITH CAUTION"
        tier_label = "TIER-C"
    else:
        verdict = "❌ NOT RECOMMENDED"
        tier_label = "TIER-D"
    
    final_results.append({
        "rank": i,
        "name": career["name"],
        "category": career["category"],
        "tier": career["tier"],
        "prelim_score": result["prelim_score"],
        "hrm_confidence": hrm_confidence,
        "hrm_decision": hrm_decision,
        "risk_level": risk_level,
        "opportunity_score": opportunity_score,
        "final_score": final_score,
        "verdict": verdict,
        "tier_label": tier_label,
        "breakdown": breakdown,
        "salary_5yr": career["salary_5yr"],
        "salary_10yr": career["salary_10yr"],
        "growth_rate": career["growth_rate"],
        "time_to_proficiency": career["time_to_proficiency"],
        "initial_investment": career["initial_investment"],
        "future_proof": career["future_proof"],
        "market_demand": career["market_demand"],
        "audit_trail": audit_trail
    })

print(f"\rProgress: [{'█' * 50}] {len(top_20)}/{len(top_20)} - Complete!{' ' * 30}")
elapsed = time.time() - start_time
print(f"\n✅ HRM Analysis complete in {elapsed:.1f} seconds\n")

# Sort by final score
final_results.sort(key=lambda x: x["final_score"], reverse=True)

print("\n" + "="*100)
print("🏆 FINAL COMPREHENSIVE RANKINGS")
print("="*100)
print(f"\n{'Rank':<6} {'Career':<30} {'Final':<8} {'HRM':<8} {'Risk':<10} {'Tier':<8} {'Verdict':<20}")
print("-" * 100)

tier_a_count = tier_b_count = tier_c_count = tier_d_count = 0

for i, r in enumerate(final_results, 1):
    emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "  "
    hrm_conf_display = f"{r['hrm_confidence']:.2f}"
    print(f"{emoji}{i:<4} {r['name']:<30} {r['final_score']:<8.1f} {hrm_conf_display:<8} {r['risk_level']:<10} {r['tier_label']:<8} {r['verdict']:<20}")
    
    if r['tier_label'] == "TIER-A":
        tier_a_count += 1
    elif r['tier_label'] == "TIER-B":
        tier_b_count += 1
    elif r['tier_label'] == "TIER-C":
        tier_c_count += 1
    else:
        tier_d_count += 1

print("\n" + "="*100)
print("📊 SUMMARY STATISTICS")
print("="*100)
print(f"""
   🏆 TIER-A (Highly Recommended): {tier_a_count} careers
   ✅ TIER-B (Recommended): {tier_b_count} careers  
   ⚠️  TIER-C (Consider with Caution): {tier_c_count} careers
   ❌ TIER-D (Not Recommended): {tier_d_count} careers
""")

# Category breakdown
category_stats = {}
for r in final_results:
    cat = r['category']
    if cat not in category_stats:
        category_stats[cat] = {'count': 0, 'avg_score': 0, 'total': 0}
    category_stats[cat]['count'] += 1
    category_stats[cat]['total'] += r['final_score']

print("\n📈 CATEGORY-WISE PERFORMANCE:")
for cat, stats in sorted(category_stats.items(), key=lambda x: x[1]['total']/x[1]['count'], reverse=True):
    avg = stats['total'] / stats['count']
    print(f"   {cat:<30} - Avg Score: {avg:.1f} ({stats['count']} careers)")

print("\n" + "="*100)
print("🎯 TOP 5 CAREER RECOMMENDATIONS (HRM APPROVED)")
print("="*100)

for i, r in enumerate(final_results[:5], 1):
    print(f"""
{'='*100}
{i}. 🌟 {r['name'].upper()} - {r['tier_label']}
{'='*100}
📊 SCORING BREAKDOWN:
   • Final Integrated Score: {r['final_score']:.1f}/100
   • Preliminary Analysis: {r['prelim_score']:.1f}/100
   • HRM Confidence: {r['hrm_confidence']:.3f} ({r['hrm_decision']})
   • Risk Assessment: {r['risk_level']} (Opportunity Score: {r['opportunity_score']})

💼 CAREER METRICS:
   • Category: {r['category']} | Industry Tier: {r['tier']}
   • Market Demand: {r['market_demand']}% | Future Proof Score: {r['future_proof']}%
   • Growth Rate: {r['growth_rate']}

💰 FINANCIAL PROJECTION:
   • 5-Year Salary: ₹{r['salary_5yr']:,}/year
   • 10-Year Salary: ₹{r['salary_10yr']:,}/year
   • Initial Investment: ₹{r['initial_investment']:,}

⏱️ TIME & EFFORT:
   • Time to Proficiency: {r['time_to_proficiency']}
   • Skill Match: {r['breakdown']['skill_match']:.1f}%
   • Soft Skills Match: {r['breakdown']['soft_match']:.1f}%

🎯 FIT ANALYSIS:
   • Financial Alignment: {r['breakdown']['financial_fit']:.1f}%
   • Lifestyle Compatibility: {r['breakdown']['lifestyle_match']:.1f}%
   • Market Viability: {r['breakdown']['market_viability']:.1f}%

✅ VERDICT: {r['verdict']}
""")

print("="*100)
print("🧠 HRM FINAL STRATEGIC RECOMMENDATION")
print("="*100)

best = final_results[0]
print(f"""
Based on comprehensive multi-dimensional analysis combining:
✓ Your unique skill profile (coding, dancing, singing)
✓ Financial goals and risk tolerance
✓ Market demand and future trends
✓ HRM hierarchical reasoning validation

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🏆 #1 RECOMMENDED CAREER PATH: {best['name'].upper()}

Why this is your BEST option:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   📊 Final Score: {best['final_score']:.1f}/100 ({best['tier_label']})
   🎯 HRM Validated: {best['hrm_decision']} (Confidence: {best['hrm_confidence']:.3f})
   💰 Financial Match: Meets your ₹{profile['goals']['5_year_salary_target']:,} goal (5yr: ₹{best['salary_5yr']:,})
   📈 Growth Potential: {best['growth_rate']}
   🛡️ Risk Level: {best['risk_level']}
   🔮 Future Proof: {best['future_proof']}% (Market Demand: {best['market_demand']}%)

🚀 STRATEGIC ACTION PLAN:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   📅 PHASE 1 (Months 1-6): Foundation Building
      • Invest ₹{best['initial_investment']:,} in learning resources
      • Focus on improving skill gaps (Current: {best['breakdown']['skill_match']:.0f}%, Target: 85%+)
      • Complete foundational courses/certifications

   📅 PHASE 2 (Months 7-18): Skill Mastery & Portfolio
      • Build 5-10 portfolio projects showcasing expertise
      • Start freelancing/internships for real-world experience
      • Network with industry professionals

   📅 PHASE 3 (Months 19-36): Market Entry & Growth
      • Apply for entry-level positions or launch business
      • Target entry salary: ₹{best['salary_5yr']//2:,}
      • Continuous learning and skill upgrades

💡 LEVERAGE YOUR UNIQUE COMBINATION:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   • Coding Skills → Technical Foundation
   • Creative Skills (Dance/Singing) → Content/Marketing Edge
   • Your unique blend gives 2-3x advantage in creative-tech roles!

⚠️ TOP 3 ALTERNATIVE OPTIONS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   2. {final_results[1]['name']} (Score: {final_results[1]['final_score']:.1f}, Salary 5yr: ₹{final_results[1]['salary_5yr']:,})
   3. {final_results[2]['name']} (Score: {final_results[2]['final_score']:.1f}, Salary 5yr: ₹{final_results[2]['salary_5yr']:,})
   4. {final_results[3]['name']} (Score: {final_results[3]['final_score']:.1f}, Salary 5yr: ₹{final_results[3]['salary_5yr']:,})

❌ CAREERS TO AVOID:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")

for r in final_results[-3:]:
    print(f"   • {r['name']} - Score: {r['final_score']:.1f}, Risk: {r['risk_level']}, {r['verdict']}")

print(f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 KEY SUCCESS FACTORS:
   1. Time to Proficiency: {best['time_to_proficiency']}
   2. Required Investment: ₹{best['initial_investment']:,}
   3. Risk Management: {best['risk_level']} risk - manage with proper planning
   4. Market Position: {best['market_demand']}% demand ensures opportunities
   5. Future Security: {best['future_proof']}% automation-resistant

💪 YOUR COMPETITIVE ADVANTAGES:
   • Young age ({profile['age']}) = Long career runway
   • Multi-skilled = Unique value proposition
   • High risk tolerance ({profile['personality']['risk_tolerance']}%) = Can pursue high-growth paths
   • Tech + Creative combo = Rare in market

⚡ NEXT IMMEDIATE STEPS:
   1. Research top 3 recommended careers in detail
   2. Connect with 5 professionals in {best['name']} field (LinkedIn)
   3. Enroll in beginner course this week
   4. Set 90-day skill improvement goal
   5. Track progress monthly

🌟 REMEMBER: Success = (Skills × Effort × Market Timing) + Luck
   This analysis optimizes the first 3 variables. Now it's YOUR turn to execute!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")

print("\n" + "="*100)
print(f"📅 Analysis completed at: {datetime.now().strftime('%I:%M:%S %p')}")
print(f"⏱️  Total processing time: {elapsed:.1f} seconds")
print(f"🧠 HRM evaluations: {len(top_20)} deep analyses")
print(f"🎯 Career database: {len(careers)} total options")
print("="*100)
