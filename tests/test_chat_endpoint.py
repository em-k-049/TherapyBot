#!/usr/bin/env python3
"""Test script to verify chat endpoint with Vertex AI responses"""

import requests
import json
import os

def test_chat_endpoint():
    """Test the chat endpoint to ensure Vertex AI responses are working"""
    
    # Configuration
    base_url = "http://localhost:8000"
    
    # Test messages
    test_messages = [
        "Hello, I'm feeling anxious today",
        "I'm having trouble sleeping",
        "Can you help me with stress management?",
        "I feel overwhelmed with work"
    ]
    
    print("Testing Chat Endpoint with Vertex AI")
    print("=" * 50)
    
    # First, try to create a test user and login
    print("Setting up test user...")
    
    # Create user
    signup_data = {
        "username": "testuser",
        "email": "test@example.com", 
        "password": "testpass123"
    }
    
    try:
        response = requests.post(f"{base_url}/auth/signup", json=signup_data)
        if response.status_code == 200:
            print("✅ Test user created")
        else:
            print("ℹ️  Test user might already exist")
    except Exception as e:
        print(f"⚠️  Could not create test user: {e}")
    
    # Login
    login_data = {
        "username": "testuser",
        "password": "testpass123"
    }
    
    try:
        response = requests.post(f"{base_url}/auth/login", json=login_data)
        if response.status_code == 200:
            token = response.json()["access_token"]
            print("✅ Successfully logged in")
        else:
            print("❌ Login failed")
            return False
    except Exception as e:
        print(f"❌ Login error: {e}")
        return False
    
    # Test chat endpoint
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\\nTesting chat responses:")
    print("-" * 30)
    
    for i, message in enumerate(test_messages, 1):
        print(f"\\nTest {i}: {message}")
        
        try:
            chat_data = {"message": message}
            response = requests.post(f"{base_url}/messages/chat", json=chat_data, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                ai_response = data.get("ai_response", "")
                
                print(f"Response: {ai_response}")
                print(f"Length: {len(ai_response)} characters")
                
                # Check if it's a real AI response or fallback
                if len(ai_response) > 20 and not any(fallback in ai_response.lower() for fallback in ["fallback", "i'm here to help", "can you tell me more"]):
                    print("✅ Appears to be a real Vertex AI response")
                else:
                    print("⚠️  Appears to be a fallback response")
                    
            else:
                print(f"❌ Request failed: {response.status_code}")
                print(f"Error: {response.text}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\\n" + "=" * 50)
    print("Chat endpoint test completed")
    return True

if __name__ == "__main__":
    test_chat_endpoint()