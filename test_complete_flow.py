#!/usr/bin/env python3
"""
Complete Flow Test for Sign Language Learning App
Tests the entire user journey: login → exercise → hand tracking → progress
"""

import requests
import time
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5000"
TEST_USER = {
    "email": "test@example.com",
    "password": "testpass123"
}

def print_status(message, status="INFO"):
    """Print formatted status message"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {status}: {message}")

def test_complete_flow():
    """Test the complete user flow"""
    session = requests.Session()
    
    print_status("🚀 Starting Complete Flow Test", "START")
    print_status("=" * 50, "SEPARATOR")
    
    # Step 1: Register/Login
    print_status("Step 1: User Authentication", "STEP")
    try:
        # Try to register first
        register_response = session.post(f"{BASE_URL}/register", data=TEST_USER)
        if "already exists" in register_response.text.lower():
            print_status("User already exists, proceeding with login", "INFO")
        else:
            print_status("User registered successfully", "SUCCESS")
        
        # Login
        login_response = session.post(f"{BASE_URL}/login", data=TEST_USER)
        if login_response.status_code == 200 and "dashboard" in login_response.url:
            print_status("✅ Login successful", "SUCCESS")
        else:
            print_status("❌ Login failed", "ERROR")
            return False
            
    except Exception as e:
        print_status(f"❌ Authentication error: {e}", "ERROR")
        return False
    
    # Step 2: Start Exercise
    print_status("Step 2: Start Exercise", "STEP")
    try:
        exercise_response = session.post(f"{BASE_URL}/api/start-exercise", 
                                       json={})
        exercise_data = exercise_response.json()
        
        if exercise_data.get('success'):
            exercise = exercise_data['exercise']
            user_progress = exercise_data['user_progress']
            print_status(f"✅ Exercise started: {exercise['type']} - {exercise['target']}", "SUCCESS")
            print_status(f"   Description: {exercise['description']}", "INFO")
            print_status(f"   User Level: {user_progress.get('level', 'beginner')}", "INFO")
        else:
            print_status(f"❌ Exercise start failed: {exercise_data.get('error')}", "ERROR")
            return False
            
    except Exception as e:
        print_status(f"❌ Exercise error: {e}", "ERROR")
        return False
    
    # Step 3: Start Hand Tracking
    print_status("Step 3: Start Hand Tracking", "STEP")
    try:
        tracking_response = session.post(f"{BASE_URL}/api/start-hand-tracking", 
                                       json={})
        tracking_data = tracking_response.json()
        
        if tracking_data.get('success'):
            print_status("✅ Hand tracking started", "SUCCESS")
        else:
            print_status(f"⚠️ Hand tracking warning: {tracking_data.get('error')}", "WARNING")
            
    except Exception as e:
        print_status(f"❌ Hand tracking error: {e}", "ERROR")
    
    # Step 4: Test Hand Tracking Data
    print_status("Step 4: Test Hand Tracking Data", "STEP")
    try:
        for i in range(5):  # Test 5 hand tracking requests
            tracking_response = session.post(f"{BASE_URL}/api/hand-tracking", 
                                           json={})
            tracking_data = tracking_response.json()
            
            if tracking_data.get('success'):
                fingers = tracking_data['fingers']
                recognized = tracking_data['recognized_sign']
                hand_detected = tracking_data['hand_detected']
                
                print_status(f"   Hand tracking {i+1}: Fingers={fingers}, "
                           f"Recognized={recognized}, Detected={hand_detected}", "INFO")
            else:
                print_status(f"   Hand tracking {i+1} failed: {tracking_data.get('error')}", "WARNING")
            
            time.sleep(0.2)  # Small delay between requests
            
    except Exception as e:
        print_status(f"❌ Hand tracking test error: {e}", "ERROR")
    
    # Step 5: Test User Progress
    print_status("Step 5: Test User Progress", "STEP")
    try:
        progress_response = session.get(f"{BASE_URL}/api/user-progress/current")
        progress_data = progress_response.json()
        
        if progress_data.get('success'):
            progress = progress_data['progress']
            completed = progress.get('completed_exercises', [])
            level = progress.get('level', 'beginner')
            score = progress.get('total_score', 0)
            
            print_status(f"✅ Progress loaded: Level={level}, Score={score}, "
                       f"Completed={len(completed)}", "SUCCESS")
        else:
            print_status(f"❌ Progress load failed: {progress_data.get('error')}", "ERROR")
            
    except Exception as e:
        print_status(f"❌ Progress error: {e}", "ERROR")
    
    # Step 6: Test Word Building (if applicable)
    if exercise.get('type') == 'word_building':
        print_status("Step 6: Test Word Building", "STEP")
        try:
            target_word = exercise['target']
            print_status(f"   Target word: {target_word}", "INFO")
            
            # Test word match check
            match_response = session.post(f"{BASE_URL}/api/check-word-match", 
                                        json={'target_word': target_word})
            match_data = match_response.json()
            
            if match_data.get('success'):
                if match_data.get('match'):
                    print_status(f"✅ Word match: {match_data['message']}", "SUCCESS")
                else:
                    print_status(f"   Word status: {match_data['message']}", "INFO")
            else:
                print_status(f"❌ Word match failed: {match_data.get('error')}", "ERROR")
                
        except Exception as e:
            print_status(f"❌ Word building error: {e}", "ERROR")
    
    # Step 7: Stop Exercise
    print_status("Step 7: Stop Exercise", "STEP")
    try:
        stop_response = session.post(f"{BASE_URL}/api/stop-exercise", json={})
        stop_data = stop_response.json()
        
        if stop_data.get('success'):
            print_status("✅ Exercise stopped successfully", "SUCCESS")
        else:
            print_status(f"❌ Exercise stop failed: {stop_data.get('error')}", "ERROR")
            
    except Exception as e:
        print_status(f"❌ Stop exercise error: {e}", "ERROR")
    
    # Step 8: Test Video Stream
    print_status("Step 8: Test Video Stream", "STEP")
    try:
        video_response = session.get(f"{BASE_URL}/simple_video", stream=True)
        if video_response.status_code == 200:
            print_status("✅ Video stream accessible", "SUCCESS")
        else:
            print_status(f"❌ Video stream failed: {video_response.status_code}", "ERROR")
            
    except Exception as e:
        print_status(f"❌ Video stream error: {e}", "ERROR")
    
    print_status("=" * 50, "SEPARATOR")
    print_status("🎉 Complete Flow Test Finished!", "SUCCESS")
    return True

def test_backend_only():
    """Test backend endpoints without browser interaction"""
    print_status("🔧 Testing Backend Endpoints", "START")
    
    # Test if app is running
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print_status("✅ App is running", "SUCCESS")
        else:
            print_status(f"❌ App not responding: {response.status_code}", "ERROR")
            return False
    except Exception as e:
        print_status(f"❌ Cannot connect to app: {e}", "ERROR")
        return False
    
    # Test video stream endpoint
    try:
        response = requests.get(f"{BASE_URL}/simple_video", stream=True, timeout=5)
        if response.status_code == 200:
            print_status("✅ Video stream endpoint working", "SUCCESS")
        else:
            print_status(f"❌ Video stream endpoint failed: {response.status_code}", "ERROR")
    except Exception as e:
        print_status(f"❌ Video stream test failed: {e}", "ERROR")
    
    return True

if __name__ == "__main__":
    print("🧪 Sign Language Learning App - Complete Flow Test")
    print("=" * 60)
    
    # First test if backend is running
    if not test_backend_only():
        print_status("❌ Backend test failed. Make sure the app is running!", "ERROR")
        print_status("Run: python app.py", "HELP")
        exit(1)
    
    print()
    
    # Then test complete flow
    success = test_complete_flow()
    
    if success:
        print_status("🎯 All tests completed successfully!", "SUCCESS")
    else:
        print_status("❌ Some tests failed. Check the output above.", "ERROR")
    
    print()
    print_status("💡 Tips:", "INFO")
    print_status("   - Make sure camera is connected and accessible", "TIP")
    print_status("   - Check that firebase-credentials.json exists", "TIP")
    print_status("   - Verify .env file has required API keys", "TIP")
    print_status("   - Ensure all dependencies are installed", "TIP") 