#!/usr/bin/env python3
"""
Test script for TherapyBot API endpoints
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_endpoint(endpoint, data, description):
    """Test an API endpoint"""
    print(f"\n🧪 {description}")
    print("=" * 50)
    print(f"POST {BASE_URL}{endpoint}")
    print(f"Data: {json.dumps(data, indent=2)}")
    
    try:
        response = requests.post(
            f"{BASE_URL}{endpoint}",
            json=data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✅ SUCCESS")
        else:
            print("❌ FAILED")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")

def main():
    print("🤖 TherapyBot API Endpoint Tests")
    print("Make sure your backend is running: cd backend && python -m uvicorn app.main:app --reload")
    
    # Test data
    test_message = {"message": "Hello, how are you?"}
    
    # Test endpoints
    test_endpoint("/messages/test-chat", test_message, "Test Chat (No Auth)")
    test_endpoint("/messages/chat", test_message, "Regular Chat (Requires Auth)")
    test_endpoint("/messages/voice-chat", {**test_message, "return_audio": True}, "Voice Chat (Requires Auth)")

if __name__ == "__main__":
    main()