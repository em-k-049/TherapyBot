from celery import Celery
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from ..models import Message, WellnessLog, AuditLog, SessionModel
from ..db import SessionLocal
from ..services.audit import log_action

# Initialize Celery (would be configured properly in production)
celery_app = Celery('retention_tasks')

@celery_app.task
def enforce_retention_policy():
    """Automatically delete old data based on retention policies"""
    db = SessionLocal()
    
    try:
        # Get retention settings (would be from database in production)
        message_retention_days = 365
        wellness_retention_days = 730
        audit_retention_days = 1095
        
        # Calculate cutoff dates
        message_cutoff = datetime.now() - timedelta(days=message_retention_days)
        wellness_cutoff = datetime.now() - timedelta(days=wellness_retention_days)
        audit_cutoff = datetime.now() - timedelta(days=audit_retention_days)
        
        # Hard delete old soft-deleted messages
        old_messages = db.query(Message).filter(
            Message.is_deleted == True,
            Message.deleted_at < message_cutoff
        ).delete()
        
        # Hard delete old soft-deleted wellness logs
        old_wellness = db.query(WellnessLog).filter(
            WellnessLog.is_deleted == True,
            WellnessLog.deleted_at < wellness_cutoff
        ).delete()
        
        # Hard delete old audit logs (including escalation history)
        old_audit_logs = db.query(AuditLog).filter(
            AuditLog.timestamp < audit_cutoff
        ).delete()
        
        # Specifically purge old escalation records
        escalation_cutoff = datetime.now() - timedelta(days=180)  # 6 months for escalations
        old_escalations = db.query(AuditLog).filter(
            AuditLog.action.in_(['escalation_created', 'escalation_viewed', 'escalation_resolved']),
            AuditLog.timestamp < escalation_cutoff
        ).delete()
        
        db.commit()
        
        # Log the cleanup action (after all deletions)
        log_action(db, "automated_data_cleanup", None, {
            "messages_deleted": old_messages,
            "wellness_logs_deleted": old_wellness,
            "audit_logs_deleted": old_audit_logs,
            "escalations_purged": old_escalations,
            "retention_policy": {
                "messages_days": message_retention_days,
                "wellness_days": wellness_retention_days,
                "audit_days": audit_retention_days,
                "escalations_days": 180
            }
        })
        
        return {
            "messages_deleted": old_messages,
            "wellness_logs_deleted": old_wellness,
            "audit_logs_deleted": old_audit_logs,
            "escalations_purged": old_escalations
        }
        
        return {
            "messages_deleted": old_messages,
            "wellness_logs_deleted": old_wellness,
            "audit_logs_deleted": old_audit_logs
        }
        
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

@celery_app.task
def soft_delete_expired_data():
    """Soft delete data that has exceeded retention period"""
    db = SessionLocal()
    
    try:
        # Get retention settings
        message_retention_days = 365
        wellness_retention_days = 730
        
        # Calculate cutoff dates
        message_cutoff = datetime.now() - timedelta(days=message_retention_days)
        wellness_cutoff = datetime.now() - timedelta(days=wellness_retention_days)
        now = datetime.now()
        
        # Soft delete old messages
        expired_messages = db.query(Message).filter(
            Message.created_at < message_cutoff,
            Message.is_deleted == False
        ).update({
            "is_deleted": True,
            "deleted_at": now
        }, synchronize_session=False)
        
        # Soft delete old wellness logs
        expired_wellness = db.query(WellnessLog).filter(
            WellnessLog.created_at < wellness_cutoff,
            WellnessLog.is_deleted == False
        ).update({
            "is_deleted": True,
            "deleted_at": now
        }, synchronize_session=False)
        
        db.commit()
        
        # Log the soft deletion
        log_action(db, "automated_soft_delete", None, {
            "messages_soft_deleted": expired_messages,
            "wellness_logs_soft_deleted": expired_wellness
        })
        
        return {
            "messages_soft_deleted": expired_messages,
            "wellness_logs_soft_deleted": expired_wellness
        }
        
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()