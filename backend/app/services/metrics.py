from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response
import time

# Define Prometheus metrics
REQUEST_COUNT = Counter(
    'therapybot_requests_total',
    'Total number of HTTP requests',
    ['method', 'endpoint', 'status_code']
)

REQUEST_DURATION = Histogram(
    'therapybot_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

ESCALATIONS_TOTAL = Counter(
    'therapybot_escalations_total',
    'Total number of escalations created',
    ['risk_level']
)

ACTIVE_SESSIONS = Gauge(
    'therapybot_active_sessions',
    'Number of active user sessions'
)

MESSAGES_TOTAL = Counter(
    'therapybot_messages_total',
    'Total number of messages sent',
    ['user_role']
)

WELLNESS_LOGS_TOTAL = Counter(
    'therapybot_wellness_logs_total',
    'Total number of wellness log entries'
)

DATABASE_CONNECTIONS = Gauge(
    'therapybot_database_connections',
    'Number of active database connections'
)

def record_request(method: str, endpoint: str, status_code: int, duration: float):
    """Record HTTP request metrics"""
    REQUEST_COUNT.labels(method=method, endpoint=endpoint, status_code=status_code).inc()
    REQUEST_DURATION.labels(method=method, endpoint=endpoint).observe(duration)

def record_escalation(risk_score: float):
    """Record escalation metrics"""
    risk_level = "critical" if risk_score >= 0.8 else "high" if risk_score >= 0.6 else "moderate"
    ESCALATIONS_TOTAL.labels(risk_level=risk_level).inc()

def record_message(user_role: str):
    """Record message metrics"""
    MESSAGES_TOTAL.labels(user_role=user_role).inc()

def record_wellness_log():
    """Record wellness log metrics"""
    WELLNESS_LOGS_TOTAL.inc()

def update_active_sessions(count: int):
    """Update active sessions gauge"""
    ACTIVE_SESSIONS.set(count)

def update_database_connections(count: int):
    """Update database connections gauge"""
    DATABASE_CONNECTIONS.set(count)

def get_metrics():
    """Get Prometheus metrics in text format"""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)