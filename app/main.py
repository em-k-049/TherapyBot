from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from app.db import crud, models
from app.db.database import get_db
from app.db.redis_client import redis_client
from app.tasks.celery_app import celery, example_task

app = FastAPI(title="TherapyBot API")

# ---------------------------
# Pydantic models
# ---------------------------
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class MessageCreate(BaseModel):
    sender: str
    content: str

class WellnessCreate(BaseModel):
    mood: str
    energy_level: int
    notes: str | None = None

class TaskPayload(BaseModel):
    message: str

# ---------------------------
# Root
# ---------------------------
@app.get("/")
def read_root():
    return {"message": "Welcome to TherapyBot API"}

# ---------------------------
# Users
# ---------------------------
@app.post("/users/")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    if crud.get_user_by_email(db, email=user.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    if crud.get_user_by_id(db, user_id=user.username):
        raise HTTPException(status_code=400, detail="Username already taken")
    return crud.create_user(db, user.username, user.email, user.password)

@app.get("/users/{user_id}")
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_id(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.get("/users/{user_id}/cached")
def read_user_cached(user_id: int, db: Session = Depends(get_db)):
    cache_key = f"user:{user_id}"
    cached = redis_client.get(cache_key)
    if cached:
        return {"cached": True, "data": eval(cached)}
    db_user = crud.get_user_by_id(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    data = {
        "id": db_user.id,
        "username": db_user.username,
        "email": db_user.email,
        "created_at": str(db_user.created_at)
    }
    redis_client.setex(cache_key, 60, str(data))
    return {"cached": False, "data": data}

# ---------------------------
# Sessions
# ---------------------------
@app.post("/sessions/")
def create_session(user_id: int, db: Session = Depends(get_db)):
    return crud.create_session(db, user_id)

@app.post("/sessions/{session_id}/end")
def end_session(session_id: int, db: Session = Depends(get_db)):
    session = crud.end_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session

# ---------------------------
# Messages
# ---------------------------
@app.post("/sessions/{session_id}/messages")
def add_message(session_id: int, msg: MessageCreate, db: Session = Depends(get_db)):
    return crud.add_message(db, session_id, msg.sender, msg.content)

@app.get("/sessions/{session_id}/messages")
def get_messages(session_id: int, db: Session = Depends(get_db)):
    return crud.get_messages_by_session(db, session_id)

# ---------------------------
# Wellness Logs
# ---------------------------
@app.post("/users/{user_id}/wellness")
def add_wellness_log(user_id: int, log: WellnessCreate, db: Session = Depends(get_db)):
    return crud.create_wellness_log(db, user_id, log.mood, log.energy_level, log.notes)

@app.get("/users/{user_id}/wellness")
def get_wellness_logs(user_id: int, db: Session = Depends(get_db)):
    return crud.get_wellness_logs(db, user_id)

# ---------------------------
# Redis caching
# ---------------------------
@app.get("/cache/{key}")
def get_cache(key: str):
    value = redis_client.get(key)
    if value:
        return {"key": key, "value": value}
    raise HTTPException(status_code=404, detail="Key not found")

@app.post("/cache/{key}")
def set_cache(key: str, value: str):
    redis_client.set(key, value)
    return {"key": key, "value": value}

# ---------------------------
# Celery tasks
# ---------------------------
@app.post("/tasks/example")
def run_example_task(payload: TaskPayload):
    task = example_task.delay(payload.message)
    return {"task_id": task.id, "status": "Task submitted"}

@app.get("/tasks/status/{task_id}")
def get_task_status(task_id: str):
    task_result = celery.AsyncResult(task_id)
    return {
        "task_id": task_id,
        "status": task_result.status,
        "result": task_result.result if task_result.ready() else None
    }

# ---------------------------
# Cached Sessions
# ---------------------------
@app.get("/users/{user_id}/sessions/cached")
def get_user_sessions_cached(user_id: int, db: Session = Depends(get_db)):
    cache_key = f"sessions:{user_id}"
    cached = redis_client.get(cache_key)
    if cached:
        return {"cached": True, "data": eval(cached)}
    sessions = crud.get_sessions_by_user(db, user_id)
    data = [
        {"id": s.id, "started_at": str(s.started_at), "ended_at": str(s.ended_at)}
        for s in sessions
    ]
    redis_client.setex(cache_key, 60, str(data))
    return {"cached": False, "data": data}


# ---------------------------
# Cached Messages by Session
# ---------------------------
@app.get("/sessions/{session_id}/messages/cached")
def get_messages_cached(session_id: int, db: Session = Depends(get_db)):
    cache_key = f"messages:{session_id}"
    cached = redis_client.get(cache_key)
    if cached:
        return {"cached": True, "data": eval(cached)}
    messages = crud.get_messages_by_session(db, session_id)
    data = [
        {"id": m.id, "sender": m.sender, "content": m.content, "timestamp": str(m.timestamp)}
        for m in messages
    ]
    redis_client.setex(cache_key, 60, str(data))
    return {"cached": False, "data": data}


# ---------------------------
# Cached Wellness Logs
# ---------------------------
@app.get("/users/{user_id}/wellness/cached")
def get_wellness_cached(user_id: int, db: Session = Depends(get_db)):
    cache_key = f"wellness:{user_id}"
    cached = redis_client.get(cache_key)
    if cached:
        return {"cached": True, "data": eval(cached)}
    logs = crud.get_wellness_logs(db, user_id)
    data = [
        {
            "id": l.id,
            "mood": l.mood,
            "energy_level": l.energy_level,
            "notes": l.notes,
            "created_at": str(l.created_at)
        }
        for l in logs
    ]
    redis_client.setex(cache_key, 60, str(data))
    return {"cached": False, "data": data}
