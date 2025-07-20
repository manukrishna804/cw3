#!/usr/bin/env python3
"""
Test script to verify existing users can still login
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_existing_user_login():
    """Test login with existing user credentials"""
    print("🔑 Testing Existing User Login...")
    
    # Test with existing user credentials (adjust these as needed)
    test_users = [
        {
            "email": "test@example.com",
            "password": "testpassword123",
            "description": "Test user"
        },
        {
            "email": "user@example.com", 
            "password": "password123",
            "description": "Another test user"
        }
    ]
    
    for user in test_users:
        print(f"\n📧 Testing: {user['description']} ({user['email']})")
        
        login_data = {
            "email": user["email"],
            "password": user["password"]
        }
        
        try:
            response = requests.post(f"{BASE_URL}/login", 
                                   json=login_data,
                                   headers={'Content-Type': 'application/json'})
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print(f"   ✅ Login successful!")
                    return True
                else:
                    print(f"   ❌ Login failed: {result.get('error')}")
            else:
                print(f"   ❌ Request failed: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    return False

def test_new_user_registration():
    """Test new user registration"""
    print("\n🔐 Testing New User Registration...")
    
    registration_data = {
        "email": "newuser@example.com",
        "password": "newpassword123",
        "name": "New User"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/register", 
                               json=registration_data,
                               headers={'Content-Type': 'application/json'})
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("   ✅ Registration successful!")
                return registration_data
            else:
                print(f"   ❌ Registration failed: {result.get('error')}")
        else:
            print(f"   ❌ Request failed: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    return None

def test_new_user_login(user_data):
    """Test login with newly registered user"""
    print(f"\n🔑 Testing New User Login...")
    
    login_data = {
        "email": user_data["email"],
        "password": user_data["password"]
    }
    
    try:
        response = requests.post(f"{BASE_URL}/login", 
                               json=login_data,
                               headers={'Content-Type': 'application/json'})
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("   ✅ New user login successful!")
                return True
            else:
                print(f"   ❌ New user login failed: {result.get('error')}")
        else:
            print(f"   ❌ Request failed: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    return False

def main():
    """Run all tests"""
    print("🧪 Testing User Authentication System...\n")
    
    # Test 1: Existing user login
    existing_user_success = test_existing_user_login()
    
    # Test 2: New user registration
    new_user_data = test_new_user_registration()
    
    # Test 3: New user login
    new_user_success = False
    if new_user_data:
        new_user_success = test_new_user_login(new_user_data)
    
    # Summary
    print("\n" + "="*50)
    print("📊 TEST SUMMARY")
    print("="*50)
    print(f"Existing User Login: {'✅ PASS' if existing_user_success else '❌ FAIL'}")
    print(f"New User Registration: {'✅ PASS' if new_user_data else '❌ FAIL'}")
    print(f"New User Login: {'✅ PASS' if new_user_success else '❌ FAIL'}")
    
    if existing_user_success and new_user_data and new_user_success:
        print("\n🎉 All authentication tests passed!")
    else:
        print("\n⚠️ Some tests failed.")
        print("\n💡 If existing users can't login:")
        print("   1. Run: python migrate_users.py")
        print("   2. Choose option 2 to migrate existing users")
        print("   3. Use the temporary passwords shown")

if __name__ == "__main__":
    main() 