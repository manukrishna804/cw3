#!/usr/bin/env python3
"""
Sign Language Learning App - No Firebase Version
This version works without external dependencies for testing
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
import cv2
from cvzone.HandTrackingModule import HandDetector
import time
import json
import os
from datetime import datetime
import google.generativeai as genai
from dotenv import load_dotenv
from functools import wraps
import threading
import time

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'demo-secret-key-123')

# Initialize Gemini AI (optional)
try:
    genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
    model = genai.GenerativeModel('gemini-pro')
    AI_AVAILABLE = True
except:
    AI_AVAILABLE = False
    print("⚠️ Gemini AI not available - using demo mode")

# Sign patterns for letters A-Z (simplified patterns)
sign_patterns = {
    "A": [1, 0, 0, 0, 0],  # Thumb only
    "B": [0, 1, 1, 1, 1],  # Four fingers up
    "C": [1, 1, 1, 0, 0],  # Thumb, index, middle
    "D": [0, 1, 0, 0, 0],  # Index finger only
    "E": [0, 0, 0, 0, 0],  # Closed fist
    "F": [1, 0, 1, 1, 1],  # Thumb, middle, ring, pinky
    "G": [1, 1, 0, 0, 0],  # Thumb and index
    "H": [0, 1, 1, 0, 0],  # Index and middle
    "I": [0, 0, 0, 0, 1],  # Pinky only
    "J": [0, 0, 0, 1, 0],  # Ring finger only
    "K": [0, 1, 1, 1, 0],  # Index, middle, ring
    "L": [1, 1, 0, 0, 0],  # Thumb and index (L shape)
    "M": [1, 0, 1, 0, 1],  # Thumb, middle, pinky
    "N": [1, 0, 0, 1, 0],  # Thumb and ring
    "O": [1, 1, 1, 1, 1],  # All fingers (circle shape)
    "P": [1, 1, 1, 0, 1],  # Thumb, index, middle, pinky
    "Q": [1, 0, 1, 1, 0],  # Thumb, middle, ring
    "R": [0, 1, 1, 0, 1],  # Index, middle, pinky
    "S": [0, 0, 0, 0, 0],  # Same as E - closed fist
    "T": [1, 0, 0, 0, 1],  # Thumb and pinky
    "U": [0, 1, 1, 0, 0],  # Index and middle together
    "V": [0, 1, 1, 0, 0],  # Same as U - peace sign
    "W": [0, 1, 1, 1, 0],  # Three fingers up
    "X": [0, 1, 0, 1, 0],  # Index and ring
    "Y": [1, 0, 0, 0, 1],  # Thumb and pinky (hang loose)
    "Z": [0, 0, 1, 0, 0],  # Middle finger only
}

# Number patterns
number_patterns = {
    "0": [0, 0, 0, 0, 0],  # Closed fist
    "1": [0, 1, 0, 0, 0],  # Index finger only
    "2": [0, 1, 1, 0, 0],  # Index and middle
    "3": [0, 1, 1, 1, 0],  # Index, middle, ring
    "4": [0, 1, 1, 1, 1],  # Four fingers
    "5": [1, 1, 1, 1, 1],  # All fingers
    "6": [1, 0, 0, 0, 0],  # Thumb only
    "7": [1, 1, 0, 0, 0],  # Thumb and index
    "8": [1, 1, 1, 0, 0],  # Thumb, index, middle
    "9": [1, 1, 1, 1, 0],  # Thumb, index, middle, ring
}

# Basic mannerisms
mannerism_patterns = {
    "HELLO": [1, 1, 0, 0, 0],  # Thumb and index (wave)
    "THANK YOU": [1, 0, 0, 0, 0],  # Thumb up
    "PLEASE": [1, 1, 1, 0, 0],  # Three fingers
    "GOOD": [1, 1, 0, 0, 0],  # Thumb and index
    "BAD": [0, 0, 0, 0, 0],  # Closed fist
    "YES": [1, 1, 1, 1, 1],  # All fingers
    "NO": [0, 0, 0, 0, 0],  # Closed fist
    "SORRY": [1, 0, 0, 0, 1],  # Thumb and pinky
}

# Demo user data (in-memory storage)
demo_users = {
    "demo@test.com": {
        "password": "demo123",
        "name": "Demo User",
        "progress": {
            "level": "beginner",
            "completed_exercises": [],
            "total_score": 0
        }
    }
}

# Demo session data
demo_sessions = {}

def login_required(f):
    """Decorator to require login for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def generate_exercise(user_level="beginner"):
    """Generate exercise based on user level"""
    if user_level == "beginner":
        # Simple exercises for beginners
        exercises = [
            {"type": "alphabet", "target": "A", "description": "Show the sign for letter A (thumb only)"},
            {"type": "alphabet", "target": "B", "description": "Show the sign for letter B (four fingers up)"},
            {"type": "number", "target": "1", "description": "Show the sign for number 1 (index finger only)"},
            {"type": "mannerism", "target": "HELLO", "description": "Show the sign for HELLO (thumb and index)"}
        ]
        return exercises[0]  # Start with first exercise
    else:
        # More complex exercises for intermediate users
        return {"type": "word_building", "target": "CAT", "description": "Spell the word CAT using sign language letters"}

