#!/usr/bin/env python3
"""Simple test script to verify AI chat endpoints"""

import requests
import json

def test_ai_endpoints():
    base_url = "http://localhost:8000"
    
    # Test messages
    test_messages = [
        "Hello, I feel anxious today",
        "I'm having trouble sleeping"
    ]
    
    print("Testing AI Chat Endpoints")
    print("=" * 50)
    
    # Create test user and login
    print("Setting up test user...")
    
    signup_data = {
        "username": "testuser",
        "email": "test@example.com", 
        "password": "testpass123"
    }
    
    try:
        response = requests.post(f"{base_url}/auth/signup", json=signup_data)
        if response.status_code == 200:
            print("[OK] Test user created")
        else:
            print("[INFO] Test user might already exist")
    except Exception as e:
        print(f"[WARN] Could not create test user: {e}")
    
    # Login
    login_data = {
        "username": "testuser",
        "password": "testpass123"
    }
    
    try:
        response = requests.post(f"{base_url}/auth/login", json=login_data)
        if response.status_code == 200:
            token = response.json()["access_token"]
            print("[OK] Successfully logged in")
        else:
            print("[ERROR] Login failed")
            return False
    except Exception as e:
        print(f"[ERROR] Login error: {e}")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n1. Testing Text Chat Endpoint (/messages/chat)")
    print("-" * 40)
    
    for i, message in enumerate(test_messages, 1):
        print(f"\nTest {i}: {message}")
        
        try:
            chat_data = {"message": message}
            response = requests.post(f"{base_url}/messages/chat", json=chat_data, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                ai_response = data.get("ai_response", "")
                user_message = data.get("user_message", "")
                
                print(f"User: {user_message}")
                print(f"AI: {ai_response}")
                print(f"Response Length: {len(ai_response)} characters")
                
                # Check if it's a real AI response
                if len(ai_response) > 20 and "placeholder" not in ai_response.lower():
                    print("[OK] Real AI response generated")
                else:
                    print("[WARN] Possible fallback response")
                    
            else:
                print(f"[ERROR] Request failed: {response.status_code}")
                print(f"Error: {response.text}")
                
        except Exception as e:
            print(f"[ERROR] Error: {e}")
    
    print("\n" + "=" * 50)
    print("AI endpoint testing completed")
    return True

if __name__ == "__main__":
    test_ai_endpoints()