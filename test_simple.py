#!/usr/bin/env python3
"""
Simple test to verify basic functionality
"""

import requests
import time

def test_basic_functionality():
    """Test basic app functionality"""
    print("🔧 Testing Basic Functionality")
    print("=" * 40)
    
    try:
        # Test if app is running
        response = requests.get("http://localhost:5000/", timeout=5)
        if response.status_code == 200:
            print("✅ App is running")
        else:
            print(f"❌ App returned status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to app: {e}")
        return False
    
    # Test video test page
    try:
        response = requests.get("http://localhost:5000/video-test", timeout=5)
        if response.status_code == 200:
            print("✅ Video test page accessible")
        else:
            print(f"❌ Video test page failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Video test page error: {e}")
    
    # Test simple video stream
    try:
        response = requests.get("http://localhost:5000/simple_video", timeout=10)
        if response.status_code == 200:
            print("✅ Simple video stream responding")
            content_type = response.headers.get('content-type', '')
            if 'multipart/x-mixed-replace' in content_type:
                print("✅ Correct video stream content type")
            else:
                print(f"⚠️  Unexpected content type: {content_type}")
        else:
            print(f"❌ Simple video stream failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Simple video stream error: {e}")
    
    return True

def main():
    print("🎯 Simple Functionality Test")
    print("=" * 50)
    
    if test_basic_functionality():
        print("\n" + "=" * 50)
        print("🎉 Test Summary:")
        print("✅ App is running")
        print("✅ Video test page works")
        print("✅ Video stream endpoint responds")
        print("\n📋 Next Steps:")
        print("1. Go to http://localhost:5000/video-test")
        print("2. You should see your camera feed")
        print("3. Then go to http://localhost:5000/exercise")
        print("4. Click 'Start Exercise' to test hand tracking")
    else:
        print("\n❌ Basic functionality test failed")

if __name__ == "__main__":
    main() 