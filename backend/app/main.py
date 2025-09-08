from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import auth, users, messages, escalation, voice, notifications, translation, guardrails, analytics, wellness, admin, privacy, health, chat
from .models import Base
from .db import engine
from .middleware import AuditMiddleware
from .services.metrics import get_metrics
from .startup_checks import run_startup_checks
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="TherapyBot API")

# Run startup checks
@app.on_event("startup")
async def startup_event():
    logger.info("Starting TherapyBot API...")
    run_startup_checks()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Add audit logging middleware
app.add_middleware(AuditMiddleware)

# Add metrics endpoint
@app.get("/metrics")
def metrics():
    return get_metrics()

# Add health endpoint
@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "TherapyBot API"}

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(messages.router)
app.include_router(escalation.router)
app.include_router(voice.router)
app.include_router(notifications.router)
app.include_router(translation.router)
app.include_router(guardrails.router)
app.include_router(analytics.router)
app.include_router(wellness.router)
app.include_router(admin.router)
app.include_router(privacy.router)
app.include_router(health.router)
app.include_router(chat.router)