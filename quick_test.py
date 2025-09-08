#!/usr/bin/env python3
"""
Quick test runner for TherapyBot
"""
import subprocess
import sys
import os

def run_command(cmd, cwd=None):
    """Run command and return success status"""
    print(f"\n🔧 Running: {cmd}")
    print("=" * 50)
    
    try:
        result = subprocess.run(cmd, shell=True, cwd=cwd)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Run quick tests"""
    print("⚡ TherapyBot Quick Tests")
    print("=" * 50)
    
    # Backend simple tests
    print("\n📡 Running Backend Simple Tests...")
    backend_success = run_command("python test_simple.py", cwd="backend")
    
    # Frontend install and test
    print("\n🌐 Setting up Frontend Tests...")
    frontend_setup = run_command("npm install", cwd="frontend")
    
    if frontend_setup:
        print("Installing Playwright...")
        run_command("npx playwright install chromium", cwd="frontend")
        
        print("Running Frontend Tests...")
        frontend_success = run_command("npx playwright test --project=chromium", cwd="frontend")
    else:
        frontend_success = False
    
    # Summary
    print("\n📊 Quick Test Summary")
    print("=" * 50)
    print(f"Backend: {'✅ PASS' if backend_success else '❌ FAIL'}")
    print(f"Frontend: {'✅ PASS' if frontend_success else '❌ FAIL'}")
    
    if backend_success and frontend_success:
        print("\n🎉 Quick tests passed!")
        return 0
    else:
        print("\n💥 Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())