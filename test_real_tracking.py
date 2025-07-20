#!/usr/bin/env python3
"""
Test script to verify real-time hand tracking is working
"""

import requests
import json
import time

BASE_URL = "http://localhost:5000"

def test_hand_tracking_thread():
    """Test if hand tracking thread is working"""
    print("🤚 Testing Real-Time Hand Tracking Thread...")
    
    # Login first
    login_data = {
        "email": "test@example.com",
        "password": "testpassword123"
    }
    
    try:
        login_response = requests.post(f"{BASE_URL}/login", 
                                     json=login_data,
                                     headers={'Content-Type': 'application/json'})
        
        if login_response.status_code != 200:
            print("❌ Login failed, cannot test hand tracking")
            return False
        
        session_cookies = login_response.cookies
        
        # Start hand tracking
        print("   🔄 Starting hand tracking thread...")
        start_response = requests.post(f"{BASE_URL}/api/start-hand-tracking", 
                                     json={},
                                     headers={'Content-Type': 'application/json'},
                                     cookies=session_cookies)
        
        if start_response.status_code != 200:
            print(f"   ❌ Failed to start hand tracking: {start_response.status_code}")
            return False
        
        # Test hand tracking data
        print("   📊 Testing hand tracking data...")
        print("   Show your hand to the camera for 10 seconds...")
        
        start_time = time.time()
        hand_detected_count = 0
        gesture_detected_count = 0
        
        while time.time() - start_time < 10:
            tracking_response = requests.post(f"{BASE_URL}/api/hand-tracking", 
                                           json={},
                                           headers={'Content-Type': 'application/json'},
                                           cookies=session_cookies)
            
            if tracking_response.status_code == 200:
                data = tracking_response.json()
                if data.get('success'):
                    fingers = data.get('fingers', [])
                    recognized = data.get('recognized_sign')
                    hand_detected = data.get('hand_detected')
                    stable = data.get('stable')
                    current_word = data.get('current_word')
                    
                    if hand_detected:
                        hand_detected_count += 1
                        print(f"   ✅ Hand detected! Fingers: {fingers}")
                        
                        if recognized and recognized != "Unknown":
                            gesture_detected_count += 1
                            print(f"   🎯 Gesture: {recognized} (Stable: {stable})")
                            
                            if stable:
                                print(f"   📝 Current word: '{current_word}'")
                    
                    time.sleep(0.5)  # Check every 0.5 seconds
                else:
                    print(f"   ❌ Hand tracking failed: {data.get('error')}")
                    break
            else:
                print(f"   ❌ Hand tracking request failed: {tracking_response.status_code}")
                break
        
        print(f"\n📊 Hand Tracking Results:")
        print(f"   Hand detected: {hand_detected_count} times")
        print(f"   Gestures recognized: {gesture_detected_count} times")
        
        if hand_detected_count > 0:
            print("   ✅ Hand tracking is working!")
            return True
        else:
            print("   ❌ No hand detected - check camera")
            return False
            
    except Exception as e:
        print(f"   ❌ Error testing hand tracking: {e}")
        return False

def test_word_building():
    """Test word building functionality"""
    print("\n📝 Testing Word Building...")
    
    # Login first
    login_data = {
        "email": "test@example.com",
        "password": "testpassword123"
    }
    
    try:
        login_response = requests.post(f"{BASE_URL}/login", 
                                     json=login_data,
                                     headers={'Content-Type': 'application/json'})
        
        if login_response.status_code != 200:
            print("❌ Login failed, cannot test word building")
            return False
        
        session_cookies = login_response.cookies
        
        # Test word building
        print("   🧪 Testing word building with sample gestures...")
        
        # Test letter 'A' gesture
        test_response = requests.post(f"{BASE_URL}/api/check-word-match", 
                                    json={'target_word': 'A'},
                                    headers={'Content-Type': 'application/json'},
                                    cookies=session_cookies)
        
        if test_response.status_code == 200:
            data = test_response.json()
            if data.get('success'):
                print("   ✅ Word building API working")
                return True
            else:
                print(f"   ❌ Word building failed: {data.get('error')}")
                return False
        else:
            print(f"   ❌ Word building request failed: {test_response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error testing word building: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Real-Time Hand Tracking System...\n")
    
    # Test 1: Hand tracking thread
    tracking_ok = test_hand_tracking_thread()
    
    # Test 2: Word building
    word_building_ok = test_word_building()
    
    # Summary
    print("\n" + "="*50)
    print("📊 REAL-TIME TRACKING TEST SUMMARY")
    print("="*50)
    print(f"Hand Tracking Thread: {'✅ PASS' if tracking_ok else '❌ FAIL'}")
    print(f"Word Building: {'✅ PASS' if word_building_ok else '❌ FAIL'}")
    
    if tracking_ok and word_building_ok:
        print("\n🎉 All real-time tracking tests passed!")
        print("🚀 Real OpenCV hand tracking is working!")
    else:
        print("\n⚠️ Some tests failed.")
        print("\n💡 Troubleshooting:")
        print("   1. Make sure the app is running: python app.py")
        print("   2. Check if camera is accessible and working")
        print("   3. Verify OpenCV and cvzone are installed")
        print("   4. Make sure no other app is using the camera")
        print("   5. Check console for hand tracking thread messages")

if __name__ == "__main__":
    main() 