#!/usr/bin/env python3
"""
Maya Private - Quick Test Script
Tests local and cloud inference endpoints
"""

import requests
import json
import time

BASE_URL = "http://localhost:5000"

def test_privacy_status():
    """Test privacy status endpoint"""
    print("\n🔍 Testing Privacy Status...")
    try:
        response = requests.get(f"{BASE_URL}/privacy/status")
        if response.status_code == 200:
            data = response.json()
            print("✅ Privacy Status:")
            print(f"   Status: {data.get('status')}")
            print(f"   Context Limit: {data.get('context_limit')} chars")
            print(f"   Total Offloads: {data.get('total_offloads')}")
            return True
        else:
            print(f"❌ Status check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_local_inference():
    """Test local inference with short prompt"""
    print("\n🟢 Testing Local Inference...")
    try:
        prompt = "Hello Maya, how are you today?"
        response = requests.post(
            f"{BASE_URL}/privacy/execute",
            json={"prompt": prompt},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Local Inference Response:")
            print(f"   Mode: {data.get('mode')}")
            print(f"   Context Length: {data.get('context_length')} chars")
            print(f"   Output: {data.get('output')[:100]}...")
            return data.get('mode') == 'local'
        else:
            print(f"❌ Local inference failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_cloud_offload():
    """Test cloud offload with long prompt"""
    print("\n⚠️  Testing Cloud Offload...")
    try:
        # Create a prompt > 2000 chars
        prompt = "Explain quantum computing in detail. " * 100
        
        response = requests.post(
            f"{BASE_URL}/privacy/execute",
            json={"prompt": prompt},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Cloud Offload Response:")
            print(f"   Mode: {data.get('mode')}")
            print(f"   Context Length: {data.get('context_length')} chars")
            print(f"   Output: {data.get('output')[:100]}...")
            return 'offload' in data.get('mode', '')
        else:
            print(f"❌ Cloud offload failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_offload_logs():
    """Test offload logs endpoint"""
    print("\n📋 Testing Offload Logs...")
    try:
        response = requests.get(f"{BASE_URL}/privacy/logs?limit=5")
        if response.status_code == 200:
            data = response.json()
            print("✅ Recent Offload Logs:")
            logs = data.get('logs', [])
            if logs:
                for log in logs[-3:]:  # Show last 3
                    print(f"   {log}")
            else:
                print("   (No offload events yet)")
            return True
        else:
            print(f"❌ Log retrieval failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("🔒 Maya Private - Testing Suite")
    print("=" * 60)
    
    # Check if server is running
    try:
        response = requests.get(BASE_URL, timeout=2)
        print("✅ Backend server is running")
    except requests.exceptions.ConnectionError:
        print("❌ Backend server is not running!")
        print("   Please start the server with: python src/config/app2.py")
        return
    
    # Run tests
    results = {
        "Privacy Status": test_privacy_status(),
        "Local Inference": test_local_inference(),
        "Cloud Offload": test_cloud_offload(),
        "Offload Logs": test_offload_logs()
    }
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\n✨ Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Maya Private is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    main()
