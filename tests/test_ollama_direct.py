#!/usr/bin/env python3
"""
Test Ollama directly
"""
import requests
import json

def test_ollama_direct():
    """Test Ollama API directly"""
    ollama_url = "http://127.0.0.1:11434"
    
    print("🦙 Testing Ollama Direct Connection")
    print("=" * 40)
    
    # Test data
    data = {
        "model": "llama2",
        "prompt": "You are a therapist. User: Hello, how are you? Therapist:",
        "stream": False
    }
    
    try:
        print(f"POST {ollama_url}/api/generate")
        print(f"Data: {json.dumps(data, indent=2)}")
        
        response = requests.post(
            f"{ollama_url}/api/generate",
            json=data,
            timeout=30
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Response: {result.get('response', 'No response field')}")
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure Ollama is running: ollama serve")
        print("2. Make sure llama2 model is installed: ollama pull llama2")
        print("3. Check if WSL is accessible from Windows")

if __name__ == "__main__":
    test_ollama_direct()