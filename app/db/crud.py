from sqlalchemy.orm import Session
from . import models

# ---------------------------
# USERS
# ---------------------------

def create_user(db: Session, username: str, email: str, password_hash: str):
    user = models.User(username=username, email=email, password_hash=password_hash)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_user_by_id(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def delete_user(db: Session, user_id: int):
    user = get_user_by_id(db, user_id)
    if user:
        db.delete(user)
        db.commit()
        return True
    return False

# ---------------------------
# SESSIONS
# ---------------------------

def create_session(db: Session, user_id: int):
    session = models.Session(user_id=user_id)
    db.add(session)
    db.commit()
    db.refresh(session)
    return session

def end_session(db: Session, session_id: int):
    session = db.query(models.Session).filter(models.Session.id == session_id).first()
    if session:
        from datetime import datetime
        session.ended_at = datetime.utcnow()
        db.commit()
        db.refresh(session)
        return session
    return None

def get_sessions_by_user(db: Session, user_id: int):
    return db.query(models.Session).filter(models.Session.user_id == user_id).all()

# ---------------------------
# MESSAGES
# ---------------------------

def add_message(db: Session, session_id: int, sender: str, content: str):
    msg = models.Message(session_id=session_id, sender=sender, content=content)
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg

def get_messages_by_session(db: Session, session_id: int):
    return db.query(models.Message).filter(models.Message.session_id == session_id).all()

# ---------------------------
# WELLNESS LOGS
# ---------------------------

def create_wellness_log(db: Session, user_id: int, mood: str, energy_level: int, notes: str = None):
    log = models.WellnessLog(user_id=user_id, mood=mood, energy_level=energy_level, notes=notes)
    db.add(log)
    db.commit()
    db.refresh(log)
    return log

def get_wellness_logs(db: Session, user_id: int):
    return db.query(models.WellnessLog).filter(models.WellnessLog.user_id == user_id).all()
