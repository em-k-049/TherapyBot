def detect_risk(message: str) -> dict:
    """Enhanced risk detection with sentiment analysis and keyword detection"""
    message_lower = message.lower()
    
    # Critical keywords that immediately escalate
    critical_keywords = ["suicide", "kill myself", "end it all", "hurt myself", "overdose"]
    high_risk_keywords = ["self harm", "cutting", "die", "death", "hopeless", "worthless"]
    moderate_keywords = ["depressed", "anxious", "scared", "alone", "sad"]
    
    # Keyword detection
    found_tags = []
    keyword_score = 0.0
    
    for keyword in critical_keywords:
        if keyword in message_lower:
            found_tags.append(f"critical:{keyword}")
            keyword_score += 1.0
    
    for keyword in high_risk_keywords:
        if keyword in message_lower:
            found_tags.append(f"high:{keyword}")
            keyword_score += 0.7
    
    for keyword in moderate_keywords:
        if keyword in message_lower:
            found_tags.append(f"moderate:{keyword}")
            keyword_score += 0.3
    
    # Simple sentiment analysis (mock VADER/TextBlob)
    negative_words = ["bad", "terrible", "awful", "hate", "angry", "frustrated", "pain"]
    sentiment_score = sum(0.2 for word in negative_words if word in message_lower)
    
    # Calculate total risk score
    total_score = min(keyword_score + sentiment_score, 1.0)
    
    # Determine if risky (threshold: 0.5 or critical keywords)
    is_risky = total_score >= 0.5 or any("critical:" in tag for tag in found_tags)
    
    return {
        "is_risky": is_risky,
        "risk_score": round(total_score, 2),
        "tags": found_tags
    }

def assess_risk(message: str) -> bool:
    """Detect high-risk messages that need escalation"""
    risk_result = detect_risk(message)
    return risk_result["is_risky"]