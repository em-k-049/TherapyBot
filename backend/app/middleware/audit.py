from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.orm import Session
from ..models import AuditLog, User
from ..db import SessionLocal
from ..security import decode_access_token
from ..services.logging import log_api_request, log_audit_event
from ..services.metrics import record_request
import json
import time
from datetime import datetime

class AuditMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.excluded_paths = {
            "/docs", "/redoc", "/openapi.json", "/favicon.ico",
            "/health", "/metrics"  # Health check and monitoring endpoints
        }
        self.excluded_methods = {"GET", "OPTIONS", "HEAD"}

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Skip audit logging for excluded paths and methods
        if (request.url.path in self.excluded_paths or 
            any(request.url.path.startswith(path) for path in self.excluded_paths) or
            request.method in self.excluded_methods):
            return await call_next(request)
        
        # Get user info from token
        user_id = None
        user_role = None
        
        try:
            auth_header = request.headers.get("authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]
                payload = decode_access_token(token)
                if payload:
                    user_id = payload.get("user_id")
                    user_role = payload.get("role")
        except Exception:
            pass  # Continue without user info if token invalid
        
        # Process request
        response = await call_next(request)
        
        # Log only successful operations (2xx status codes)
        if 200 <= response.status_code < 300:
            try:
                # Prepare audit log data
                action = self._get_action_from_route(request.method, request.url.path)
                metadata = {
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "user_role": user_role,
                    "duration_ms": round((time.time() - start_time) * 1000, 2)
                }
                
                # Add query parameters if present
                if request.query_params:
                    metadata["query_params"] = dict(request.query_params)
                
                # Save audit log asynchronously
                self._save_audit_log(user_id, action, metadata)
                
            except Exception as e:
                # Don't fail the request if audit logging fails
                print(f"Audit logging error: {e}")
        
        return response
    
    def _get_action_from_route(self, method: str, path: str) -> str:
        """Extract meaningful action from HTTP method and path"""
        
        # Authentication actions
        if "/auth/login" in path:
            return "user_login"
        elif "/auth/signup" in path:
            return "user_signup"
        elif "/auth/2fa" in path:
            return "2fa_setup" if "setup" in path else "2fa_verify"
        
        # Message actions
        elif "/messages" in path and method == "POST":
            return "message_sent"
        
        # Escalation actions
        elif "/escalations" in path:
            if method == "POST" and "notify" in path:
                return "escalation_notification_sent"
            else:
                return "escalation_viewed"
        
        # Wellness actions
        elif "/wellness/log" in path and method == "POST":
            return "wellness_log_created"
        elif "/wellness/delete" in path:
            return "wellness_data_deleted"
        
        # Admin actions
        elif "/admin" in path:
            if "retention" in path:
                return "retention_settings_updated"
            elif "cleanup" in path:
                return "data_cleanup_executed"
            else:
                return "admin_action"
        
        # User management
        elif "/users" in path and "role" in path:
            return "user_role_changed"
        
        # Translation actions
        elif "/translation" in path:
            return "translation_used"
        
        # Default action based on method
        return f"{method.lower()}_request"
    
    def _save_audit_log(self, user_id: str, action: str, metadata: dict):
        """Save audit log to database"""
        try:
            db = SessionLocal()
            
            audit_log = AuditLog(
                user_id=user_id,
                action=action,
                audit_metadata=metadata
            )
            
            db.add(audit_log)
            db.commit()
            db.close()
            
        except Exception as e:
            print(f"Failed to save audit log: {e}")
            # Ensure database connection is closed
            try:
                db.close()
            except:
                pass