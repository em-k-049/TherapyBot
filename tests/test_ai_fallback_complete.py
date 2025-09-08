#!/usr/bin/env python3
"""
Test AI fallback system
"""
import requests
import json
import os

def test_fastapi_endpoint():
    """Test FastAPI chat endpoint"""
    base_url = "http://localhost:8000"
    
    print("🤖 Testing FastAPI AI Fallback")
    print("=" * 40)
    
    # Test data
    data = {"message": "I'm feeling anxious about work"}
    
    try:
        print(f"POST {base_url}/messages/test-chat")
        print(f"Data: {json.dumps(data, indent=2)}")
        
        response = requests.post(
            f"{base_url}/messages/test-chat",
            json=data,
            timeout=60
        )
        
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2)}")
        
        if result.get("ai_response"):
            print("✅ AI Response received successfully")
            if "error" in result:
                print(f"⚠️  Fallback used due to: {result['error']}")
        else:
            print("❌ No AI response received")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

def main():
    print("AI Fallback System Test")
    print("\nMake sure these are running:")
    print("1. FastAPI backend: cd backend && python -m uvicorn app.main:app --reload")
    print("2. Ollama (WSL): ollama serve")
    print("3. Ollama model: ollama pull llama2")
    print()
    
    test_fastapi_endpoint()

if __name__ == "__main__":
    main()