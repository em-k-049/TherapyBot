"""Startup checks for TherapyBot backend"""

import os
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def check_vertex_ai_setup():
    """Check if Vertex AI is properly configured"""
    logger.info("Checking Vertex AI configuration...")
    
    # Check environment variables
    project_id = os.getenv("GCP_PROJECT_ID")
    region = os.getenv("GCP_REGION")
    model = os.getenv("VERTEX_AI_MODEL")
    credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    
    if not project_id:
        logger.error("GCP_PROJECT_ID not set")
        return False
    
    if not credentials_path:
        logger.error("GOOGLE_APPLICATION_CREDENTIALS not set")
        return False
    
    if not os.path.exists(credentials_path):
        logger.error(f"Credentials file not found: {credentials_path}")
        return False
    
    logger.info(f"✅ Vertex AI configured - Project: {project_id}, Region: {region}, Model: {model}")
    
    # Test Vertex AI client
    try:
        from .services.vertex_ai import get_vertex_client
        client = get_vertex_client()
        
        if client.model is None:
            logger.error("❌ Vertex AI model initialization failed")
            return False
        
        # Test a simple response
        test_response = client.generate_response("Hello")
        if test_response and len(test_response) > 10:
            logger.info("✅ Vertex AI test response generated successfully")
            return True
        else:
            logger.warning("⚠️  Vertex AI returned fallback response")
            return False
            
    except Exception as e:
        logger.error(f"❌ Vertex AI test failed: {e}")
        return False

def run_startup_checks():
    """Run all startup checks"""
    logger.info("Running startup checks...")
    
    checks = [
        ("Vertex AI", check_vertex_ai_setup),
    ]
    
    all_passed = True
    for check_name, check_func in checks:
        try:
            if check_func():
                logger.info(f"✅ {check_name} check passed")
            else:
                logger.error(f"❌ {check_name} check failed")
                all_passed = False
        except Exception as e:
            logger.error(f"❌ {check_name} check error: {e}")
            all_passed = False
    
    if all_passed:
        logger.info("🎉 All startup checks passed!")
    else:
        logger.warning("⚠️  Some startup checks failed - application may not work correctly")
    
    return all_passed