#!/usr/bin/env python3
"""
Simple test for AI endpoints without authentication
"""
import asyncio
import sys
import os

# Add the backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

async def test_ai_services():
    """Test AI services directly"""
    try:
        from backend.app.services.vertex_ai import get_ai_response
        
        print("🤖 Testing AI Services")
        print("=" * 40)
        
        test_message = "I'm feeling anxious about work"
        print(f"Input: {test_message}")
        
        try:
            response = await get_ai_response(test_message)
            print(f"✅ Success: {response}")
        except Exception as e:
            print(f"❌ Error: {e}")
            
    except ImportError as e:
        print(f"Import error: {e}")
        print("Make sure you're running from the project root directory")

if __name__ == "__main__":
    asyncio.run(test_ai_services())