"""
NLP Preprocessor for HRM Decision System

Preprocesses natural language input before sending to LLM.
Handles normalization, entity extraction, and context enrichment.
"""

import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NLPPreprocessor:
    """
    Preprocesses natural language input for the HRM Decision System.
    
    Features:
    - Text normalization
    - Time reference resolution
    - Keyword extraction and tagging
    - Entity pre-extraction
    - Security term detection
    """
    
    # Time patterns with their resolvers
    TIME_PATTERNS = {
        "yesterday": lambda: (datetime.now() - timedelta(days=1)).date(),
        "today": lambda: datetime.now().date(),
        "now": lambda: datetime.now(),
        "last hour": lambda: datetime.now() - timedelta(hours=1),
        "last 24 hours": lambda: datetime.now() - timedelta(hours=24),
        "last 48 hours": lambda: datetime.now() - timedelta(hours=48),
        "this week": lambda: datetime.now() - timedelta(days=7),
        "last week": lambda: datetime.now() - timedelta(days=14),
        "this month": lambda: datetime.now() - timedelta(days=30),
        "last month": lambda: datetime.now() - timedelta(days=60),
    }
    
    # Keywords mapped to intent categories
    KEYWORD_TAGS = {
        "security": [
            "suspicious", "attack", "threat", "block", "breach", "malicious",
            "intrusion", "hack", "exploit", "vulnerability", "unauthorized",
            "anomaly", "compromised", "infected", "quarantine"
        ],
        "compliance": [
            "policy", "audit", "regulation", "compliance", "standard",
            "requirement", "framework", "gdpr", "hipaa", "sox", "pci",
            "violation", "report", "documentation"
        ],
        "access": [
            "access", "permission", "grant", "revoke", "user", "role",
            "authenticate", "authorize", "login", "logout", "privilege",
            "credential", "password", "mfa", "2fa"
        ],
        "system": [
            "backup", "schedule", "maintenance", "restart", "update",
            "upgrade", "configure", "deploy", "monitor", "performance",
            "resource", "server", "service", "network"
        ],
        "query": [
            "show", "list", "display", "find", "search", "get",
            "report", "analyze", "summarize", "count", "status"
        ]
    }
    
    # Action keywords for detection
    ACTION_KEYWORDS = {
        "block": ["block", "deny", "reject", "blacklist", "ban"],
        "allow": ["allow", "permit", "whitelist", "approve", "unblock"],
        "notify": ["notify", "alert", "inform", "email", "message"],
        "scan": ["scan", "check", "verify", "validate", "inspect"],
        "analyze": ["analyze", "investigate", "review", "examine"],
        "schedule": ["schedule", "plan", "set up", "arrange"],
        "grant": ["grant", "give", "provide", "enable"],
        "revoke": ["revoke", "remove", "disable", "take away"]
    }
    
    # IP address regex pattern
    IP_PATTERN = re.compile(
        r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}'
        r'(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b'
    )
    
    # Email pattern
    EMAIL_PATTERN = re.compile(
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    )
    
    # Domain pattern
    DOMAIN_PATTERN = re.compile(
        r'\b(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}\b'
    )
    
    def __init__(self, custom_patterns: Optional[Dict] = None):
        """
        Initialize the preprocessor.
        
        Args:
            custom_patterns: Optional dictionary of custom patterns to add
        """
        self.custom_patterns = custom_patterns or {}
        logger.info("NLPPreprocessor initialized")
    
    def preprocess(self, text: str, include_entities: bool = True) -> Dict[str, Any]:
        """
        Preprocess natural language text.
        
        Args:
            text: Raw user input text
            include_entities: Whether to extract entities
            
        Returns:
            Dictionary containing preprocessed data
        """
        if not text or not isinstance(text, str):
            logger.warning("Empty or invalid text received")
            return self._empty_result()
        
        # Normalize text
        normalized = self._normalize_text(text)
        
        # Resolve time references
        time_refs = self._resolve_time_references(normalized)
        
        # Extract tags
        tags = self._extract_tags(normalized)
        
        # Detect actions
        detected_actions = self._detect_actions(normalized)
        
        # Extract entities if requested
        entities = {}
        if include_entities:
            entities = self._extract_entities(text)
        
        # Clean text
        cleaned = self._clean_text(normalized)
        
        # Calculate urgency
        urgency = self._calculate_urgency(normalized, tags)
        
        result = {
            "original": text,
            "normalized": normalized,
            "cleaned": cleaned,
            "time_references": time_refs,
            "tags": tags,
            "detected_actions": detected_actions,
            "entities": entities,
            "urgency": urgency,
            "preprocessed_at": datetime.now().isoformat(),
            "word_count": len(cleaned.split()),
            "char_count": len(cleaned)
        }
        
        logger.info(f"Preprocessed text with tags: {tags}, urgency: {urgency}")
        return result
    
    def _empty_result(self) -> Dict:
        """Return empty preprocessing result"""
        return {
            "original": "",
            "normalized": "",
            "cleaned": "",
            "time_references": {},
            "tags": [],
            "detected_actions": [],
            "entities": {},
            "urgency": "low",
            "preprocessed_at": datetime.now().isoformat(),
            "word_count": 0,
            "char_count": 0
        }
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text to lowercase and strip whitespace"""
        return text.lower().strip()
    
    def _resolve_time_references(self, text: str) -> Dict[str, str]:
        """
        Resolve time references in text.
        
        Args:
            text: Normalized text
            
        Returns:
            Dictionary mapping time expressions to resolved dates
        """
        resolved = {}
        for pattern, resolver in self.TIME_PATTERNS.items():
            if pattern in text:
                try:
                    resolved[pattern] = str(resolver())
                except Exception as e:
                    logger.error(f"Error resolving time pattern '{pattern}': {e}")
        return resolved
    
    def _extract_tags(self, text: str) -> List[str]:
        """
        Extract category tags from text.
        
        Args:
            text: Normalized text
            
        Returns:
            List of detected category tags
        """
        tags = []
        tag_scores = {}
        
        for category, keywords in self.KEYWORD_TAGS.items():
            score = sum(1 for kw in keywords if kw in text)
            if score > 0:
                tag_scores[category] = score
        
        # Sort by score and return as uppercase tags
        sorted_tags = sorted(tag_scores.items(), key=lambda x: x[1], reverse=True)
        tags = [tag.upper() for tag, _ in sorted_tags]
        
        return tags
    
    def _detect_actions(self, text: str) -> List[str]:
        """
        Detect potential actions from text.
        
        Args:
            text: Normalized text
            
        Returns:
            List of detected action types
        """
        detected = []
        for action_type, keywords in self.ACTION_KEYWORDS.items():
            if any(kw in text for kw in keywords):
                detected.append(action_type.upper())
        return detected
    
    def _extract_entities(self, text: str) -> Dict[str, List[str]]:
        """
        Extract entities from text.
        
        Args:
            text: Original text (preserving case for entities)
            
        Returns:
            Dictionary of extracted entities by type
        """
        entities = {
            "ip_addresses": [],
            "emails": [],
            "domains": [],
            "numbers": [],
            "quoted_strings": []
        }
        
        # Extract IP addresses
        entities["ip_addresses"] = list(set(self.IP_PATTERN.findall(text)))
        
        # Extract emails
        entities["emails"] = list(set(self.EMAIL_PATTERN.findall(text)))
        
        # Extract domains (excluding emails)
        all_domains = set(self.DOMAIN_PATTERN.findall(text))
        email_domains = {email.split('@')[1] for email in entities["emails"]}
        entities["domains"] = list(all_domains - email_domains)
        
        # Extract numbers
        numbers = re.findall(r'\b\d+(?:\.\d+)?\b', text)
        entities["numbers"] = list(set(numbers))
        
        # Extract quoted strings
        quoted = re.findall(r'"([^"]*)"', text) + re.findall(r"'([^']*)'", text)
        entities["quoted_strings"] = list(set(quoted))
        
        return entities
    
    def _clean_text(self, text: str) -> str:
        """
        Clean text by removing extra whitespace.
        
        Args:
            text: Text to clean
            
        Returns:
            Cleaned text
        """
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def _calculate_urgency(self, text: str, tags: List[str]) -> str:
        """
        Calculate urgency level based on text content.
        
        Args:
            text: Normalized text
            tags: Extracted tags
            
        Returns:
            Urgency level: low, medium, high, critical
        """
        urgent_keywords = [
            "urgent", "immediately", "asap", "critical", "emergency",
            "now", "right away", "priority", "important", "attack"
        ]
        
        urgent_count = sum(1 for kw in urgent_keywords if kw in text)
        
        if "SECURITY" in tags and urgent_count >= 2:
            return "critical"
        elif urgent_count >= 2 or ("SECURITY" in tags and urgent_count >= 1):
            return "high"
        elif urgent_count >= 1 or "SECURITY" in tags:
            return "medium"
        else:
            return "low"
    
    def enrich_for_llm(self, preprocessed: Dict) -> str:
        """
        Create enriched prompt for LLM based on preprocessing.
        
        Args:
            preprocessed: Preprocessed data dictionary
            
        Returns:
            Enriched prompt string
        """
        parts = [
            f"Original Request: {preprocessed['original']}",
            f"Detected Categories: {', '.join(preprocessed['tags']) or 'None'}",
            f"Urgency Level: {preprocessed['urgency']}",
        ]
        
        if preprocessed['time_references']:
            parts.append(f"Time References: {preprocessed['time_references']}")
        
        if preprocessed['detected_actions']:
            parts.append(f"Possible Actions: {', '.join(preprocessed['detected_actions'])}")
        
        entities = preprocessed.get('entities', {})
        if entities.get('ip_addresses'):
            parts.append(f"IP Addresses: {', '.join(entities['ip_addresses'])}")
        if entities.get('emails'):
            parts.append(f"Emails: {', '.join(entities['emails'])}")
        
        return "\n".join(parts)
