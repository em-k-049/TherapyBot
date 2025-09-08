from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import Dict, Any, List
from pydantic import BaseModel
from datetime import datetime, timedelta
from ..models import User, Message, AuditLog, Session as SessionModel
from ..deps import get_db, require_role
from ..services.audit import log_action

router = APIRouter(prefix="/admin", tags=["admin"])

class RetentionSettings(BaseModel):
    messages: int
    wellness: int
    audit: int
    escalations: int = 180  # 6 months for escalation history
    autoDelete: bool = False

class AuditLogRead(BaseModel):
    id: str
    user: str = None
    action: str
    timestamp: datetime
    metadata: dict = None
    
    class Config:
        from_attributes = True

@router.get("/metrics")
def get_system_metrics(
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_role("admin"))
):
    """Get system-wide metrics for admin dashboard"""
    
    # Count total users
    total_users = db.query(User).count()
    
    # Count active sessions (last 24 hours)
    yesterday = datetime.now() - timedelta(days=1)
    active_sessions = db.query(SessionModel).filter(
        SessionModel.started_at >= yesterday,
        SessionModel.ended_at.is_(None)
    ).count()
    
    # Count total escalations
    total_escalations = db.query(Message).filter(Message.is_escalated == True).count()
    
    # Count critical cases (risk score >= 0.8)
    critical_cases = db.query(Message).filter(
        and_(Message.is_escalated == True, Message.risk_score >= 0.8)
    ).count()
    
    # Count online consultants (mock - would need real presence tracking)
    consultants_online = db.query(User).join(User.role).filter(
        User.role.has(name="consultant")
    ).count()
    
    # Average response time (mock - would need actual response tracking)
    avg_response_time = 8.5
    
    return {
        "total_users": total_users,
        "active_sessions": active_sessions,
        "total_escalations": total_escalations,
        "critical_cases": critical_cases,
        "consultants_online": consultants_online,
        "avg_response_time": avg_response_time
    }

@router.get("/audit-logs", response_model=List[AuditLogRead])
def get_audit_logs(
    limit: int = 100,
    user_filter: str = None,
    action_filter: str = None,
    date_from: str = None,
    date_to: str = None,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_role("admin"))
):
    """Get filtered audit logs"""
    
    query = db.query(AuditLog).join(
        User, AuditLog.user_id == User.id, isouter=True
    )
    
    # Apply filters
    if user_filter:
        query = query.filter(User.username.ilike(f"%{user_filter}%"))
    
    if action_filter:
        query = query.filter(AuditLog.action.ilike(f"%{action_filter}%"))
    
    if date_from:
        query = query.filter(AuditLog.timestamp >= date_from)
    
    if date_to:
        query = query.filter(AuditLog.timestamp <= date_to + " 23:59:59")
    
    logs = query.order_by(AuditLog.timestamp.desc()).limit(limit).all()
    
    return [
        AuditLogRead(
            id=str(log.id),
            user=log.user.username if log.user else None,
            action=log.action,
            timestamp=log.timestamp,
            metadata=log.metadata
        )
        for log in logs
    ]

@router.put("/settings/retention")
def update_retention_settings(
    settings: RetentionSettings,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_role("admin"))
):
    """Update data retention policies"""
    
    # Log the settings change
    log_action(
        db,
        "retention_settings_updated",
        str(admin_user.id),
        {
            "messages_days": settings.messages,
            "wellness_days": settings.wellness,
            "audit_days": settings.audit,
            "escalations_days": settings.escalations
        }
    )
    
    # In production, would store these settings in a configuration table
    # For now, just return success
    return {
        "message": "Retention settings updated successfully",
        "settings": settings.dict()
    }

@router.delete("/cleanup/messages")
def cleanup_old_messages(
    days: int = 365,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_role("admin"))
):
    """Clean up old messages based on retention policy"""
    
    cutoff_date = datetime.now() - timedelta(days=days)
    deleted_count = db.query(Message).filter(
        Message.created_at < cutoff_date
    ).delete()
    
    db.commit()
    
    # Log the cleanup action
    log_action(
        db,
        "messages_cleanup",
        str(admin_user.id),
        {"deleted_count": deleted_count, "days": days}
    )
    
    return {
        "message": f"Deleted {deleted_count} old messages",
        "deleted_count": deleted_count
    }

@router.delete("/cleanup/audit-logs")
def cleanup_old_audit_logs(
    days: int = 1095,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_role("admin"))
):
    """Clean up old audit logs based on retention policy"""
    
    cutoff_date = datetime.now() - timedelta(days=days)
    deleted_count = db.query(AuditLog).filter(
        AuditLog.timestamp < cutoff_date
    ).delete()
    
    db.commit()
    
    return {
        "message": f"Deleted {deleted_count} old audit logs",
        "deleted_count": deleted_count
    }