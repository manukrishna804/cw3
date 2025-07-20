#!/usr/bin/env python3
"""
Test script to verify real OpenCV hand tracking functionality
"""

import requests
import json
import time

BASE_URL = "http://localhost:5000"

def test_hand_tracking_api():
    """Test the hand tracking API endpoint"""
    print("📹 Testing Real Hand Tracking API...")
    
    # First, we need to login to get a session
    login_data = {
        "email": "test@example.com",
        "password": "testpassword123"
    }
    
    try:
        # Login
        login_response = requests.post(f"{BASE_URL}/login", 
                                     json=login_data,
                                     headers={'Content-Type': 'application/json'})
        
        if login_response.status_code != 200:
            print("❌ Login failed, cannot test hand tracking")
            return False
        
        # Get session cookies
        session_cookies = login_response.cookies
        
        # Test hand tracking API
        print("   🔄 Testing hand tracking endpoint...")
        
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
                
                print(f"   ✅ Hand tracking working!")
                print(f"   📊 Finger pattern: {fingers}")
                print(f"   🎯 Recognized sign: {recognized}")
                print(f"   🤚 Hand detected: {hand_detected}")
                
                return True
            else:
                print(f"   ❌ Hand tracking failed: {data.get('error')}")
                return False
        else:
            print(f"   ❌ Hand tracking request failed: {tracking_response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error testing hand tracking: {e}")
        return False

def test_exercise_generation():
    """Test exercise generation with Gemini AI"""
    print("\n🧠 Testing Exercise Generation with Gemini...")
    
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
            print("❌ Login failed, cannot test exercise generation")
            return False
        
        session_cookies = login_response.cookies
        
        # Test exercise generation
        exercise_response = requests.post(f"{BASE_URL}/api/start-exercise", 
                                        json={},
                                        headers={'Content-Type': 'application/json'},
                                        cookies=session_cookies)
        
        if exercise_response.status_code == 200:
            data = exercise_response.json()
            if data.get('success'):
                exercise = data.get('exercise', {})
                print(f"   ✅ Exercise generated successfully!")
                print(f"   📝 Exercise type: {exercise.get('type')}")
                print(f"   🎯 Target: {exercise.get('target')}")
                print(f"   📖 Description: {exercise.get('description')}")
                
                return True
            else:
                print(f"   ❌ Exercise generation failed: {data.get('error')}")
                return False
        else:
            print(f"   ❌ Exercise request failed: {exercise_response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error testing exercise generation: {e}")
        return False

def test_sign_recognition():
    """Test sign recognition with sample finger patterns"""
    print("\n👆 Testing Sign Recognition...")
    
    # Sample finger patterns for testing
    test_patterns = [
        ([1, 0, 0, 0, 0], "A - Thumb only"),
        ([0, 1, 0, 0, 0], "1 - Index only"),
        ([1, 1, 0, 0, 0], "L - Thumb and index"),
        ([0, 1, 1, 0, 0], "U - Index and middle"),
        ([1, 1, 1, 1, 1], "O - All fingers")
    ]
    
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
            print("❌ Login failed, cannot test sign recognition")
            return False
        
        session_cookies = login_response.cookies
        
        # Test each pattern
        for fingers, description in test_patterns:
            print(f"   🧪 Testing: {description}")
            
            check_response = requests.post(f"{BASE_URL}/api/check-sign", 
                                         json={
                                             'fingers': fingers,
                                             'exercise': {'type': 'alphabet', 'target': 'A'},
                                             'current_letters': []
                                         },
                                         headers={'Content-Type': 'application/json'},
                                         cookies=session_cookies)
            
            if check_response.status_code == 200:
                data = check_response.json()
                if data.get('success'):
                    recognized = data.get('recognized')
                    correct = data.get('correct')
                    print(f"      ✅ Recognized: {recognized}, Correct: {correct}")
                else:
                    print(f"      ❌ Recognition failed: {data.get('error')}")
            else:
                print(f"      ❌ Request failed: {check_response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error testing sign recognition: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Real Hand Tracking System...\n")
    
    # Test 1: Hand tracking API
    tracking_success = test_hand_tracking_api()
    
    # Test 2: Exercise generation
    exercise_success = test_exercise_generation()
    
    # Test 3: Sign recognition
    recognition_success = test_sign_recognition()
    
    # Summary
    print("\n" + "="*50)
    print("📊 HAND TRACKING TEST SUMMARY")
    print("="*50)
    print(f"Real Hand Tracking: {'✅ PASS' if tracking_success else '❌ FAIL'}")
    print(f"Exercise Generation: {'✅ PASS' if exercise_success else '❌ FAIL'}")
    print(f"Sign Recognition: {'✅ PASS' if recognition_success else '❌ FAIL'}")
    
    if all([tracking_success, exercise_success, recognition_success]):
        print("\n🎉 All hand tracking tests passed!")
        print("🚀 Real OpenCV hand tracking is working!")
    else:
        print("\n⚠️ Some tests failed.")
        print("\n💡 Troubleshooting:")
        print("   1. Make sure the app is running: python app.py")
        print("   2. Check if camera is accessible")
        print("   3. Verify OpenCV and cvzone are installed")
        print("   4. Test with a registered user account")

if __name__ == "__main__":
    main() 