#!/usr/bin/env python3
"""
Test script to verify voice chat fix
"""
import requests
import json

def test_voice_chat():
    """Test the voice chat endpoint"""
    BASE_URL = "http://localhost:8000"
    
    # Test data - simulating what frontend sends
    test_data = {
        "message": "hello how are you",
        "return_audio": True
    }
    
    print("🎤 Testing Voice Chat Fix")
    print("=" * 40)
    print(f"Sending: {test_data}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/chat/voice",
            json=test_data,
            headers={
                "Content-Type": "application/json",
                # Note: You'll need a valid token for actual testing
                # "Authorization": "Bearer YOUR_TOKEN_HERE"
            }
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success!")
            print(f"AI Response: {data.get('ai_response', 'N/A')}")
        else:
            print(f"❌ Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    print("Voice Chat Fix Test")
    print("Note: Start your backend server first:")
    print("cd backend && python -m uvicorn app.main:app --reload")
    print()
    # Uncomment to run test (after starting server and adding auth token)
    # test_voice_chat()