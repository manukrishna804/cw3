#!/usr/bin/env python3
"""
Test script to verify authentication security and camera functionality
"""

import requests
import json
import time

BASE_URL = "http://localhost:5000"

def test_registration():
    """Test user registration"""
    print("🔐 Testing User Registration...")
    
    # Test valid registration
    registration_data = {
        "email": "testuser@example.com",
        "password": "testpassword123",
        "name": "Test User"
    }
    
    response = requests.post(f"{BASE_URL}/register", 
                           json=registration_data,
                           headers={'Content-Type': 'application/json'})
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            print("✅ Registration successful!")
            return registration_data
        else:
            print(f"❌ Registration failed: {result.get('error')}")
            return None
    else:
        print(f"❌ Registration request failed: {response.status_code}")
        return None

def test_login_with_registered_user(user_data):
    """Test login with registered user"""
    print("\n🔑 Testing Login with Registered User...")
    
    login_data = {
        "email": user_data["email"],
        "password": user_data["password"]
    }
    
    response = requests.post(f"{BASE_URL}/login", 
                           json=login_data,
                           headers={'Content-Type': 'application/json'})
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            print("✅ Login successful for registered user!")
            return True
        else:
            print(f"❌ Login failed: {result.get('error')}")
            return False
    else:
        print(f"❌ Login request failed: {response.status_code}")
        return False

def test_login_with_unregistered_user():
    """Test login with unregistered user (should fail)"""
    print("\n🚫 Testing Login with Unregistered User...")
    
    login_data = {
        "email": "nonexistent@example.com",
        "password": "wrongpassword"
    }
    
    response = requests.post(f"{BASE_URL}/login", 
                           json=login_data,
                           headers={'Content-Type': 'application/json'})
    
    if response.status_code == 200:
        result = response.json()
        if not result.get('success'):
            print("✅ Login correctly rejected for unregistered user!")
            return True
        else:
            print("❌ Login should have failed for unregistered user!")
            return False
    else:
        print(f"❌ Login request failed: {response.status_code}")
        return False

def test_exercise_access():
    """Test exercise access"""
    print("\n🎯 Testing Exercise Access...")
    
    # Try to access exercise without login (should redirect to login)
    response = requests.get(f"{BASE_URL}/exercise", allow_redirects=False)
    
    if response.status_code == 302:
        print("✅ Exercise page correctly redirects to login when not authenticated!")
        return True
    else:
        print(f"❌ Exercise page should redirect to login: {response.status_code}")
        return False

def test_camera_api():
    """Test camera API endpoints"""
    print("\n📹 Testing Camera API...")
    
    # Test start exercise API (should fail without authentication)
    response = requests.post(f"{BASE_URL}/api/start-exercise", 
                           json={},
                           headers={'Content-Type': 'application/json'})
    
    if response.status_code == 401 or response.status_code == 302:
        print("✅ Camera API correctly requires authentication!")
        return True
    else:
        print(f"❌ Camera API should require authentication: {response.status_code}")
        return False

def main():
    """Run all tests"""
    print("🧪 Starting Authentication Security Tests...\n")
    
    # Test 1: Registration
    user_data = test_registration()
    if not user_data:
        print("❌ Cannot continue tests without successful registration")
        return
    
    # Test 2: Login with registered user
    login_success = test_login_with_registered_user(user_data)
    
    # Test 3: Login with unregistered user
    unregistered_test = test_login_with_unregistered_user()
    
    # Test 4: Exercise access protection
    exercise_test = test_exercise_access()
    
    # Test 5: Camera API protection
    camera_test = test_camera_api()
    
    # Summary
    print("\n" + "="*50)
    print("📊 TEST SUMMARY")
    print("="*50)
    print(f"Registration: {'✅ PASS' if user_data else '❌ FAIL'}")
    print(f"Registered User Login: {'✅ PASS' if login_success else '❌ FAIL'}")
    print(f"Unregistered User Blocked: {'✅ PASS' if unregistered_test else '❌ FAIL'}")
    print(f"Exercise Access Protected: {'✅ PASS' if exercise_test else '❌ FAIL'}")
    print(f"Camera API Protected: {'✅ PASS' if camera_test else '❌ FAIL'}")
    
    if all([user_data, login_success, unregistered_test, exercise_test, camera_test]):
        print("\n🎉 All authentication security tests passed!")
    else:
        print("\n⚠️ Some tests failed. Check the implementation.")

if __name__ == "__main__":
    main() 