#!/usr/bin/env python3
"""
Simplified tests that don't require full app dependencies
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_health_endpoint():
    """Test health endpoint"""
    print("🏥 Testing Health Endpoint")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data}")
            return True
        else:
            print(f"❌ Health check failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Health endpoint error: {e}")
        return False

def test_chat_endpoint():
    """Test chat endpoint"""
    print("\n💬 Testing Chat Endpoint")
    try:
        response = requests.post(
            f"{BASE_URL}/messages/test-chat",
            json={"message": "Hello, how are you?"},
            timeout=30
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Chat test passed")
            print(f"Response: {data.get('ai_response', 'No AI response')}")
            return True
        else:
            print(f"❌ Chat test failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Chat endpoint error: {e}")
        return False

def test_invalid_payload():
    """Test invalid payload handling"""
    print("\n🚫 Testing Invalid Payload")
    try:
        response = requests.post(
            f"{BASE_URL}/messages/test-chat",
            json={},
            timeout=5
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 422:
            print("✅ Invalid payload correctly rejected")
            return True
        else:
            print(f"❌ Expected 422, got {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Invalid payload test error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 TherapyBot Simple Tests")
    print("=" * 50)
    print("Make sure backend is running: python -m uvicorn app.main:app --reload")
    print()
    
    results = []
    results.append(test_health_endpoint())
    results.append(test_chat_endpoint())
    results.append(test_invalid_payload())
    
    print("\n📊 Test Results")
    print("=" * 50)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("💥 Some tests failed!")
        return 1

if __name__ == "__main__":
    exit(main())