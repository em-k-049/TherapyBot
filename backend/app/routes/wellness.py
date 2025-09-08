from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID
from ..models import WellnessLog, User
from ..deps import get_db, get_current_user
from ..services.audit import log_action
from ..services.metrics import record_wellness_log

router = APIRouter(prefix="/wellness", tags=["wellness"])

class WellnessLogCreate(BaseModel):
    mood_score: int = Field(..., ge=1, le=10)
    note: str = None

class WellnessLogRead(BaseModel):
    id: UUID
    mood_score: int
    note: str = None
    created_at: datetime
    
    class Config:
        from_attributes = True

@router.post("/log", response_model=WellnessLogRead)
def create_wellness_log(
    wellness_data: WellnessLogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create wellness log entry (patients only)"""
    if current_user.role.name != "patient":
        raise HTTPException(status_code=403, detail="Only patients can create wellness logs")
    
    wellness_log = WellnessLog(
        patient_id=current_user.id,
        mood_score=wellness_data.mood_score
    )
    
    # Use encrypted setter for note
    if wellness_data.note:
        wellness_log.set_note(wellness_data.note)
    
    db.add(wellness_log)
    db.commit()
    db.refresh(wellness_log)
    
    # Record metrics and log action
    record_wellness_log()
    log_action(db, "wellness_log_created", str(current_user.id), {"mood_score": wellness_data.mood_score})
    
    return WellnessLogRead(
        id=wellness_log.id,
        mood_score=wellness_log.mood_score,
        note=wellness_log.get_note(),
        created_at=wellness_log.created_at
    )

@router.get("/logs", response_model=List[WellnessLogRead])
def get_wellness_logs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's wellness logs"""
    if current_user.role.name == "patient":
        # Patients see only their own logs
        logs = db.query(WellnessLog).filter(WellnessLog.patient_id == current_user.id).order_by(WellnessLog.created_at.desc()).all()
    elif current_user.role.name in ["consultant", "admin"]:
        # Consultants/admins see all logs
        logs = db.query(WellnessLog).order_by(WellnessLog.created_at.desc()).all()
    else:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return [
        WellnessLogRead(
            id=log.id,
            mood_score=log.mood_score,
            note=log.get_note(),
            created_at=log.created_at
        )
        for log in logs
    ]

@router.delete("/delete-all")
def delete_all_wellness_data(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete all wellness data for current user (patients only)"""
    if current_user.role.name != "patient":
        raise HTTPException(status_code=403, detail="Only patients can delete their wellness data")
    
    deleted_count = db.query(WellnessLog).filter(WellnessLog.patient_id == current_user.id).delete()
    db.commit()
    
    # Log action
    log_action(db, "wellness_data_deleted", str(current_user.id), {"deleted_count": deleted_count})
    
    return {"message": f"Deleted {deleted_count} wellness entries", "deleted_count": deleted_count}

@router.delete("/logs/{log_id}")
def delete_wellness_log(
    log_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete specific wellness log entry"""
    wellness_log = db.query(WellnessLog).filter(WellnessLog.id == log_id).first()
    
    if not wellness_log:
        raise HTTPException(status_code=404, detail="Wellness log not found")
    
    # Patients can only delete their own logs
    if current_user.role.name == "patient" and wellness_log.patient_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Consultants/admins can delete any log
    if current_user.role.name not in ["patient", "consultant", "admin"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    db.delete(wellness_log)
    db.commit()
    
    # Log action
    log_action(db, "wellness_log_deleted", str(current_user.id), {"log_id": str(log_id)})
    
    return {"message": "Wellness log deleted successfully"}