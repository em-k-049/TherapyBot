from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from ..models import User
from ..deps import get_db, get_current_user
from ..services.analytics import (
    get_case_trends, 
    get_escalation_patterns, 
    get_consultant_activity,
    get_risk_score_distribution,
    get_daily_activity
)

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/trends", response_model=Dict[str, Any])
def case_trends(
    period: str = Query("week", regex="^(week|month)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get escalation trends over time (consultants and admins only)"""
    if current_user.role.name not in ["consultant", "admin"]:
        return {"error": "Access denied"}
    
    return get_case_trends(db, period)

@router.get("/patterns", response_model=Dict[str, Any])
def escalation_patterns(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get common crisis trigger patterns (consultants and admins only)"""
    if current_user.role.name not in ["consultant", "admin"]:
        return {"error": "Access denied"}
    
    return get_escalation_patterns(db)

@router.get("/consultant-activity", response_model=Dict[str, Any])
def consultant_activity(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get consultant intervention activity (admins only)"""
    if current_user.role.name != "admin":
        return {"error": "Access denied"}
    
    return get_consultant_activity(db)

@router.get("/risk-distribution", response_model=Dict[str, Any])
def risk_distribution(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get risk score distribution (consultants and admins only)"""
    if current_user.role.name not in ["consultant", "admin"]:
        return {"error": "Access denied"}
    
    return get_risk_score_distribution(db)

@router.get("/daily-activity", response_model=Dict[str, Any])
def daily_activity(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get daily message and escalation activity (consultants and admins only)"""
    if current_user.role.name not in ["consultant", "admin"]:
        return {"error": "Access denied"}
    
    return get_daily_activity(db)

@router.get("/dashboard", response_model=Dict[str, Any])
def dashboard_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get complete dashboard data (consultants and admins only)"""
    if current_user.role.name not in ["consultant", "admin"]:
        return {"error": "Access denied"}
    
    return {
        "trends": get_case_trends(db, "week"),
        "patterns": get_escalation_patterns(db),
        "risk_distribution": get_risk_score_distribution(db),
        "daily_activity": get_daily_activity(db),
        "consultant_activity": get_consultant_activity(db) if current_user.role.name == "admin" else None
    }