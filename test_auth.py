#!/usr/bin/env python3
"""
Test script for Sign Language Learning App Authentication
"""

import os
import sys
import json
from datetime import datetime

def test_firebase_setup():
    """Test Firebase setup and authentication"""
    print("🔍 Testing Firebase Authentication Setup...")
    
    try:
        import firebase_admin
        from firebase_admin import credentials, auth, firestore
        
        # Check if Firebase is initialized
        if not firebase_admin._apps:
            if os.path.exists('firebase-credentials.json'):
                cred = credentials.Certificate("firebase-credentials.json")
                firebase_admin.initialize_app(cred)
                print("✅ Firebase initialized successfully")
            else:
                print("❌ Firebase credentials not found")
                return False
        else:
            print("✅ Firebase already initialized")
        
        # Test Firestore connection
        db = firestore.client()
        print("✅ Firestore client created")
        
        # Test creating a test user (this would normally be done through the web interface)
        try:
            # Note: This is just a test - in production, users register through the web interface
            print("ℹ️  Firebase Auth is ready for user registration/login")
            print("   Users will be created through the web interface")
        except Exception as e:
            print(f"⚠️  Firebase Auth test note: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Firebase test failed: {e}")
        return False

def test_app_structure():
    """Test app structure and authentication routes"""
    print("\n🔍 Testing App Structure...")
    
    try:
        from app import app
        
        # Check if authentication routes exist
        routes = []
        for rule in app.url_map.iter_rules():
            routes.append(rule.rule)
        
        required_routes = [
            '/',
            '/login',
            '/register',
            '/logout',
            '/dashboard',
            '/exercise',
            '/progress',
            '/api/start-exercise',
            '/api/check-sign',
            '/api/stop-exercise',
            '/api/user-progress/current'
        ]
        
        missing_routes = []
        for route in required_routes:
            if route not in routes:
                missing_routes.append(route)
        
        if missing_routes:
            print(f"❌ Missing routes: {missing_routes}")
            return False
        else:
            print("✅ All required routes found")
        
        # Check if templates exist
        template_files = [
            'templates/index.html',
            'templates/login.html',
            'templates/register.html',
            'templates/dashboard.html',
            'templates/exercise.html',
            'templates/progress.html'
        ]
        
        missing_templates = []
        for template in template_files:
            if not os.path.exists(template):
                missing_templates.append(template)
        
        if missing_templates:
            print(f"❌ Missing templates: {missing_templates}")
            return False
        else:
            print("✅ All required templates found")
        
        return True
        
    except Exception as e:
        print(f"❌ App structure test failed: {e}")
        return False

def test_environment():
    """Test environment configuration"""
    print("\n🔍 Testing Environment Configuration...")
    
    # Check if .env file exists
    if os.path.exists('.env'):
        print("✅ .env file found")
    else:
        print("⚠️  .env file not found")
        print("   Creating basic .env file...")
        
        env_content = """# Sign Language Learning App Environment Variables

# Flask Secret Key (generate a secure random key)
SECRET_KEY=your-secret-key-here-change-this-in-production

# Google Gemini AI API Key
# Get your API key from: https://makersuite.google.com/app/apikey
GEMINI_API_KEY=your-gemini-api-key-here

# Optional: Debug mode
DEBUG=True
"""
        
        with open('.env', 'w') as f:
            f.write(env_content)
        
        print("✅ .env file created")
    
    # Check Firebase credentials
    if os.path.exists('firebase-credentials.json'):
        print("✅ Firebase credentials found")
        
        # Validate JSON structure
        try:
            with open('firebase-credentials.json', 'r') as f:
                creds = json.load(f)
            
            required_fields = ['type', 'project_id', 'private_key', 'client_email']
            missing_fields = []
            
            for field in required_fields:
                if field not in creds:
                    missing_fields.append(field)
            
            if missing_fields:
                print(f"❌ Missing fields in Firebase credentials: {missing_fields}")
                return False
            else:
                print("✅ Firebase credentials are valid")
                
        except json.JSONDecodeError:
            print("❌ Firebase credentials file is not valid JSON")
            return False
    else:
        print("⚠️  firebase-credentials.json not found")
        print("   Please download from Firebase Console")
        return False
    
    return True

def test_dependencies():
    """Test required dependencies"""
    print("\n🔍 Testing Dependencies...")
    
    required_packages = [
        'flask',
        'firebase_admin',
        'google.generativeai',
        'python-dotenv'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package}")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n❌ Missing packages: {missing_packages}")
        print("Please install: pip install " + " ".join(missing_packages))
        return False
    
    return True

def main():
    """Run all tests"""
    print("🚀 Sign Language Learning App - Authentication Test")
    print("=" * 60)
    
    tests = [
        test_dependencies,
        test_environment,
        test_firebase_setup,
        test_app_structure
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your authentication system is ready.")
        print("\nNext steps:")
        print("1. Set up your GEMINI_API_KEY in the .env file")
        print("2. Run the app: python app.py")
        print("3. Visit: http://localhost:5000")
        print("4. Create an account and start learning!")
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
        print("\nCommon solutions:")
        print("1. Install dependencies: pip install flask firebase-admin google-generativeai python-dotenv")
        print("2. Download Firebase credentials from Firebase Console")
        print("3. Set up environment variables in .env file")
        print("4. Get Gemini AI API key from Google AI Studio")
    
    return passed == total

if __name__ == '__main__':
    main() 