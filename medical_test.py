import requests
import json

BASE = 'http://localhost:8000/api/v1/decision/quick'

print("\n" + "="*70)
print("🏥 HRM MEDICAL RECORDS USE CASE DEMONSTRATION")
print("="*70)

# Medical record scenarios
medical_scenarios = [
    # Access Control
    "Grant Dr. Smith access to patient John Doe medical records",
    "Revoke nurse access to psychiatric patient files",
    "Check if intern has authorization to view lab results",
    
    # Compliance & Privacy
    "Verify HIPAA compliance for patient data transfer",
    "Audit who accessed patient record #12345 in last 7 days",
    "Generate compliance report for patient data handling",
    
    # Clinical Decisions
    "Approve prescription request for controlled substance",
    "Schedule emergency surgery for patient with critical condition",
    "Review and approve patient discharge request",
    
    # Data Management
    "Backup all patient records before system migration",
    "Archive medical records older than 7 years",
    "Transfer patient records to new healthcare provider",
]

print("\n📋 Testing Medical Record Scenarios:\n")

for i, scenario in enumerate(medical_scenarios, 1):
    r = requests.post(BASE, json={'message': scenario})
    d = r.json()
    
    l1 = d.get('audit_trail', {}).get('L1_strategic', {})
    l2 = d.get('audit_trail', {}).get('L2_tactical', {})
    l3 = d.get('audit_trail', {}).get('L3_operational', {})
    
    print(f"{i:2}. 📝 \"{scenario}\"")
    print(f"    🎯 Goal: {l1.get('goal', 'N/A')}")
    print(f"    ⚠️  Risk: {l1.get('risk_level', 'N/A')} | 💯 Confidence: {d.get('confidence')}")
    print(f"    📊 Strategy: {l2.get('strategy', 'N/A')} | Policy: {l2.get('policy', 'N/A')}")
    print(f"    🔧 Actions: {l3.get('actions', [])}")
    print()

print("="*70)
print("🏥 MEDICAL RECORDS HRM CAPABILITIES")
print("="*70)
print("""
✅ WHAT HRM CAN DO FOR MEDICAL RECORDS:

1. 🔐 ACCESS CONTROL
   - Grant/revoke access to patient records
   - Role-based permission management
   - Authentication verification

2. 📋 COMPLIANCE & AUDIT
   - HIPAA compliance verification
   - Audit trail generation
   - Access logging and monitoring

3. 🏥 CLINICAL WORKFLOW
   - Prescription approval workflows
   - Surgery scheduling decisions
   - Discharge authorization

4. 💾 DATA MANAGEMENT
   - Backup and archival decisions
   - Data transfer authorization
   - Record retention policies

5. ⚠️  RISK ASSESSMENT
   - Privacy breach risk evaluation
   - Compliance risk scoring
   - Security threat detection

⚠️  IMPORTANT CONSIDERATIONS:

1. REGULATORY COMPLIANCE:
   - Must comply with HIPAA (USA)
   - GDPR for EU patients
   - Local healthcare regulations

2. DATA SENSITIVITY:
   - PHI (Protected Health Information) handling
   - Encryption requirements
   - Minimum necessary standard

3. INTEGRATION NEEDS:
   - EHR/EMR system integration
   - HL7/FHIR standards support
   - Healthcare API compatibility

4. AUDIT REQUIREMENTS:
   - Complete audit trails
   - Non-repudiation
   - Long-term log retention

💡 TO FULLY ADAPT FOR MEDICAL USE:
   1. Add HIPAA-specific policies
   2. Integrate with EHR systems
   3. Add clinical decision support rules
   4. Implement patient consent management
   5. Add emergency access protocols (Break-the-glass)
""")
print("="*70)
