#!/usr/bin/env python3
"""
Test script to verify the Layla Travel Agent integration
"""

import requests
import time
import sys

def test_python_api():
    """Test the Python FastAPI server"""
    print("🧪 Testing Python API server...")
    
    try:
        # Test health endpoint
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Python API health check passed")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Python API health check failed: {response.status_code}")
            return False
            
        # Test chat endpoint
        chat_data = {
            "message": "Bonjour, je veux partir en voyage",
            "conversation_id": None,
            "user_id": None
        }
        
        response = requests.post("http://localhost:8000/chat", json=chat_data, timeout=10)
        if response.status_code == 200:
            print("✅ Python API chat endpoint working")
            result = response.json()
            print(f"   Response preview: {result['response'][:100]}...")
        else:
            print(f"❌ Python API chat endpoint failed: {response.status_code}")
            return False
            
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Python API test failed: {e}")
        return False

def test_symfony_server():
    """Test the Symfony web server"""
    print("\n🧪 Testing Symfony web server...")
    
    try:
        # Test homepage
        response = requests.get("http://localhost:8001", timeout=5)
        if response.status_code == 200:
            print("✅ Symfony server homepage accessible")
        else:
            print(f"❌ Symfony server homepage failed: {response.status_code}")
            return False
            
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Symfony server test failed: {e}")
        return False

def test_full_integration():
    """Test the full integration through Symfony"""
    print("\n🧪 Testing full integration...")
    
    try:
        # Test chat endpoint through Symfony
        chat_data = {
            "message": "Bonjour, je veux partir en voyage",
            "conversation_id": None,
            "user_id": None
        }
        
        response = requests.post("http://localhost:8001/chat/send", json=chat_data, timeout=10)
        if response.status_code == 200:
            print("✅ Full integration working!")
            result = response.json()
            print(f"   Response preview: {result.get('response', '')[:100]}...")
            return True
        else:
            print(f"❌ Full integration failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Full integration test failed: {e}")
        return False

def main():
    print("🚀 Testing Layla Travel Agent Integration")
    print("=" * 50)
    
    # Test Python API
    if not test_python_api():
        print("\n❌ Python API test failed. Please check the server.")
        sys.exit(1)
    
    # Test Symfony server
    if not test_symfony_server():
        print("\n❌ Symfony server test failed. Please check the server.")
        sys.exit(1)
    
    # Test full integration
    if not test_full_integration():
        print("\n❌ Full integration test failed.")
        print("   This might be due to routing issues or missing endpoints.")
        sys.exit(1)
    
    print("\n🎉 All tests passed! Integration is working correctly!")
    print("\n📝 Next steps:")
    print("   1. Open http://localhost:8001 in your browser")
    print("   2. Navigate to the chat interface")
    print("   3. Start chatting with Layla!")
    print("   4. Test travel planning features")

if __name__ == "__main__":
    main() 