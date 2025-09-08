from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime, date
from uuid import UUID
from ..models import Message, User, Session as SessionModel
from ..deps import get_db, require_role, get_current_user
# from ..tasks import send_email_task, send_sms_task  # Disabled for MVP
from ..services.audit import log_escalation_resolved

router = APIRouter(prefix="/escalations", tags=["escalations"])

class EscalationRead(BaseModel):
    id: UUID
    content: str
    created_at: datetime
    session_id: UUID
    user_id: UUID
    username: str
    risk_score: float = None
    risk_tags: list = None
    
    class Config:
        from_attributes = True

class NotificationRequest(BaseModel):
    escalation_ids: List[UUID]
    message: str = None

@router.get("/", response_model=List[EscalationRead])
def get_escalations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    risk_score_min: Optional[float] = Query(None, ge=0.0, le=1.0),
    patient: Optional[str] = Query(None),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None)
):
    # Only consultants and admins can view escalations
    if current_user.role.name not in ["consultant", "admin"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    query = db.query(Message).join(
        SessionModel, Message.session_id == SessionModel.id
    ).join(
        User, SessionModel.user_id == User.id
    ).filter(
        Message.is_escalated == True
    )
    
    # Apply filters
    if risk_score_min is not None:
        query = query.filter(Message.risk_score >= risk_score_min)
    
    if patient:
        query = query.filter(User.username.ilike(f"%{patient}%"))
    
    if date_from:
        query = query.filter(Message.created_at >= date_from)
    
    if date_to:
        query = query.filter(Message.created_at <= date_to)
    
    escalated_messages = query.order_by(Message.risk_score.desc()).all()
    
    return [
        EscalationRead(
            id=msg.id,
            content=msg.get_content(),
            created_at=msg.created_at,
            session_id=msg.session_id,
            user_id=msg.session.user_id,
            username=msg.session.user.username,
            risk_score=msg.risk_score,
            risk_tags=msg.risk_tags
        )
        for msg in escalated_messages
    ]

@router.post("/notify")
def notify_escalations(
    notification_request: NotificationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Only consultants and admins can send notifications
    if current_user.role.name not in ["consultant", "admin"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get escalated messages
    escalated_messages = db.query(Message).join(
        SessionModel, Message.session_id == SessionModel.id
    ).join(
        User, SessionModel.user_id == User.id
    ).filter(
        Message.id.in_(notification_request.escalation_ids),
        Message.is_escalated == True
    ).all()
    
    if not escalated_messages:
        raise HTTPException(status_code=404, detail="No escalated messages found")
    
    # Send notifications for each escalation
    notification_tasks = []
    
    for msg in escalated_messages:
        # Email notification
        subject = f"URGENT: Patient Escalation Alert - {msg.session.user.username}"
        body = notification_request.message or f"""
URGENT ESCALATION REQUIRED

Patient: {msg.session.user.username}
Risk Score: {msg.risk_score or 'N/A'}
Message: {msg.get_content()}
Time: {msg.created_at}

Please contact the patient immediately.
"""
        
        # TODO: Implement direct email/SMS for MVP (without Celery)
        # For now, just log the notification
        print(f"NOTIFICATION: {subject}")
        print(f"BODY: {body}")
        
        # SMS notification for high-risk cases
        if (msg.risk_score or 0) >= 0.8:
            sms_message = f"URGENT: Patient {msg.session.user.username} escalation detected. Risk: {msg.risk_score:.2f}. Check email."
            print(f"SMS: {sms_message}")
        
        notification_tasks.append(f"logged-notification-{msg.id}")
    
    # Log escalation resolution for each handled case
    for msg in escalated_messages:
        log_escalation_resolved(db, current_user, str(msg.id), "Notification sent to consultants")
    
    return {
        "message": f"Notifications logged for {len(escalated_messages)} escalations",
        "notification_ids": notification_tasks,
        "escalations_notified": len(escalated_messages)
    }