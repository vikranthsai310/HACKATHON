"""
Entity Extraction Service

Advanced entity extraction from natural language text.
Extracts IPs, emails, usernames, dates, resources, and more.
"""

import re
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class EntityType(Enum):
    """Types of extractable entities"""
    IP_ADDRESS = "ip_address"
    IPV6_ADDRESS = "ipv6_address"
    EMAIL = "email"
    USERNAME = "username"
    DOMAIN = "domain"
    URL = "url"
    FILE_PATH = "file_path"
    PORT = "port"
    DATETIME = "datetime"
    DURATION = "duration"
    RESOURCE = "resource"
    PERMISSION = "permission"
    ACTION = "action"
    NUMBER = "number"
    PERCENTAGE = "percentage"


@dataclass
class ExtractedEntity:
    """Represents an extracted entity"""
    type: EntityType
    value: str
    original_text: str
    start_pos: int
    end_pos: int
    confidence: float = 1.0
    context: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class EntityExtractor:
    """
    Extract structured entities from natural language text
    
    Features:
    - Pattern-based extraction
    - Context-aware entity classification
    - Confidence scoring
    - Deduplication
    """
    
    def __init__(self):
        """Initialize entity extractor with patterns"""
        self._compile_patterns()
        self._load_dictionaries()
    
    def _compile_patterns(self):
        """Compile regex patterns for entity extraction"""
        
        self.patterns = {
            EntityType.IP_ADDRESS: re.compile(
                r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}'
                r'(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b'
            ),
            
            EntityType.IPV6_ADDRESS: re.compile(
                r'\b(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}\b|'
                r'\b(?:[0-9a-fA-F]{1,4}:){1,7}:\b|'
                r'\b(?:[0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}\b'
            ),
            
            EntityType.EMAIL: re.compile(
                r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b'
            ),
            
            EntityType.DOMAIN: re.compile(
                r'\b(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}\b'
            ),
            
            EntityType.URL: re.compile(
                r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+[^\s]*'
            ),
            
            EntityType.FILE_PATH: re.compile(
                r'(?:/[\w.-]+)+|(?:[A-Za-z]:\\[\w\\.-]+)'
            ),
            
            EntityType.PORT: re.compile(
                r'\b(?:port\s*)?(\d{1,5})\b',
                re.IGNORECASE
            ),
            
            EntityType.NUMBER: re.compile(
                r'\b\d+(?:\.\d+)?\b'
            ),
            
            EntityType.PERCENTAGE: re.compile(
                r'\b\d+(?:\.\d+)?%\b'
            )
        }
        
        # Username patterns (more complex)
        self.username_patterns = [
            re.compile(r'\buser[:\s]+([a-zA-Z0-9._-]+)\b', re.IGNORECASE),
            re.compile(r'\b(?:for|to|from)\s+(?:user\s+)?([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b'),
            re.compile(r'\b([a-z]+\.[a-z]+)\b'),  # john.doe format
            re.compile(r'\b@([a-zA-Z0-9_]+)\b'),  # @username format
        ]
        
        # Duration patterns
        self.duration_patterns = [
            (re.compile(r'\b(\d+)\s*(seconds?|secs?|s)\b', re.I), 'seconds'),
            (re.compile(r'\b(\d+)\s*(minutes?|mins?|m)\b', re.I), 'minutes'),
            (re.compile(r'\b(\d+)\s*(hours?|hrs?|h)\b', re.I), 'hours'),
            (re.compile(r'\b(\d+)\s*(days?|d)\b', re.I), 'days'),
            (re.compile(r'\b(\d+)\s*(weeks?|wks?|w)\b', re.I), 'weeks'),
            (re.compile(r'\b(\d+)\s*(months?|mos?)\b', re.I), 'months'),
        ]
        
        # Date/time patterns
        self.datetime_patterns = [
            re.compile(r'\b\d{4}-\d{2}-\d{2}(?:T\d{2}:\d{2}:\d{2})?(?:Z|[+-]\d{2}:\d{2})?\b'),
            re.compile(r'\b\d{2}/\d{2}/\d{4}\b'),
            re.compile(r'\b\d{2}:\d{2}(?::\d{2})?\s*(?:AM|PM|am|pm)?\b'),
            re.compile(r'\b(?:today|yesterday|tomorrow)\b', re.I),
            re.compile(r'\blast\s+(?:\d+\s+)?(?:hour|day|week|month|year)s?\b', re.I),
            re.compile(r'\b(?:next|this)\s+(?:hour|day|week|month|year)\b', re.I),
        ]
    
    def _load_dictionaries(self):
        """Load keyword dictionaries for entity classification"""
        
        self.resource_keywords = {
            "database", "server", "firewall", "system", "network",
            "file", "folder", "directory", "log", "logs", "report",
            "service", "application", "api", "endpoint", "backup",
            "storage", "disk", "memory", "cpu", "container", "pod",
            "cluster", "node", "volume", "instance", "vm", "cloud"
        }
        
        self.permission_keywords = {
            "read", "write", "execute", "delete", "create", "update",
            "admin", "administrator", "root", "sudo", "owner",
            "viewer", "editor", "contributor", "manager", "guest",
            "full", "limited", "readonly", "readwrite"
        }
        
        self.action_keywords = {
            "block", "allow", "deny", "grant", "revoke", "enable",
            "disable", "start", "stop", "restart", "pause", "resume",
            "create", "delete", "update", "modify", "read", "write",
            "scan", "check", "verify", "validate", "audit", "monitor",
            "backup", "restore", "export", "import", "sync", "schedule"
        }
    
    def extract(self, text: str) -> Dict[str, List[ExtractedEntity]]:
        """
        Extract all entities from text
        
        Args:
            text: Input text to extract entities from
            
        Returns:
            Dictionary mapping entity types to lists of extracted entities
        """
        entities: Dict[str, List[ExtractedEntity]] = {}
        text_lower = text.lower()
        
        # Extract pattern-based entities
        for entity_type, pattern in self.patterns.items():
            if entity_type == EntityType.PORT:
                # Special handling for ports
                extracted = self._extract_ports(text)
            else:
                extracted = self._extract_by_pattern(text, pattern, entity_type)
            
            if extracted:
                entities[entity_type.value] = extracted
        
        # Extract usernames
        usernames = self._extract_usernames(text)
        if usernames:
            entities[EntityType.USERNAME.value] = usernames
        
        # Extract durations
        durations = self._extract_durations(text)
        if durations:
            entities[EntityType.DURATION.value] = durations
        
        # Extract datetimes
        datetimes = self._extract_datetimes(text)
        if datetimes:
            entities[EntityType.DATETIME.value] = datetimes
        
        # Extract resources
        resources = self._extract_keywords(text_lower, self.resource_keywords, EntityType.RESOURCE)
        if resources:
            entities[EntityType.RESOURCE.value] = resources
        
        # Extract permissions
        permissions = self._extract_keywords(text_lower, self.permission_keywords, EntityType.PERMISSION)
        if permissions:
            entities[EntityType.PERMISSION.value] = permissions
        
        # Extract actions
        actions = self._extract_keywords(text_lower, self.action_keywords, EntityType.ACTION)
        if actions:
            entities[EntityType.ACTION.value] = actions
        
        # Deduplicate
        entities = self._deduplicate_entities(entities)
        
        return entities
    
    def _extract_by_pattern(
        self,
        text: str,
        pattern: re.Pattern,
        entity_type: EntityType
    ) -> List[ExtractedEntity]:
        """Extract entities using a regex pattern"""
        entities = []
        
        for match in pattern.finditer(text):
            entity = ExtractedEntity(
                type=entity_type,
                value=match.group(),
                original_text=match.group(),
                start_pos=match.start(),
                end_pos=match.end(),
                context=self._get_context(text, match.start(), match.end())
            )
            entities.append(entity)
        
        return entities
    
    def _extract_ports(self, text: str) -> List[ExtractedEntity]:
        """Extract port numbers with validation"""
        entities = []
        pattern = re.compile(r'\bport\s*(\d{1,5})\b|\b:(\d{1,5})\b', re.I)
        
        for match in pattern.finditer(text):
            port_str = match.group(1) or match.group(2)
            port_num = int(port_str)
            
            # Validate port range
            if 1 <= port_num <= 65535:
                entity = ExtractedEntity(
                    type=EntityType.PORT,
                    value=str(port_num),
                    original_text=match.group(),
                    start_pos=match.start(),
                    end_pos=match.end(),
                    metadata={"port_number": port_num}
                )
                entities.append(entity)
        
        return entities
    
    def _extract_usernames(self, text: str) -> List[ExtractedEntity]:
        """Extract usernames using multiple patterns"""
        entities = []
        seen_values = set()
        
        for pattern in self.username_patterns:
            for match in pattern.finditer(text):
                value = match.group(1) if match.groups() else match.group()
                
                # Skip if already seen or too short
                if value.lower() in seen_values or len(value) < 2:
                    continue
                
                # Skip if it looks like a common word
                if value.lower() in {"the", "and", "for", "with", "from", "user"}:
                    continue
                
                seen_values.add(value.lower())
                entity = ExtractedEntity(
                    type=EntityType.USERNAME,
                    value=value,
                    original_text=match.group(),
                    start_pos=match.start(),
                    end_pos=match.end(),
                    context=self._get_context(text, match.start(), match.end())
                )
                entities.append(entity)
        
        return entities
    
    def _extract_durations(self, text: str) -> List[ExtractedEntity]:
        """Extract duration expressions"""
        entities = []
        
        for pattern, unit in self.duration_patterns:
            for match in pattern.finditer(text):
                value = int(match.group(1))
                entity = ExtractedEntity(
                    type=EntityType.DURATION,
                    value=f"{value} {unit}",
                    original_text=match.group(),
                    start_pos=match.start(),
                    end_pos=match.end(),
                    metadata={
                        "value": value,
                        "unit": unit,
                        "seconds": self._duration_to_seconds(value, unit)
                    }
                )
                entities.append(entity)
        
        return entities
    
    def _extract_datetimes(self, text: str) -> List[ExtractedEntity]:
        """Extract date/time expressions"""
        entities = []
        
        for pattern in self.datetime_patterns:
            for match in pattern.finditer(text):
                entity = ExtractedEntity(
                    type=EntityType.DATETIME,
                    value=match.group(),
                    original_text=match.group(),
                    start_pos=match.start(),
                    end_pos=match.end(),
                    metadata={"parsed": self._parse_datetime(match.group())}
                )
                entities.append(entity)
        
        return entities
    
    def _extract_keywords(
        self,
        text: str,
        keywords: set,
        entity_type: EntityType
    ) -> List[ExtractedEntity]:
        """Extract entities based on keyword matching"""
        entities = []
        
        for keyword in keywords:
            pattern = re.compile(rf'\b{re.escape(keyword)}\b', re.I)
            for match in pattern.finditer(text):
                entity = ExtractedEntity(
                    type=entity_type,
                    value=keyword,
                    original_text=match.group(),
                    start_pos=match.start(),
                    end_pos=match.end()
                )
                entities.append(entity)
        
        return entities
    
    def _get_context(self, text: str, start: int, end: int, window: int = 30) -> str:
        """Get surrounding context for an entity"""
        ctx_start = max(0, start - window)
        ctx_end = min(len(text), end + window)
        return text[ctx_start:ctx_end]
    
    def _duration_to_seconds(self, value: int, unit: str) -> int:
        """Convert duration to seconds"""
        multipliers = {
            "seconds": 1,
            "minutes": 60,
            "hours": 3600,
            "days": 86400,
            "weeks": 604800,
            "months": 2592000  # Approximate
        }
        return value * multipliers.get(unit, 1)
    
    def _parse_datetime(self, text: str) -> Optional[str]:
        """Parse datetime text to ISO format"""
        text_lower = text.lower()
        now = datetime.now()
        
        if text_lower == "today":
            return now.date().isoformat()
        elif text_lower == "yesterday":
            return (now - timedelta(days=1)).date().isoformat()
        elif text_lower == "tomorrow":
            return (now + timedelta(days=1)).date().isoformat()
        elif "last" in text_lower:
            # Handle "last X hours/days/etc"
            match = re.search(r'last\s+(\d+)?\s*(hour|day|week|month)', text_lower)
            if match:
                num = int(match.group(1)) if match.group(1) else 1
                unit = match.group(2)
                delta = {
                    "hour": timedelta(hours=num),
                    "day": timedelta(days=num),
                    "week": timedelta(weeks=num),
                    "month": timedelta(days=num*30)
                }.get(unit, timedelta())
                return (now - delta).isoformat()
        
        # Try ISO format
        try:
            return datetime.fromisoformat(text).isoformat()
        except:
            pass
        
        return text
    
    def _deduplicate_entities(
        self,
        entities: Dict[str, List[ExtractedEntity]]
    ) -> Dict[str, List[ExtractedEntity]]:
        """Remove duplicate entities"""
        deduplicated = {}
        
        for entity_type, entity_list in entities.items():
            seen = set()
            unique = []
            
            for entity in entity_list:
                key = (entity.type, entity.value.lower())
                if key not in seen:
                    seen.add(key)
                    unique.append(entity)
            
            if unique:
                deduplicated[entity_type] = unique
        
        return deduplicated
    
    def extract_targets(self, text: str) -> List[str]:
        """Extract target entities (IPs, domains, systems)"""
        entities = self.extract(text)
        targets = []
        
        for ip in entities.get(EntityType.IP_ADDRESS.value, []):
            targets.append(ip.value)
        for domain in entities.get(EntityType.DOMAIN.value, []):
            targets.append(domain.value)
        for resource in entities.get(EntityType.RESOURCE.value, []):
            targets.append(resource.value)
        
        return targets
    
    def extract_subjects(self, text: str) -> List[str]:
        """Extract subject entities (users, emails)"""
        entities = self.extract(text)
        subjects = []
        
        for username in entities.get(EntityType.USERNAME.value, []):
            subjects.append(username.value)
        for email in entities.get(EntityType.EMAIL.value, []):
            subjects.append(email.value)
        
        return subjects
    
    def to_dict(self, entities: Dict[str, List[ExtractedEntity]]) -> Dict[str, Any]:
        """Convert extracted entities to dictionary format"""
        result = {}
        
        for entity_type, entity_list in entities.items():
            result[entity_type] = [
                {
                    "value": e.value,
                    "original": e.original_text,
                    "position": {"start": e.start_pos, "end": e.end_pos},
                    "confidence": e.confidence,
                    "context": e.context,
                    "metadata": e.metadata
                }
                for e in entity_list
            ]
        
        return result
    
    def get_summary(self, text: str) -> Dict[str, Any]:
        """Get a summary of extracted entities"""
        entities = self.extract(text)
        
        return {
            "total_entities": sum(len(v) for v in entities.values()),
            "entity_types": list(entities.keys()),
            "counts": {k: len(v) for k, v in entities.items()},
            "targets": self.extract_targets(text),
            "subjects": self.extract_subjects(text)
        }


# Singleton instance
_extractor_instance: Optional[EntityExtractor] = None


def get_entity_extractor() -> EntityExtractor:
    """Get or create singleton entity extractor"""
    global _extractor_instance
    if _extractor_instance is None:
        _extractor_instance = EntityExtractor()
    return _extractor_instance
