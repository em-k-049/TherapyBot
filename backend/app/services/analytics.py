from sqlalchemy.orm import Session
from sqlalchemy import func, extract, and_
from datetime import datetime, timedelta
from typing import Dict, List, Any
from ..models import Message, User, Session as SessionModel
import json

def get_case_trends(db: Session, period: str = "week") -> Dict[str, Any]:
    """Get escalation trends over time"""
    if period == "week":
        # Last 12 weeks
        weeks_ago = datetime.now() - timedelta(weeks=12)
        query = db.query(
            extract('week', Message.created_at).label('period'),
            extract('year', Message.created_at).label('year'),
            func.count(Message.id).label('count')
        ).filter(
            Message.is_escalated == True,
            Message.created_at >= weeks_ago
        ).group_by('period', 'year').order_by('year', 'period')
        
        period_label = "Week"
    else:  # month
        # Last 12 months
        months_ago = datetime.now() - timedelta(days=365)
        query = db.query(
            extract('month', Message.created_at).label('period'),
            extract('year', Message.created_at).label('year'),
            func.count(Message.id).label('count')
        ).filter(
            Message.is_escalated == True,
            Message.created_at >= months_ago
        ).group_by('period', 'year').order_by('year', 'period')
        
        period_label = "Month"
    
    results = query.all()
    
    return {
        "chart_type": "line",
        "title": f"Escalations per {period_label}",
        "labels": [f"{int(r.year)}-{int(r.period):02d}" for r in results],
        "datasets": [{
            "label": "Escalations",
            "data": [r.count for r in results],
            "borderColor": "#e74c3c",
            "backgroundColor": "rgba(231, 76, 60, 0.1)"
        }]
    }

def get_escalation_patterns(db: Session) -> Dict[str, Any]:
    """Categorize common crisis triggers from risk tags"""
    # Get escalated messages with risk tags
    escalated_messages = db.query(Message).filter(
        Message.is_escalated == True,
        Message.risk_tags.isnot(None)
    ).all()
    
    # Count trigger categories
    trigger_counts = {}
    for msg in escalated_messages:
        if msg.risk_tags:
            for tag in msg.risk_tags:
                if ':' in tag:
                    category = tag.split(':')[1]
                    trigger_counts[category] = trigger_counts.get(category, 0) + 1
    
    # Sort by frequency
    sorted_triggers = sorted(trigger_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    
    return {
        "chart_type": "doughnut",
        "title": "Common Crisis Triggers",
        "labels": [trigger[0].replace('_', ' ').title() for trigger in sorted_triggers],
        "datasets": [{
            "data": [trigger[1] for trigger in sorted_triggers],
            "backgroundColor": [
                "#e74c3c", "#f39c12", "#f1c40f", "#27ae60", "#3498db",
                "#9b59b6", "#e67e22", "#95a5a6", "#34495e", "#16a085"
            ]
        }]
    }

def get_consultant_activity(db: Session) -> Dict[str, Any]:
    """Track consultant interventions and activity"""
    # Mock consultant activity data (in production, track actual interventions)
    consultants = db.query(User).filter(
        User.role.has(name="consultant")
    ).all()
    
    # Simulate activity data
    activity_data = []
    for consultant in consultants:
        # In production, track actual interventions from logs/database
        activity_data.append({
            "consultant": consultant.username,
            "cases_handled": len(consultant.username) * 3,  # Mock data
            "response_time_avg": 15 + (len(consultant.username) % 10),  # Mock avg minutes
            "escalations_resolved": len(consultant.username) * 2
        })
    
    return {
        "chart_type": "bar",
        "title": "Consultant Activity",
        "labels": [c["consultant"] for c in activity_data],
        "datasets": [
            {
                "label": "Cases Handled",
                "data": [c["cases_handled"] for c in activity_data],
                "backgroundColor": "#3498db"
            },
            {
                "label": "Escalations Resolved",
                "data": [c["escalations_resolved"] for c in activity_data],
                "backgroundColor": "#27ae60"
            }
        ]
    }

def get_risk_score_distribution(db: Session) -> Dict[str, Any]:
    """Get distribution of risk scores"""
    risk_ranges = [
        ("Low (0.0-0.4)", 0.0, 0.4),
        ("Moderate (0.4-0.6)", 0.4, 0.6),
        ("High (0.6-0.8)", 0.6, 0.8),
        ("Critical (0.8-1.0)", 0.8, 1.0)
    ]
    
    counts = []
    for label, min_score, max_score in risk_ranges:
        count = db.query(Message).filter(
            and_(
                Message.risk_score >= min_score,
                Message.risk_score < max_score if max_score < 1.0 else Message.risk_score <= max_score,
                Message.is_escalated == True
            )
        ).count()
        counts.append(count)
    
    return {
        "chart_type": "bar",
        "title": "Risk Score Distribution",
        "labels": [r[0] for r in risk_ranges],
        "datasets": [{
            "label": "Messages",
            "data": counts,
            "backgroundColor": ["#27ae60", "#f1c40f", "#f39c12", "#e74c3c"]
        }]
    }

def get_daily_activity(db: Session) -> Dict[str, Any]:
    """Get daily message and escalation activity for last 30 days"""
    thirty_days_ago = datetime.now() - timedelta(days=30)
    
    daily_stats = db.query(
        func.date(Message.created_at).label('date'),
        func.count(Message.id).label('total_messages'),
        func.sum(func.cast(Message.is_escalated, db.bind.dialect.name == 'postgresql' and 'INTEGER' or 'SIGNED')).label('escalations')
    ).filter(
        Message.created_at >= thirty_days_ago
    ).group_by(func.date(Message.created_at)).order_by('date').all()
    
    return {
        "chart_type": "line",
        "title": "Daily Activity (Last 30 Days)",
        "labels": [str(stat.date) for stat in daily_stats],
        "datasets": [
            {
                "label": "Total Messages",
                "data": [stat.total_messages for stat in daily_stats],
                "borderColor": "#3498db",
                "backgroundColor": "rgba(52, 152, 219, 0.1)"
            },
            {
                "label": "Escalations",
                "data": [stat.escalations or 0 for stat in daily_stats],
                "borderColor": "#e74c3c",
                "backgroundColor": "rgba(231, 76, 60, 0.1)"
            }
        ]
    }