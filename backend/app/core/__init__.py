# Core logic package
from .schema_validator import SchemaValidator
from .preprocessor import NLPPreprocessor
from .llm_interpreter import LLMInterpreter
from .hrm_engine import HRMEngine, create_hrm_engine
from .action_executor import ActionExecutor, create_action_executor

# Phase 2 imports
from .prompt_templates import PromptTemplates, ConversationContext
from .llm_enhanced import EnhancedLLMInterpreter, LLMConfig, ResponseCache
from .entity_extractor import EntityExtractor, ExtractedEntity, EntityType
from .intent_validator import IntentValidator, IntentEnricher, ValidationResult
from .action_mapper import ActionMapper, MappedAction, ActionDefinition, ActionCategory

# Phase 3 imports
from .audit_logger import (
    AuditLogger,
    AuditEntry,
    AuditSummary,
    AuditEventType,
    AuditSeverity,
    get_audit_logger,
    create_audit_logger
)

__all__ = [
    # Phase 1
    "SchemaValidator",
    "NLPPreprocessor",
    "LLMInterpreter",
    "HRMEngine",
    "ActionExecutor",
    "PlaceholderHRMEngine",
    # Phase 2
    "PromptTemplates",
    "ConversationContext",
    "EnhancedLLMInterpreter",
    "LLMConfig",
    "ResponseCache",
    "EntityExtractor",
    "ExtractedEntity",
    "EntityType",
    "IntentValidator",
    "IntentEnricher",
    "ValidationResult",
    "ActionMapper",
    "MappedAction",
    "ActionDefinition",
    "ActionCategory",
    # Phase 3
    "create_hrm_engine",
    "create_action_executor",
    "AuditLogger",
    "AuditEntry",
    "AuditSummary",
    "AuditEventType",
    "AuditSeverity",
    "get_audit_logger",
    "create_audit_logger",
]
