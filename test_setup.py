#!/usr/bin/env python3
"""
Test script to verify the Sign Language Learning App setup
"""

import sys
import importlib
import os

def test_imports():
    """Test if all required packages can be imported"""
    print("🔍 Testing package imports...")
    
    required_packages = [
        'flask',
        'cv2',
        'cvzone',
        'mediapipe',
        'firebase_admin',
        'google.generativeai',
        'dotenv'
    ]
    
    failed_imports = []
    
    for package in required_packages:
        try:
            importlib.import_module(package)
            print(f"✅ {package}")
        except ImportError as e:
            print(f"❌ {package}: {e}")
            failed_imports.append(package)
    
    if failed_imports:
        print(f"\n❌ Failed to import: {', '.join(failed_imports)}")
        print("Please install missing packages: pip install -r requirements.txt")
        return False
    else:
        print("\n✅ All packages imported successfully!")
        return True

def test_environment():
    """Test environment configuration"""
    print("\n🔍 Testing environment configuration...")
    
    # Check if .env file exists
    if os.path.exists('.env'):
        print("✅ .env file found")
    else:
        print("⚠️  .env file not found")
        print("   Copy env_example.txt to .env and configure your API keys")
    
    # Check if firebase credentials exist
    if os.path.exists('firebase-credentials.json'):
        print("✅ Firebase credentials found")
    else:
        print("⚠️  firebase-credentials.json not found")
        print("   Download from Firebase Console and save in project root")
    
    # Check for required environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = ['SECRET_KEY', 'GEMINI_API_KEY']
    missing_vars = []
    
    for var in required_vars:
        if os.getenv(var):
            print(f"✅ {var} is set")
        else:
            print(f"❌ {var} is not set")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n⚠️  Missing environment variables: {', '.join(missing_vars)}")
        print("   Please set them in your .env file")
        return False
    
    return True

def test_flask_app():
    """Test Flask app initialization"""
    print("\n🔍 Testing Flask app...")
    
    try:
        from app import app
        print("✅ Flask app imported successfully")
        
        # Test basic route
        with app.test_client() as client:
            response = client.get('/')
            if response.status_code == 200:
                print("✅ Home route working")
            else:
                print(f"❌ Home route failed: {response.status_code}")
                return False
        
        return True
    except Exception as e:
        print(f"❌ Flask app test failed: {e}")
        return False

def test_opencv():
    """Test OpenCV functionality"""
    print("\n🔍 Testing OpenCV...")
    
    try:
        import cv2
        print("✅ OpenCV imported successfully")
        
        # Test camera access
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            print("✅ Camera access working")
            cap.release()
        else:
            print("⚠️  Camera not accessible (this is normal if no camera is connected)")
        
        return True
    except Exception as e:
        print(f"❌ OpenCV test failed: {e}")
        return False

def test_firebase():
    """Test Firebase connection"""
    print("\n🔍 Testing Firebase...")
    
    try:
        import firebase_admin
        from firebase_admin import credentials, firestore
        
        # Check if already initialized
        if not firebase_admin._apps:
            if os.path.exists('firebase-credentials.json'):
                cred = credentials.Certificate("firebase-credentials.json")
                firebase_admin.initialize_app(cred)
                print("✅ Firebase initialized successfully")
            else:
                print("⚠️  Firebase credentials not found")
                return False
        else:
            print("✅ Firebase already initialized")
        
        # Test Firestore connection
        db = firestore.client()
        print("✅ Firestore client created")
        
        return True
    except Exception as e:
        print(f"❌ Firebase test failed: {e}")
        return False

def test_gemini():
    """Test Gemini AI connection"""
    print("\n🔍 Testing Gemini AI...")
    
    try:
        import google.generativeai as genai
        from dotenv import load_dotenv
        
        load_dotenv()
        api_key = os.getenv('GEMINI_API_KEY')
        
        if not api_key:
            print("❌ GEMINI_API_KEY not found in environment")
            return False
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')
        print("✅ Gemini AI configured successfully")
        
        return True
    except Exception as e:
        print(f"❌ Gemini AI test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Sign Language Learning App - Setup Test")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_environment,
        test_flask_app,
        test_opencv,
        test_firebase,
        test_gemini
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your setup is ready.")
        print("\nTo run the application:")
        print("python app.py")
        print("\nThen visit: http://localhost:5000")
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
        print("\nCommon solutions:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Set up environment variables in .env file")
        print("3. Download Firebase credentials")
        print("4. Get Gemini AI API key from Google AI Studio")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 