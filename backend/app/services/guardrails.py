import re
from typing import List

# PII patterns
EMAIL_PATTERN = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
PHONE_PATTERN = re.compile(r'\b(?:\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b')
SSN_PATTERN = re.compile(r'\b\d{3}-?\d{2}-?\d{4}\b')
CREDIT_CARD_PATTERN = re.compile(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b')
ADDRESS_PATTERN = re.compile(r'\b\d+\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Lane|Ln|Boulevard|Blvd)\b', re.IGNORECASE)

# Unsafe content blocklist
UNSAFE_SUGGESTIONS = [
    'kill yourself', 'end your life', 'commit suicide', 'hurt yourself',
    'self harm', 'overdose', 'jump off', 'hang yourself', 'cut yourself',
    'you should die', 'better off dead', 'no hope', 'give up completely'
]

HARMFUL_KEYWORDS = [
    'violence', 'weapon', 'bomb', 'terrorist', 'illegal drugs',
    'prescription abuse', 'self-medication', 'unprescribed medication'
]

def sanitize_input(message: str) -> str:
    """Remove PII and harmful content from user input"""
    sanitized = message
    
    # Remove PII
    sanitized = EMAIL_PATTERN.sub('[EMAIL_REDACTED]', sanitized)
    sanitized = PHONE_PATTERN.sub('[PHONE_REDACTED]', sanitized)
    sanitized = SSN_PATTERN.sub('[SSN_REDACTED]', sanitized)
    sanitized = CREDIT_CARD_PATTERN.sub('[CARD_REDACTED]', sanitized)
    sanitized = ADDRESS_PATTERN.sub('[ADDRESS_REDACTED]', sanitized)
    
    # Remove specific harmful content
    for keyword in HARMFUL_KEYWORDS:
        if keyword.lower() in sanitized.lower():
            sanitized = re.sub(re.escape(keyword), '[CONTENT_FILTERED]', sanitized, flags=re.IGNORECASE)
    
    return sanitized.strip()

def validate_response(response: str) -> str:
    """Validate AI response and redact unsafe content"""
    validated = response
    
    # Check for unsafe suggestions
    for unsafe in UNSAFE_SUGGESTIONS:
        if unsafe.lower() in validated.lower():
            validated = re.sub(re.escape(unsafe), '[RESPONSE_FILTERED]', validated, flags=re.IGNORECASE)
    
    # Remove any PII that might have leaked through
    validated = EMAIL_PATTERN.sub('[EMAIL_REDACTED]', validated)
    validated = PHONE_PATTERN.sub('[PHONE_REDACTED]', validated)
    validated = SSN_PATTERN.sub('[SSN_REDACTED]', validated)
    
    # Check for inappropriate medical advice
    medical_disclaimers = [
        'diagnose', 'prescribe', 'medication dosage', 'stop taking medication',
        'medical diagnosis', 'replace doctor', 'substitute for professional'
    ]
    
    for disclaimer in medical_disclaimers:
        if disclaimer.lower() in validated.lower():
            validated += "\n\n⚠️ This is not medical advice. Please consult a healthcare professional."
            break
    
    # Ensure response is supportive
    if any(word in validated.lower() for word in ['hopeless', 'no point', 'nothing helps']):
        validated += "\n\nRemember: You are not alone, and help is available. Consider reaching out to a mental health professional."
    
    return validated.strip()

def is_safe_content(text: str) -> bool:
    """Check if content is safe for processing"""
    text_lower = text.lower()
    
    # Check for immediate safety concerns
    crisis_indicators = ['want to die', 'going to kill', 'plan to hurt', 'suicide plan']
    if any(indicator in text_lower for indicator in crisis_indicators):
        return False
    
    # Check for excessive PII
    pii_count = (
        len(EMAIL_PATTERN.findall(text)) +
        len(PHONE_PATTERN.findall(text)) +
        len(SSN_PATTERN.findall(text)) +
        len(CREDIT_CARD_PATTERN.findall(text))
    )
    
    return pii_count <= 2  # Allow minimal PII but flag excessive sharing

def get_safety_warning(text: str) -> str:
    """Generate appropriate safety warning for flagged content"""
    text_lower = text.lower()
    
    if any(indicator in text_lower for indicator in ['want to die', 'going to kill', 'suicide plan']):
        return "⚠️ CRISIS DETECTED: If you're having thoughts of self-harm, please contact emergency services (911) or a crisis hotline immediately."
    
    if any(pii in text for pii in ['[EMAIL_REDACTED]', '[PHONE_REDACTED]', '[SSN_REDACTED]']):
        return "ℹ️ Personal information has been removed for your privacy and security."
    
    return ""