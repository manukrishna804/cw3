#!/usr/bin/env python3
"""
Startup script for Sign Language Learning App
"""

import os
import sys
import subprocess
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    try:
        import flask
        import cv2
        import cvzone
        import mediapipe
        print("✅ All core dependencies found")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please install dependencies: pip install -r requirements.txt")
        return False

def check_environment():
    """Check environment configuration"""
    print("🔍 Checking environment...")
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("⚠️  .env file not found")
        print("   Creating .env from template...")
        
        if os.path.exists('env_example.txt'):
            with open('env_example.txt', 'r') as f:
                content = f.read()
            
            with open('.env', 'w') as f:
                f.write(content)
            
            print("✅ .env file created from template")
            print("   Please edit .env file with your API keys")
            return False
        else:
            print("❌ env_example.txt not found")
            return False
    
    # Check Firebase credentials
    if not os.path.exists('firebase-credentials.json'):
        print("⚠️  firebase-credentials.json not found")
        print("   Please download from Firebase Console")
        print("   The app will run in demo mode without Firebase")
    
    return True

def run_app():
    """Run the Flask application"""
    print("🚀 Starting Sign Language Learning App...")
    
    # Set default port
    port = os.getenv('PORT', 5000)
    
    try:
        # Import and run the app
        from app import app
        
        print(f"✅ App loaded successfully")
        print(f"🌐 Server starting on http://localhost:{port}")
        print("📱 Open your browser and navigate to the URL above")
        print("🔄 Press Ctrl+C to stop the server")
        print("-" * 50)
        
        app.run(
            host='0.0.0.0',
            port=port,
            debug=os.getenv('DEBUG', 'True').lower() == 'true'
        )
        
    except ImportError as e:
        print(f"❌ Error importing app: {e}")
        print("Please check your installation and dependencies")
        return False
    except Exception as e:
        print(f"❌ Error starting app: {e}")
        return False

def run_demo():
    """Run the demo version"""
    print("🎮 Running in demo mode...")
    print("This mode simulates the app without external dependencies")
    
    try:
        from demo import main
        main()
    except ImportError:
        print("❌ Demo module not found")
        return False
    except Exception as e:
        print(f"❌ Error running demo: {e}")
        return False

def main():
    """Main function"""
    print("🤟 Sign Language Learning App")
    print("=" * 40)
    
    # Check if running in demo mode
    if len(sys.argv) > 1 and sys.argv[1] == 'demo':
        run_demo()
        return
    
    # Check dependencies
    if not check_dependencies():
        print("\n💡 Try running in demo mode:")
        print("   python run.py demo")
        return
    
    # Check environment
    env_ok = check_environment()
    
    if not env_ok:
        print("\n⚠️  Environment not fully configured")
        print("The app may not work properly without API keys")
        print("You can still try running it, or use demo mode:")
        print("   python run.py demo")
        
        response = input("\nContinue anyway? (y/n): ").lower()
        if response != 'y':
            return
    
    # Run the app
    run_app()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 App stopped by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("Please check the error message above") 