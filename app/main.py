from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from app.db import database, crud, models
from app.db.redis_client import r

app = FastAPI(title="TherapyBot API")

# Dependency to get DB session
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Root endpoint
@app.get("/")
def read_root():
    return {"message": "TherapyBot backend is running!"}

# Example: Create a new user
@app.post("/users/")
def create_user(username: str, email: str, password: str, db: Session = Depends(get_db)):
    existing = crud.get_user_by_email(db, email)
    if existing:
        return {"error": "User already exists"}
    user = crud.create_user(db, username, email, password)
    return {"id": user.id, "username": user.username, "email": user.email}

# Example: Set/Get Redis cache
@app.post("/cache/")
def set_cache(key: str, value: str):
    r.set(key, value)
    return {"status": "OK"}

@app.get("/cache/")
def get_cache(key: str):
    value = r.get(key)
    return {"key": key, "value": value}
