from fastapi import APIRouter, Depends
from pydantic import BaseModel
from ..models import User
from ..deps import get_current_user, require_role
from ..services.guardrails import sanitize_input, validate_response, is_safe_content

router = APIRouter(prefix="/guardrails", tags=["guardrails"])

class ContentCheck(BaseModel):
    text: str

class ContentResponse(BaseModel):
    original_text: str
    sanitized_text: str
    is_safe: bool
    warnings: list = []

@router.post("/sanitize", response_model=ContentResponse)
def sanitize_content(
    content: ContentCheck,
    current_user: User = Depends(get_current_user)
):
    """Sanitize content for PII and harmful material"""
    sanitized = sanitize_input(content.text)
    is_safe = is_safe_content(content.text)
    
    warnings = []
    if sanitized != content.text:
        warnings.append("Content has been sanitized for privacy/safety")
    if not is_safe:
        warnings.append("Content flagged for safety review")
    
    return ContentResponse(
        original_text=content.text,
        sanitized_text=sanitized,
        is_safe=is_safe,
        warnings=warnings
    )

@router.post("/validate", response_model=ContentResponse)
def validate_content(
    content: ContentCheck,
    admin_user: User = Depends(require_role("admin"))
):
    """Validate AI response content (admin only)"""
    validated = validate_response(content.text)
    is_safe = is_safe_content(content.text)
    
    warnings = []
    if validated != content.text:
        warnings.append("Response has been filtered for safety")
    
    return ContentResponse(
        original_text=content.text,
        sanitized_text=validated,
        is_safe=is_safe,
        warnings=warnings
    )