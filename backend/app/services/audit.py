from sqlalchemy.orm import Session
from datetime import datetime
from typing import Dict, Any, Optional
from ..models import AuditLog, User
from datetime import datetime
import json

def log_action(
    db: Session,
    action: str,
    user_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
):
    """Log user action for audit trail"""
    audit_log = AuditLog(
        user_id=user_id,
        action=action,
        metadata=metadata
    )
    db.add(audit_log)
    db.commit()

def log_login(db: Session, user: User, success: bool = True):
    """Log user login attempt"""
    log_action(
        db,
        "login_success" if success else "login_failed",
        str(user.id) if user else None,
        {"username": user.username if user else "unknown"}
    )

def log_message_sent(db: Session, user: User, message_id: str, is_escalated: bool = False):
    """Log message sending"""
    log_action(
        db,
        "message_sent",
        str(user.id),
        {"message_id": message_id, "escalated": is_escalated}
    )

def log_escalation_viewed(db: Session, user: User, escalation_id: str):
    """Log escalation viewing by consultant"""
    log_action(
        db,
        "escalation_viewed",
        str(user.id),
        {"escalation_id": escalation_id, "role": user.role.name}
    )

def log_role_change(db: Session, admin_user: User, target_user: User, old_role: str, new_role: str):
    """Log user role changes"""
    log_action(
        db,
        "role_changed",
        str(admin_user.id),
        {
            "target_user": target_user.username,
            "old_role": old_role,
            "new_role": new_role
        }
    )

def log_escalation_created(db: Session, user: User, message_id: str, risk_score: float, risk_tags: list):
    """Log escalation creation"""
    log_action(
        db,
        "escalation_created",
        str(user.id),
        {
            "message_id": message_id,
            "risk_score": risk_score,
            "risk_tags": risk_tags,
            "escalation_timestamp": datetime.now().isoformat()
        }
    )

def log_escalation_resolved(db: Session, consultant: User, message_id: str, resolution_notes: str = None):
    """Log escalation resolution"""
    log_action(
        db,
        "escalation_resolved",
        str(consultant.id),
        {
            "message_id": message_id,
            "resolution_notes": resolution_notes,
            "resolved_by": consultant.username,
            "resolution_timestamp": datetime.now().isoformat()
        }
    )