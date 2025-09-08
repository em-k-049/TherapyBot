#!/usr/bin/env python3
"""
Test script to demonstrate Vertex AI + Ollama fallback functionality
"""
import asyncio
import sys
import os

# Add the backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.vertex_ai import get_ai_response

async def test_ai_fallback():
    """Test the AI fallback system"""
    test_messages = [
        "Hello, I need help with anxiety",
        "I'm feeling very depressed today",
        "Can you help me with stress management?",
        "I'm having trouble sleeping"
    ]
    
    print("🤖 Testing Vertex AI + Ollama Fallback System")
    print("=" * 50)
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n{i}. Testing message: '{message}'")
        print("-" * 40)
        
        try:
            response = await get_ai_response(message)
            print(f"✅ AI Response: {response}")
            
            # Check if it's a fallback response
            fallback_indicators = [
                "I'm here to support",
                "I understand you're feeling",
                "Anxiety can feel",
                "It sounds like",
                "I'm concerned",
                "Thank you for sharing"
            ]
            
            is_fallback = any(indicator in response for indicator in fallback_indicators)
            if is_fallback:
                print("🔄 This appears to be a fallback response (Vertex AI likely unavailable)")
            else:
                print("🎯 This appears to be a real AI response (Vertex AI or Ollama working)")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("Test completed!")

if __name__ == "__main__":
    asyncio.run(test_ai_fallback())