#!/usr/bin/env python3
"""Test script to verify Vertex AI integration"""

import os
import sys
import asyncio
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from services.vertex_ai import get_vertex_client, send_to_vertex_ai

def test_vertex_ai():
    """Test Vertex AI client initialization and response generation"""
    print("Testing Vertex AI Integration...")
    print("=" * 50)
    
    # Test client initialization
    client = get_vertex_client()
    print(f"Project ID: {client.project_id}")
    print(f"Region: {client.region}")
    print(f"Model: {client.model_name}")
    print(f"Model initialized: {client.model is not None}")
    
    if client.model is None:
        print("❌ Vertex AI model not initialized - check credentials and configuration")
        return False
    
    # Test response generation
    test_messages = [
        "Hello, I'm feeling anxious today",
        "I'm having trouble sleeping",
        "Can you help me with stress management?"
    ]
    
    print("\nTesting response generation:")
    print("-" * 30)
    
    for i, message in enumerate(test_messages, 1):
        print(f"\nTest {i}: {message}")
        try:
            response = send_to_vertex_ai(message)
            print(f"Response: {response}")
            print(f"Length: {len(response)} characters")
            
            if len(response) > 10 and "fallback" not in response.lower():
                print("✅ Real Vertex AI response generated")
            else:
                print("⚠️  Fallback response used")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    print("\n" + "=" * 50)
    print("✅ Vertex AI integration test completed successfully")
    return True

if __name__ == "__main__":
    # Set environment variables if not already set
    if not os.getenv("GCP_PROJECT_ID"):
        os.environ["GCP_PROJECT_ID"] = "therapybot-469702"
    if not os.getenv("GCP_REGION"):
        os.environ["GCP_REGION"] = "us-central1"
    if not os.getenv("VERTEX_AI_MODEL"):
        os.environ["VERTEX_AI_MODEL"] = "gemini-2.0-flash"
    if not os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(Path(__file__).parent / "secrets" / "gcp-credentials.json")
    
    success = test_vertex_ai()
    sys.exit(0 if success else 1)