@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        if email in demo_users and demo_users[email]['password'] == password:
            session['user_id'] = email
            session['user_name'] = demo_users[email]['name']
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Register page"""
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        name = request.form['name']
        
        if email in demo_users:
            flash('Email already registered', 'error')
        else:
            demo_users[email] = {
                "password": password,
                "name": name,
                "progress": {
                    "level": "beginner",
                    "completed_exercises": [],
                    "total_score": 0
                }
            }
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard"""
    user_email = session['user_id']
    user_data = demo_users[user_email]
    
    return render_template('dashboard.html', 
                         user=user_data, 
                         progress=user_data['progress'])

@app.route('/exercise')
@login_required
def exercise():
    """Exercise page"""
    return render_template('exercise.html')

@app.route('/progress')
@login_required
def progress():
    """Progress tracking page"""
    user_email = session['user_id']
    user_data = demo_users[user_email]
    
    return render_template('progress.html', 
                         user=user_data, 
                         progress=user_data['progress'])

@app.route('/logout')
def logout():
    """Logout user"""
    session.clear()
    flash('Logged out successfully', 'success')
    return redirect(url_for('index'))

@app.route('/api/start-exercise', methods=['POST'])
@login_required
def start_exercise():
    """Start a new exercise"""
    try:
        user_email = session['user_id']
        user_data = demo_users[user_email]
        
        # Generate exercise based on user level
        exercise = generate_exercise(user_data['progress']['level'])
        
        # Store exercise in session
        if 'current_exercise' not in session:
            session['current_exercise'] = exercise
        
        return jsonify({
            'success': True,
            'exercise': exercise
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/check-sign', methods=['POST'])
@login_required
def check_sign():
    """Check if the sign matches the current exercise"""
    try:
        data = request.get_json()
        fingers = data.get('fingers', [])
        
        if not fingers or len(fingers) != 5:
            return jsonify({
                'success': False,
                'error': 'Invalid finger data'
            })
        
        # Check against all patterns
        recognized_sign = None
        sign_type = None
        
        # Check alphabet patterns
        for letter, pattern in sign_patterns.items():
            if fingers == pattern:
                recognized_sign = letter
                sign_type = 'alphabet'
                break
        
        # Check number patterns
        if not recognized_sign:
            for number, pattern in number_patterns.items():
                if fingers == pattern:
                    recognized_sign = number
                    sign_type = 'number'
                    break
        
        # Check mannerism patterns
        if not recognized_sign:
            for mannerism, pattern in mannerism_patterns.items():
                if fingers == pattern:
                    recognized_sign = mannerism
                    sign_type = 'mannerism'
                    break
        
        if recognized_sign:
            # Check if it matches current exercise
            current_exercise = session.get('current_exercise')
            if current_exercise and recognized_sign == current_exercise['target']:
                # Exercise completed!
                user_email = session['user_id']
                user_data = demo_users[user_email]
                
                # Update progress
                user_data['progress']['completed_exercises'].append({
                    'type': current_exercise['type'],
                    'target': current_exercise['target'],
                    'completed_at': datetime.now().isoformat()
                })
                
                user_data['progress']['total_score'] += 10
                
                # Check if ready for next level
                if len(user_data['progress']['completed_exercises']) >= 5:
                    user_data['progress']['level'] = 'intermediate'
                
                # Clear current exercise
                session.pop('current_exercise', None)
                
                return jsonify({
                    'success': True,
                    'correct': True,
                    'recognized': recognized_sign,
                    'message': f'Correct! You signed {recognized_sign}',
                    'exercise_complete': True,
                    'new_level': user_data['progress']['level']
                })
            else:
                return jsonify({
                    'success': True,
                    'correct': False,
                    'recognized': recognized_sign,
                    'message': f'You signed {recognized_sign}, but the target is {current_exercise["target"] if current_exercise else "unknown"}'
                })
        else:
            return jsonify({
                'success': True,
                'correct': False,
                'recognized': None,
                'message': 'No sign recognized'
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/user-progress/<user_id>')
@login_required
def get_user_progress(user_id):
    """Get user progress data"""
    try:
        user_email = session['user_id']
        if user_email != user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'})
        
        user_data = demo_users[user_email]
        return jsonify({
            'success': True,
            'progress': user_data['progress']
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

if __name__ == '__main__':
    print("🚀 Starting Sign Language Learning App (No Firebase)")
    print("📱 Open your browser and go to: http://localhost:5000")
    print("🔑 Demo login: demo@test.com / demo123")
    print("🔄 Press Ctrl+C to stop")
    
    try:
        app.run(host='0.0.0.0', port=5000, debug=True)
    except KeyboardInterrupt:
        print("\n👋 App stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting app: {e}")
