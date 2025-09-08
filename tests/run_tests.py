#!/usr/bin/env python3
"""
Test runner for TherapyBot
"""
import subprocess
import sys
import os
import time

def run_command(cmd, cwd=None):
    """Run command and return success status"""
    print(f"\n🔧 Running: {cmd}")
    print("=" * 50)
    
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            cwd=cwd,
            capture_output=False,
            text=True
        )
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 TherapyBot Test Suite")
    print("=" * 50)
    
    # Backend tests
    print("\n📡 Running Backend Tests...")
    backend_success = run_command("pytest test_endpoints.py -v", cwd="backend")
    
    if backend_success:
        print("✅ Backend tests passed")
    else:
        print("❌ Backend tests failed")
    
    # Frontend tests
    print("\n🌐 Running Frontend Tests...")
    
    # Install playwright if needed
    print("Installing Playwright browsers...")
    run_command("npx playwright install", cwd="frontend")
    
    # Run tests
    frontend_success = run_command("npm run test", cwd="frontend")
    
    if frontend_success:
        print("✅ Frontend tests passed")
    else:
        print("❌ Frontend tests failed")
    
    # Summary
    print("\n📊 Test Summary")
    print("=" * 50)
    print(f"Backend: {'✅ PASS' if backend_success else '❌ FAIL'}")
    print(f"Frontend: {'✅ PASS' if frontend_success else '❌ FAIL'}")
    
    if backend_success and frontend_success:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print("\n💥 Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())