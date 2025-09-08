import structlog
import logging
from elasticsearch import Elasticsearch
from datetime import datetime
import json
import os

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

# Initialize Elasticsearch client
ES_HOST = os.getenv("ELASTICSEARCH_HOST", "localhost:9200")
try:
    es_client = Elasticsearch([ES_HOST])
except Exception:
    es_client = None

logger = structlog.get_logger()

def log_to_elasticsearch(index: str, doc_type: str, body: dict):
    """Send log entry to Elasticsearch"""
    if not es_client:
        return
    
    try:
        es_client.index(
            index=f"therapybot-{index}-{datetime.now().strftime('%Y.%m.%d')}",
            body={
                **body,
                "timestamp": datetime.now().isoformat(),
                "service": "therapybot-api"
            }
        )
    except Exception as e:
        logger.error("Failed to send log to Elasticsearch", error=str(e))

def log_audit_event(user_id: str, action: str, metadata: dict):
    """Log audit event to Elasticsearch"""
    log_to_elasticsearch("audit", "audit_log", {
        "user_id": user_id,
        "action": action,
        "metadata": metadata,
        "log_type": "audit"
    })

def log_escalation_event(message_id: str, risk_score: float, user_id: str, action: str):
    """Log escalation event to Elasticsearch"""
    log_to_elasticsearch("escalations", "escalation_log", {
        "message_id": message_id,
        "risk_score": risk_score,
        "user_id": user_id,
        "action": action,
        "log_type": "escalation"
    })

def log_api_request(method: str, path: str, status_code: int, duration_ms: float, user_id: str = None):
    """Log API request to Elasticsearch"""
    log_to_elasticsearch("api", "api_log", {
        "method": method,
        "path": path,
        "status_code": status_code,
        "duration_ms": duration_ms,
        "user_id": user_id,
        "log_type": "api_request"
    })

def log_error(error: Exception, context: dict = None):
    """Log error to Elasticsearch"""
    log_to_elasticsearch("errors", "error_log", {
        "error_type": type(error).__name__,
        "error_message": str(error),
        "context": context or {},
        "log_type": "error"
    })