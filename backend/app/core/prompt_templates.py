"""
Prompt Templates for LLM Integration

This module contains all prompt templates used for LLM-based intent parsing,
entity extraction, and action mapping.
"""

from typing import Dict, Any, Optional
from datetime import datetime


class PromptTemplates:
    """
    Collection of prompt templates for different LLM tasks
    """
    
    # ==========================================================================
    # SYSTEM PROMPTS
    # ==========================================================================
    
    INTENT_PARSER_SYSTEM = """You are a semantic intent parser for a Hybrid Decision-Making System (HRM).
Your role is to extract structured intent from natural language requests.

IMPORTANT RULES:
1. You are NOT a decision maker - only extract intent
2. Output MUST be valid JSON matching the schema exactly
3. Be precise and deterministic
4. If intent is unclear, set confidence < 0.5
5. Extract ALL relevant entities from the request

VALID INTENT TYPES:
- SECURITY: Threat detection, IP blocking, security monitoring, attack prevention
- COMPLIANCE: Policy checks, audit requests, regulatory compliance, reports
- ACCESS: Permission management, user access grants/revokes, role assignments
- SYSTEM: Maintenance, backups, scheduling, configuration changes
- QUERY: Information retrieval, status checks, log queries, data lookups

VALID ACTIONS (use one or more):
Security Actions:
- BLOCK_IP: Block an IP address
- ALLOW_IP: Whitelist an IP address
- UPDATE_FIREWALL_RULES: Modify firewall configuration
- SCAN_NETWORK: Scan for threats
- ISOLATE_SYSTEM: Isolate a compromised system

Access Actions:
- GRANT_ACCESS: Give access permissions
- REVOKE_ACCESS: Remove access permissions
- MODIFY_PERMISSIONS: Change existing permissions
- CREATE_USER: Create new user account
- DELETE_USER: Remove user account

Query Actions:
- QUERY_DATABASE: Search database
- FETCH_LOGS: Retrieve log entries
- GET_STATUS: Get system status
- GENERATE_REPORT: Create a report

System Actions:
- EXECUTE_COMMAND: Run system command
- SCHEDULE_TASK: Schedule a task
- BACKUP_DATA: Backup data
- RESTART_SERVICE: Restart a service
- UPDATE_CONFIG: Update configuration

Compliance Actions:
- GENERATE_AUDIT_REPORT: Create audit report
- VERIFY_COMPLIANCE: Check compliance status
- ENFORCE_POLICY: Apply policy rules

RISK LEVELS:
- LOW: Read-only operations, queries, status checks
- MEDIUM: Minor changes, temporary modifications
- HIGH: Significant changes, access modifications
- CRITICAL: System-wide changes, security actions, data deletion

OUTPUT SCHEMA:
{
  "intent_type": "SECURITY|COMPLIANCE|ACCESS|SYSTEM|QUERY",
  "goal": "Clear description of what the user wants to achieve",
  "constraints": {
    "time_window": {"start": "ISO8601 or null", "end": "ISO8601 or null"},
    "filters": {"key": "value"},
    "thresholds": {"metric": value}
  },
  "entities": {
    "targets": [{"type": "ip|user|system|resource", "value": "..."}],
    "subjects": [{"type": "user|role|group", "value": "..."}],
    "objects": [{"type": "resource|permission|data", "value": "..."}]
  },
  "requested_actions": ["ACTION_1", "ACTION_2"],
  "confidence": 0.0-1.0,
  "risk_assessment": "LOW|MEDIUM|HIGH|CRITICAL",
  "reasoning": "Brief explanation of interpretation"
}"""

    ENTITY_EXTRACTOR_SYSTEM = """You are an entity extraction system.
Extract all relevant entities from the text.

Entity Types:
- IP_ADDRESS: IPv4 or IPv6 addresses
- EMAIL: Email addresses
- USERNAME: User identifiers (john.doe, jsmith, etc.)
- DOMAIN: Domain names (example.com)
- PATH: File paths (/var/log/syslog)
- PORT: Network ports (8080, 443)
- DATETIME: Date and time references
- DURATION: Time durations (24 hours, 2 days)
- RESOURCE: System resources (database, server, firewall)
- PERMISSION: Access levels (read, write, admin)

Output as JSON array:
[
  {"type": "IP_ADDRESS", "value": "192.168.1.100", "context": "target of block"},
  {"type": "USERNAME", "value": "john.smith", "context": "subject of access grant"}
]"""

    ACTION_MAPPER_SYSTEM = """You are an action mapping system.
Map user intentions to specific system actions.

Given the intent and entities, determine:
1. Primary action to take
2. Secondary/supporting actions
3. Required parameters for each action
4. Execution order (sequential or parallel)

Output as JSON:
{
  "primary_action": "ACTION_NAME",
  "secondary_actions": ["ACTION_1", "ACTION_2"],
  "parameters": {
    "ACTION_NAME": {"param1": "value1"}
  },
  "execution_order": "sequential|parallel",
  "requires_confirmation": true|false
}"""

    # ==========================================================================
    # USER PROMPT TEMPLATES
    # ==========================================================================
    
    @staticmethod
    def build_intent_prompt(
        message: str,
        preprocessed: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Build the user prompt for intent parsing"""
        
        prompt_parts = [
            f"Parse the following user request into structured intent:\n",
            f'REQUEST: "{message}"\n'
        ]
        
        if preprocessed:
            prompt_parts.append("\nPREPROCESSED INFO:")
            if 'normalized' in preprocessed:
                prompt_parts.append(f"- Normalized: {preprocessed['normalized']}")
            if 'time_references' in preprocessed and preprocessed['time_references']:
                prompt_parts.append(f"- Time References: {preprocessed['time_references']}")
            if 'tags' in preprocessed and preprocessed['tags']:
                prompt_parts.append(f"- Tags: {preprocessed['tags']}")
            if 'entities' in preprocessed and preprocessed['entities']:
                prompt_parts.append(f"- Detected Entities: {preprocessed['entities']}")
            if 'detected_actions' in preprocessed and preprocessed['detected_actions']:
                prompt_parts.append(f"- Detected Actions: {preprocessed['detected_actions']}")
            if 'urgency' in preprocessed:
                prompt_parts.append(f"- Urgency: {preprocessed['urgency']}")
        
        if context:
            prompt_parts.append("\nCONTEXT:")
            if 'user_role' in context:
                prompt_parts.append(f"- User Role: {context['user_role']}")
            if 'previous_intents' in context:
                prompt_parts.append(f"- Previous Intents: {context['previous_intents'][-3:]}")
            if 'session_id' in context:
                prompt_parts.append(f"- Session: {context['session_id']}")
        
        prompt_parts.append(f"\nCurrent Time: {datetime.now().isoformat()}")
        prompt_parts.append("\nOutput the structured intent JSON:")
        
        return "\n".join(prompt_parts)
    
    @staticmethod
    def build_entity_prompt(message: str, preprocessed: Optional[Dict] = None) -> str:
        """Build prompt for entity extraction"""
        
        prompt = f'Extract all entities from this text:\n\n"{message}"'
        
        if preprocessed and 'entities' in preprocessed:
            prompt += f"\n\nAlready detected: {preprocessed['entities']}"
            prompt += "\n\nExtract any additional entities not listed above."
        
        return prompt
    
    @staticmethod
    def build_clarification_prompt(
        original_message: str,
        parsed_intent: Dict[str, Any],
        ambiguities: list
    ) -> str:
        """Build prompt to clarify ambiguous requests"""
        
        return f"""The following request has ambiguities that need clarification:

ORIGINAL REQUEST: "{original_message}"

CURRENT INTERPRETATION:
- Intent: {parsed_intent.get('intent_type', 'UNKNOWN')}
- Goal: {parsed_intent.get('goal', 'Unknown')}
- Confidence: {parsed_intent.get('confidence', 0)}

AMBIGUITIES DETECTED:
{chr(10).join(f'- {a}' for a in ambiguities)}

Generate a clarifying question to ask the user."""
    
    @staticmethod
    def build_action_mapping_prompt(
        intent_type: str,
        goal: str,
        entities: Dict[str, Any],
        constraints: Dict[str, Any]
    ) -> str:
        """Build prompt for action mapping"""
        
        return f"""Map the following intent to system actions:

INTENT TYPE: {intent_type}
GOAL: {goal}
ENTITIES: {entities}
CONSTRAINTS: {constraints}

Determine the appropriate actions and their parameters."""

    # ==========================================================================
    # FEW-SHOT EXAMPLES
    # ==========================================================================
    
    FEW_SHOT_EXAMPLES = [
        {
            "input": "Block all suspicious login attempts from foreign IPs in the last 24 hours",
            "output": {
                "intent_type": "SECURITY",
                "goal": "Block suspicious foreign login attempts",
                "constraints": {
                    "time_window": {"start": "24 hours ago", "end": "now"},
                    "filters": {"login_status": "suspicious", "ip_origin": "foreign"},
                    "thresholds": {}
                },
                "entities": {
                    "targets": [],
                    "subjects": [],
                    "objects": [{"type": "login_attempts", "value": "suspicious"}]
                },
                "requested_actions": ["SCAN_NETWORK", "BLOCK_IP"],
                "confidence": 0.92,
                "risk_assessment": "HIGH",
                "reasoning": "User wants to identify and block suspicious foreign login attempts from the past day"
            }
        },
        {
            "input": "Grant John Smith read access to the financial reports",
            "output": {
                "intent_type": "ACCESS",
                "goal": "Grant read access to financial reports for specific user",
                "constraints": {
                    "time_window": {},
                    "filters": {},
                    "thresholds": {}
                },
                "entities": {
                    "targets": [{"type": "resource", "value": "financial reports"}],
                    "subjects": [{"type": "user", "value": "John Smith"}],
                    "objects": [{"type": "permission", "value": "read"}]
                },
                "requested_actions": ["GRANT_ACCESS"],
                "confidence": 0.95,
                "risk_assessment": "MEDIUM",
                "reasoning": "Clear access grant request for a specific user to a specific resource"
            }
        },
        {
            "input": "Show me all failed login attempts from yesterday",
            "output": {
                "intent_type": "QUERY",
                "goal": "Retrieve failed login attempts from yesterday",
                "constraints": {
                    "time_window": {"start": "yesterday 00:00", "end": "yesterday 23:59"},
                    "filters": {"login_status": "failed"},
                    "thresholds": {}
                },
                "entities": {
                    "targets": [],
                    "subjects": [],
                    "objects": [{"type": "log_entry", "value": "login_attempts"}]
                },
                "requested_actions": ["FETCH_LOGS", "GENERATE_REPORT"],
                "confidence": 0.93,
                "risk_assessment": "LOW",
                "reasoning": "Read-only query for historical login data"
            }
        },
        {
            "input": "Schedule a full database backup for 2 AM tonight",
            "output": {
                "intent_type": "SYSTEM",
                "goal": "Schedule database backup",
                "constraints": {
                    "time_window": {"scheduled": "02:00 tonight"},
                    "filters": {"backup_type": "full"},
                    "thresholds": {}
                },
                "entities": {
                    "targets": [{"type": "resource", "value": "database"}],
                    "subjects": [],
                    "objects": []
                },
                "requested_actions": ["SCHEDULE_TASK", "BACKUP_DATA"],
                "confidence": 0.94,
                "risk_assessment": "LOW",
                "reasoning": "Scheduled maintenance task with specific time requirement"
            }
        },
        {
            "input": "Generate compliance audit report for Q4 2025",
            "output": {
                "intent_type": "COMPLIANCE",
                "goal": "Generate quarterly compliance audit report",
                "constraints": {
                    "time_window": {"start": "2025-10-01", "end": "2025-12-31"},
                    "filters": {"report_type": "compliance_audit", "period": "Q4 2025"},
                    "thresholds": {}
                },
                "entities": {
                    "targets": [],
                    "subjects": [],
                    "objects": [{"type": "report", "value": "compliance_audit"}]
                },
                "requested_actions": ["GENERATE_AUDIT_REPORT"],
                "confidence": 0.91,
                "risk_assessment": "LOW",
                "reasoning": "Report generation request for specific time period"
            }
        }
    ]
    
    @classmethod
    def get_few_shot_prompt(cls) -> str:
        """Generate few-shot examples string"""
        
        examples = []
        for i, example in enumerate(cls.FEW_SHOT_EXAMPLES, 1):
            examples.append(f"Example {i}:")
            examples.append(f"Input: \"{example['input']}\"")
            examples.append(f"Output: {example['output']}")
            examples.append("")
        
        return "\n".join(examples)
    
    @classmethod
    def get_full_system_prompt(cls, include_examples: bool = True) -> str:
        """Get complete system prompt with optional few-shot examples"""
        
        prompt = cls.INTENT_PARSER_SYSTEM
        
        if include_examples:
            prompt += "\n\n" + "="*50 + "\nEXAMPLES:\n" + "="*50 + "\n"
            prompt += cls.get_few_shot_prompt()
        
        return prompt


class ConversationContext:
    """
    Manages conversation context for multi-turn interactions
    """
    
    def __init__(self, session_id: str, max_history: int = 10):
        self.session_id = session_id
        self.max_history = max_history
        self.history: list = []
        self.extracted_entities: Dict[str, Any] = {}
        self.current_intent: Optional[Dict[str, Any]] = None
        self.clarification_needed: bool = False
        self.created_at = datetime.now()
        self.last_activity = datetime.now()
    
    def add_turn(self, user_message: str, intent: Dict[str, Any], response: str):
        """Add a conversation turn"""
        self.history.append({
            "timestamp": datetime.now().isoformat(),
            "user_message": user_message,
            "intent": intent,
            "response": response
        })
        
        # Keep only recent history
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]
        
        # Update entities
        if 'entities' in intent:
            self._merge_entities(intent['entities'])
        
        self.current_intent = intent
        self.last_activity = datetime.now()
    
    def _merge_entities(self, new_entities: Dict[str, list]):
        """Merge new entities with existing ones"""
        for entity_type, entities in new_entities.items():
            if entity_type not in self.extracted_entities:
                self.extracted_entities[entity_type] = []
            
            for entity in entities:
                if entity not in self.extracted_entities[entity_type]:
                    self.extracted_entities[entity_type].append(entity)
    
    def get_context_for_prompt(self) -> Dict[str, Any]:
        """Get context data for prompt building"""
        return {
            "session_id": self.session_id,
            "previous_intents": [h['intent'].get('intent_type') for h in self.history[-3:]],
            "known_entities": self.extracted_entities,
            "turn_count": len(self.history),
            "last_intent": self.current_intent
        }
    
    def needs_clarification(self, intent: Dict[str, Any]) -> tuple:
        """Check if intent needs clarification"""
        ambiguities = []
        
        # Low confidence
        if intent.get('confidence', 1.0) < 0.5:
            ambiguities.append("Low confidence in interpretation")
        
        # Missing required entities for certain intents
        intent_type = intent.get('intent_type', '')
        entities = intent.get('entities', {})
        
        if intent_type == 'ACCESS':
            if not entities.get('subjects'):
                ambiguities.append("No user/subject specified for access request")
            if not entities.get('targets') and not entities.get('objects'):
                ambiguities.append("No resource/target specified for access request")
        
        if intent_type == 'SECURITY':
            if not entities.get('targets') and 'BLOCK' in str(intent.get('requested_actions', [])):
                ambiguities.append("No target specified for blocking action")
        
        self.clarification_needed = len(ambiguities) > 0
        return self.clarification_needed, ambiguities
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize context to dictionary"""
        return {
            "session_id": self.session_id,
            "history": self.history,
            "extracted_entities": self.extracted_entities,
            "current_intent": self.current_intent,
            "clarification_needed": self.clarification_needed,
            "created_at": self.created_at.isoformat(),
            "last_activity": self.last_activity.isoformat()
        }
