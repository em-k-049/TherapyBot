from fastapi import APIRouter
from ..db import get_db
from sqlalchemy.orm import Session
from sqlalchemy import text
from fastapi import Depends
from ..services.vertex_ai import get_vertex_client

router = APIRouter()

@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    health_status = {"status": "healthy"}
    
    try:
        # Test database connection
        db.execute(text("SELECT 1"))
        health_status["database"] = "connected"
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["database"] = f"error: {str(e)}"
    
    # Test Vertex AI connection
    try:
        client = get_vertex_client()
        if client.model is not None:
            health_status["vertex_ai"] = "connected"
        else:
            health_status["vertex_ai"] = "fallback_mode"
    except Exception as e:
        health_status["vertex_ai"] = f"error: {str(e)}"
    
    return health_status