from fastapi import APIRouter, Depends
from pydantic import BaseModel
from ..models import User
from ..deps import require_role
from ..services.notifications import send_email, send_sms

router = APIRouter(prefix="/notifications", tags=["notifications"])

class EmailRequest(BaseModel):
    to_email: str
    subject: str
    body: str

class SMSRequest(BaseModel):
    to_number: str
    message: str

@router.post("/email")
def send_email_notification(
    request: EmailRequest,
    admin_user: User = Depends(require_role("admin"))
):
    """Send email notification async (admin only)"""
    from ..tasks import send_email_task
    task = send_email_task.delay(request.to_email, request.subject, request.body)
    return {"task_id": task.id, "status": "queued"}

@router.post("/sms")
def send_sms_notification(
    request: SMSRequest,
    admin_user: User = Depends(require_role("admin"))
):
    """Send SMS notification async (admin only)"""
    from ..tasks import send_sms_task
    task = send_sms_task.delay(request.to_number, request.message)
    return {"task_id": task.id, "status": "queued"}