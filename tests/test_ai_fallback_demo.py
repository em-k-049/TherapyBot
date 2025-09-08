#!/usr/bin/env python3
"""
Demo script to test Vertex AI + Ollama fallback functionality
"""
import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BASE_URL = "http://localhost:8000"

def test_text_chat(message: str, auth_token: str):
    """Test the /chat/text endpoint"""
    print(f"\n🔤 Testing text chat with message: '{message}'")
    
    response = requests.post(
        f"{BASE_URL}/chat/text",
        json={"message": message},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Reply: {data['reply']}")
    else:
        print(f"❌ Error: {response.text}")
    
    return response

def test_voice_chat(message: str, auth_token: str):
    """Test the /chat/voice endpoint"""
    print(f"\n🎤 Testing voice chat with message: '{message}'")
    
    response = requests.post(
        f"{BASE_URL}/chat/voice",
        data={"message": message},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Reply: {data['reply']}")
        if data.get('transcribed_text'):
            print(f"📝 Transcribed: {data['transcribed_text']}")
    else:
        print(f"❌ Error: {response.text}")
    
    return response

def test_scenarios():
    """Test different scenarios"""
    
    # You'll need to get an auth token first
    # For demo purposes, assuming you have a way to get this
    auth_token = "your-auth-token-here"  # Replace with actual token
    
    print("=" * 60)
    print("🤖 TherapyBot AI Fallback Demo")
    print("=" * 60)
    
    # Test messages
    test_messages = [
        "I'm feeling anxious about work",
        "Can you help me with stress management?",
        "I'm having trouble sleeping",
        "How do I deal with depression?"
    ]
    
    for message in test_messages:
        # Test text endpoint
        test_text_chat(message, auth_token)
        
        # Test voice endpoint
        test_voice_chat(message, auth_token)
        
        print("-" * 40)

def test_with_vertex_disabled():
    """Test with Vertex AI disabled to force Ollama usage"""
    print("\n🔧 Testing with Vertex AI disabled (Ollama only)")
    
    # This would require temporarily setting USE_VERTEX_AI=false
    # and restarting the backend
    
def test_with_ollama_down():
    """Test with Ollama down to see error handling"""
    print("\n⚠️  Testing with Ollama down (error handling)")
    
    # This would require stopping Ollama service
    # Should return "No AI backend available" error

if __name__ == "__main__":
    print("Demo script for AI fallback functionality")
    print("\nTo run this demo:")
    print("1. Start your FastAPI backend: cd backend && python -m uvicorn app.main:app --reload")
    print("2. Ensure Ollama is running: ollama serve")
    print("3. Get an auth token from your login endpoint")
    print("4. Update the auth_token variable in this script")
    print("5. Run: python test_ai_fallback_demo.py")
    
    # Uncomment to run tests (after setting up auth token)
    # test_scenarios()