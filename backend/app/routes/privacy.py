from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel
import json
import io
from ..models import User, Message, WellnessLog, Session as SessionModel
from ..deps import get_db, get_current_user
from ..services.audit import log_action

router = APIRouter(prefix="/privacy", tags=["privacy"])

class DataExportResponse(BaseModel):
    message: str
    download_url: str = None

class DataDeletionRequest(BaseModel):
    confirm: bool
    reason: str = None

@router.get("/export")
def export_user_data(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Export all user data (messages, wellness logs, sessions)"""
    
    # Get user's messages with decrypted content
    messages = db.query(Message).join(SessionModel).filter(
        SessionModel.user_id == current_user.id,
        Message.is_deleted == False
    ).all()
    
    # Get user's wellness logs with decrypted notes
    wellness_logs = db.query(WellnessLog).filter(
        WellnessLog.patient_id == current_user.id,
        WellnessLog.is_deleted == False
    ).all()
    
    # Get user's sessions
    sessions = db.query(SessionModel).filter(
        SessionModel.user_id == current_user.id
    ).all()
    
    # Prepare export data
    export_data = {
        "user_info": {
            "username": current_user.username,
            "email": current_user.email,
            "role": current_user.role.name,
            "created_at": current_user.created_at.isoformat(),
            "preferred_language": current_user.preferred_language
        },
        "messages": [
            {
                "id": str(msg.id),
                "content": msg.get_content(),
                "created_at": msg.created_at.isoformat(),
                "is_escalated": msg.is_escalated,
                "risk_score": msg.risk_score,
                "risk_tags": msg.risk_tags,
                "session_id": str(msg.session_id)
            }
            for msg in messages
        ],
        "wellness_logs": [
            {
                "id": str(log.id),
                "mood_score": log.mood_score,
                "note": log.get_note(),
                "created_at": log.created_at.isoformat()
            }
            for log in wellness_logs
        ],
        "sessions": [
            {
                "id": str(session.id),
                "started_at": session.started_at.isoformat(),
                "ended_at": session.ended_at.isoformat() if session.ended_at else None
            }
            for session in sessions
        ],
        "export_info": {
            "exported_at": datetime.now().isoformat(),
            "total_messages": len(messages),
            "total_wellness_logs": len(wellness_logs),
            "total_sessions": len(sessions)
        }
    }
    
    # Log the export action
    log_action(db, "data_exported", str(current_user.id), {
        "messages_count": len(messages),
        "wellness_logs_count": len(wellness_logs)
    })
    
    # Create JSON file in memory
    json_data = json.dumps(export_data, indent=2, ensure_ascii=False)
    file_buffer = io.BytesIO(json_data.encode('utf-8'))
    
    filename = f"therapybot_data_export_{current_user.username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    return StreamingResponse(
        io.BytesIO(json_data.encode('utf-8')),
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@router.post("/delete-account")
def delete_user_account(
    request: DataDeletionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Soft delete user account and all associated data"""
    
    if not request.confirm:
        raise HTTPException(status_code=400, detail="Account deletion must be confirmed")
    
    now = datetime.now()
    
    # Get user's session IDs first
    user_session_ids = db.query(SessionModel.id).filter(
        SessionModel.user_id == current_user.id
    ).subquery()
    
    # Soft delete user's messages using subquery
    messages_updated = db.query(Message).filter(
        Message.session_id.in_(user_session_ids),
        Message.is_deleted == False
    ).update({
        "is_deleted": True,
        "deleted_at": now
    }, synchronize_session=False)
    
    # Soft delete user's wellness logs
    wellness_updated = db.query(WellnessLog).filter(
        WellnessLog.patient_id == current_user.id,
        WellnessLog.is_deleted == False
    ).update({
        "is_deleted": True,
        "deleted_at": now
    }, synchronize_session=False)
    
    # Mark user as deleted (keep for audit purposes)
    current_user.is_deleted = True
    current_user.deleted_at = now
    
    db.commit()
    
    # Log the deletion action
    log_action(db, "account_deleted", str(current_user.id), {
        "reason": request.reason,
        "messages_deleted": messages_updated,
        "wellness_logs_deleted": wellness_updated
    })
    
    return {
        "message": "Account and all associated data have been deleted",
        "deleted_items": {
            "messages": messages_updated,
            "wellness_logs": wellness_updated
        }
    }

@router.delete("/messages")
def delete_user_messages(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Soft delete all user messages"""
    
    now = datetime.now()
    
    # Get user's session IDs first
    user_session_ids = db.query(SessionModel.id).filter(
        SessionModel.user_id == current_user.id
    ).subquery()
    
    # Update messages using subquery
    messages_updated = db.query(Message).filter(
        Message.session_id.in_(user_session_ids),
        Message.is_deleted == False
    ).update({
        "is_deleted": True,
        "deleted_at": now
    }, synchronize_session=False)
    
    db.commit()
    
    # Log the deletion action
    log_action(db, "messages_deleted", str(current_user.id), {
        "messages_count": messages_updated
    })
    
    return {
        "message": f"Deleted {messages_updated} messages",
        "deleted_count": messages_updated
    }

@router.delete("/account")
def delete_user_account_delete(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """DELETE method for account deletion"""
    now = datetime.now()
    
    # Get user's session IDs first
    user_session_ids = db.query(SessionModel.id).filter(
        SessionModel.user_id == current_user.id
    ).subquery()
    
    # Soft delete user's messages using subquery
    messages_updated = db.query(Message).filter(
        Message.session_id.in_(user_session_ids),
        Message.is_deleted == False
    ).update({
        "is_deleted": True,
        "deleted_at": now
    }, synchronize_session=False)
    
    # Soft delete user's wellness logs
    wellness_updated = db.query(WellnessLog).filter(
        WellnessLog.patient_id == current_user.id,
        WellnessLog.is_deleted == False
    ).update({
        "is_deleted": True,
        "deleted_at": now
    }, synchronize_session=False)
    
    # Mark user as deleted
    current_user.is_deleted = True
    current_user.deleted_at = now
    
    db.commit()
    
    # Log the deletion action
    log_action(db, "account_deleted", str(current_user.id), {
        "reason": "User requested deletion via DELETE method",
        "messages_deleted": messages_updated,
        "wellness_logs_deleted": wellness_updated
    })
    
    return {
        "message": "Account and all associated data have been deleted",
        "deleted_items": {
            "messages": messages_updated,
            "wellness_logs": wellness_updated
        }
    }

@router.get("/retention-status")
def get_retention_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's data retention status"""
    
    # Get retention policies (would be from settings table in production)
    message_retention_days = 365
    wellness_retention_days = 730
    
    # Calculate cutoff dates
    message_cutoff = datetime.now() - timedelta(days=message_retention_days)
    wellness_cutoff = datetime.now() - timedelta(days=wellness_retention_days)
    
    # Count data eligible for deletion
    old_messages = db.query(Message).join(SessionModel).filter(
        SessionModel.user_id == current_user.id,
        Message.created_at < message_cutoff,
        Message.is_deleted == False
    ).count()
    
    old_wellness = db.query(WellnessLog).filter(
        WellnessLog.patient_id == current_user.id,
        WellnessLog.created_at < wellness_cutoff,
        WellnessLog.is_deleted == False
    ).count()
    
    return {
        "retention_policies": {
            "messages_days": message_retention_days,
            "wellness_days": wellness_retention_days
        },
        "data_eligible_for_deletion": {
            "old_messages": old_messages,
            "old_wellness_logs": old_wellness
        },
        "next_cleanup_date": (datetime.now() + timedelta(days=1)).isoformat()
    }