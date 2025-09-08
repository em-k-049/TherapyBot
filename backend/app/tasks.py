from .celery_app import celery_app
from .services.notifications import send_email, send_sms
import logging

logger = logging.getLogger(__name__)

@celery_app.task
def send_email_task(to_email: str, subject: str, body: str):
    """Async task to send email"""
    try:
        success = send_email(to_email, subject, body)
        if success:
            logger.info(f"Email sent successfully to {to_email}")
            return {"status": "success", "recipient": to_email}
        else:
            logger.error(f"Failed to send email to {to_email}")
            return {"status": "failed", "recipient": to_email}
    except Exception as e:
        logger.error(f"Email task error: {e}")
        return {"status": "error", "error": str(e)}

@celery_app.task
def send_sms_task(to_number: str, message: str):
    """Async task to send SMS"""
    try:
        success = send_sms(to_number, message)
        if success:
            logger.info(f"SMS sent successfully to {to_number}")
            return {"status": "success", "recipient": to_number}
        else:
            logger.error(f"Failed to send SMS to {to_number}")
            return {"status": "failed", "recipient": to_number}
    except Exception as e:
        logger.error(f"SMS task error: {e}")
        return {"status": "error", "error": str(e)}

@celery_app.task
def escalate_case_task(user_id: str, message_content: str, risk_score: float):
    """Async task to handle case escalation"""
    try:
        # Send email to consultants
        consultant_email = "consultant@therapybot.com"  # Should be from config
        subject = f"URGENT: Patient Escalation Alert - Risk Score: {risk_score}"
        body = f"""
        URGENT ESCALATION REQUIRED
        
        Patient ID: {user_id}
        Risk Score: {risk_score}
        Message: {message_content}
        
        Please contact the patient immediately.
        """
        
        email_result = send_email(consultant_email, subject, body)
        
        # Send SMS alert
        consultant_phone = "+1234567890"  # Should be from config
        sms_message = f"URGENT: Patient escalation detected. Risk score: {risk_score}. Check email for details."
        sms_result = send_sms(consultant_phone, sms_message)
        
        logger.info(f"Escalation processed for user {user_id}: email={email_result}, sms={sms_result}")
        
        return {
            "status": "completed",
            "user_id": user_id,
            "email_sent": email_result,
            "sms_sent": sms_result
        }
        
    except Exception as e:
        logger.error(f"Escalation task error: {e}")
        return {"status": "error", "error": str(e)}