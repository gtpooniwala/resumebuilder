#!/usr/bin/env python3
"""
Test Runner Script - Validates all LangGraph resume editing features
"""
import os
import sys
import subprocess
import time
from pathlib import Path

def run_test_suite():
    """Run the complete test suite for LangGraph resume editing system"""
    
    # Ensure we're in the right directory
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)
    
    # Set environment variables for testing
    os.environ.update({
        'PYTHONPATH': str(backend_dir),
        'DATABASE_URL': 'postgresql://test_user:test_password@localhost:5432/test_resumebuilder',
        'OPENAI_API_KEY': 'test-key-for-mocking',
        'ENVIRONMENT': 'test'
    })
    
    print("🧪 Starting LangGraph Resume Editing Test Suite")
    print("=" * 60)
    
    # Test files to run in order
    test_files = [
        'tests/test_context_manager.py',
        'tests/test_conversation_manager.py', 
        'tests/test_resume_tools.py',
        'tests/test_chat_service.py'
    ]
    
    results = {}
    
    for test_file in test_files:
        if not Path(test_file).exists():
            print(f"❌ Test file not found: {test_file}")
            results[test_file] = "NOT_FOUND"
            continue
            
        print(f"\n🔍 Running {test_file}...")
        print("-" * 40)
        
        try:
            # Run pytest for this specific file
            result = subprocess.run([
                sys.executable, '-m', 'pytest', 
                test_file, 
                '-v',
                '--tb=short',
                '--asyncio-mode=auto'
            ], capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                print(f"✅ {test_file} - PASSED")
                results[test_file] = "PASSED"
            else:
                print(f"❌ {test_file} - FAILED")
                print("STDOUT:", result.stdout[-500:])  # Last 500 chars
                print("STDERR:", result.stderr[-500:])  # Last 500 chars
                results[test_file] = "FAILED"
                
        except subprocess.TimeoutExpired:
            print(f"⏰ {test_file} - TIMEOUT")
            results[test_file] = "TIMEOUT"
        except Exception as e:
            print(f"💥 {test_file} - ERROR: {e}")
            results[test_file] = "ERROR"
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 TEST SUITE SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for status in results.values() if status == "PASSED")
    total = len(results)
    
    for test_file, status in results.items():
        emoji = {
            "PASSED": "✅",
            "FAILED": "❌", 
            "TIMEOUT": "⏰",
            "ERROR": "💥",
            "NOT_FOUND": "🚫"
        }.get(status, "❓")
        
        print(f"{emoji} {test_file}: {status}")
    
    print(f"\n🎯 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! LangGraph implementation is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        return False

if __name__ == "__main__":
    success = run_test_suite()
    sys.exit(0 if success else 1)
