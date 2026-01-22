"""
Utility helper functions for HRM Decision System
"""

import re
from typing import Dict, List, Any, Optional
from datetime import datetime
import json


def extract_ip_addresses(text: str) -> List[str]:
    """Extract IP addresses from text"""
    ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
    return re.findall(ip_pattern, text)


def extract_emails(text: str) -> List[str]:
    """Extract email addresses from text"""
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return re.findall(email_pattern, text)


def extract_usernames(text: str) -> List[str]:
    """Extract potential usernames from text"""
    # Simple pattern: word after "user" keyword
    username_pattern = r'(?:user|username)\s+(\w+)'
    return re.findall(username_pattern, text.lower())


def sanitize_string(text: str) -> str:
    """Sanitize string for safe processing"""
    # Remove potentially dangerous characters
    sanitized = re.sub(r'[<>\"\'%;()&+]', '', text)
    return sanitized.strip()


def format_timestamp(dt: datetime) -> str:
    """Format datetime to ISO8601 string"""
    return dt.isoformat()


def parse_timestamp(timestamp_str: str) -> datetime:
    """Parse ISO8601 timestamp string"""
    try:
        return datetime.fromisoformat(timestamp_str)
    except ValueError:
        return datetime.now()


def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to max length with ellipsis"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."


def safe_json_dumps(obj: Any, indent: int = 2) -> str:
    """Safely serialize object to JSON with datetime handling"""
    def default_handler(o):
        if isinstance(o, datetime):
            return o.isoformat()
        return str(o)
    
    return json.dumps(obj, indent=indent, default=default_handler)


def validate_confidence(value: float) -> bool:
    """Validate confidence score is between 0 and 1"""
    return 0.0 <= value <= 1.0


def merge_dicts(*dicts: Dict) -> Dict:
    """Merge multiple dictionaries"""
    result = {}
    for d in dicts:
        result.update(d)
    return result
