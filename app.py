from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash, Response
import os
import cv2
import time
import json
from functools import wraps
from dotenv import load_dotenv
import google.generativeai as genai

# Import our new handlers
from db_handler import DBHandler
from camera_handler import CameraHandler

# Load env variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'default-dev-key-123')

# Initialize Handlers
db = DBHandler()
camera = CameraHandler()

# Initialize Gemini (Optional)
GEMINI_KEY = os.getenv('GEMINI_API_KEY')
model = None
if GEMINI_KEY:
    try:
        genai.configure(api_key=GEMINI_KEY)
        model = genai.GenerativeModel('gemini-pro')
        print("✅ Gemini AI Initialized")
    except Exception as e:
        print(f"⚠️ Gemini AI Error: {e}")

# --- Decorators ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# --- Helpers ---
def generate_exercise_logic(level, completed_history):
    """Generates an exercise based on level"""
    # Simple hardcoded progression for stability
    if level == 'beginner':
        exercises = [
            {"type": "alphabet", "target": "A", "description": "Show letter A (Thumb Only)"},
            {"type": "alphabet", "target": "B", "description": "Show letter B (4 Fingers Up)"},
            {"type": "number", "target": "1", "description": "Show Number 1 (Index Finger)"},
            {"type": "mannerism", "target": "HELLO", "description": "Sign HELLO (Wave)"}
        ]
        # Pick one they haven't done if possible, or random
        import random
        return random.choice(exercises)
        
    elif level == 'intermediate':
        # Word building
        words = ["CAT", "DOG", "HI", "YES"]
        import random
        word = random.choice(words)
        return {
            "type": "word_building", 
            "target": word, 
            "description": f"Spell {word}", 
            "letters": list(word)
        }
    
    return {"type": "alphabet", "target": "A", "description": "Default: Letter A"}

# --- Routes ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Handle both JSON (API/Fetch) and Form (Browser default)
        if request.is_json:
            data = request.get_json()
            email = data.get('email')
            password = data.get('password')
        else:
            email = request.form.get('email')
            password = request.form.get('password')
        
        result = db.verify_login(email, password)
        if result['success']:
            session['user_id'] = result['user_id']
            session['user_name'] = result['name']
            
            # Return JSON for fetch requests, Redirect for forms
            if request.is_json:
                return jsonify({'success': True, 'redirect': url_for('dashboard')})
            return redirect(url_for('dashboard'))
        else:
            if request.is_json:
                return jsonify({'success': False, 'error': result['error']})
            flash(result['error'], 'error')
            
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            email = data.get('email')
            password = data.get('password')
            name = data.get('name')
        else:
            email = request.form.get('email')
            password = request.form.get('password')
            name = request.form.get('name')
        
        result = db.create_user(email, password, name)
        if result['success']:
            if request.is_json:
                return jsonify({'success': True, 'redirect': url_for('login')})
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        else:
            if request.is_json:
                return jsonify({'success': False, 'error': result['error']})
            flash(result['error'], 'error')
            
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    progress = db.get_user_progress(session['user_id'])
    # User object for template
    user = {'name': session.get('user_name', 'User')}
    return render_template('dashboard.html', user=user, progress=progress)

@app.route('/exercise')
@login_required
def exercise_page():
    return render_template('exercise.html')

@app.route('/progress')
@login_required
def progress_page():
    progress = db.get_user_progress(session['user_id'])
    user = {'name': session.get('user_name', 'User')}
    return render_template('progress.html', user=user, progress=progress)

# --- API Endpoints ---

@app.route('/api/start-exercise', methods=['POST'])
@login_required
def start_exercise_api():
    try:
        user_id = session['user_id']
        progress = db.get_user_progress(user_id)
        
        level = progress.get('level', 'beginner')
        completed = progress.get('completed_exercises', [])
        
        exercise = generate_exercise_logic(level, completed)
        
        # Start camera
        camera.start_camera()
        camera.set_exercise_target(exercise['target'])
        
        session['current_exercise'] = exercise
        
        return jsonify({
            'success': True,
            'exercise': exercise,
            'user_progress': progress
        })
    except Exception as e:
        print(f"Error starting exercise: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/stop-exercise', methods=['POST'])
@login_required
def stop_exercise_api():
    camera.stop_camera()
    return jsonify({'success': True})

@app.route('/api/hand-tracking', methods=['POST'])
@login_required
def hand_tracking_api():
    """Returns camera analysis data JSON"""
    if not camera.is_running:
        # Start it smoothly if not running
        camera.start_camera()
    
    data = camera.get_data()
    # Remove large frame data from JSON
    if 'frame_feed' in data:
        del data['frame_feed']
        
    return jsonify({
        'success': True,
        'fingers': data['fingers'],
        'recognized_sign': data['recognized'],
        'stable': data['stable'],
        'current_word': data['current_word'],
        'completed_text': data['completed_text'],
        'hand_detected': data['hand_detected'],
        'stable_count': data['stable_count'],
        'cooldown_remaining': data['cooldown_remaining']
    })
    
@app.route('/api/user-progress/current')
@login_required
def get_current_user_progress():
    user_id = session.get('user_id')
    progress = db.get_user_progress(user_id)
    return jsonify(progress)

@app.route('/api/start-hand-tracking', methods=['POST'])
@login_required
def start_tracking_api():
    camera.start_camera()
    return jsonify({'success': True})

@app.route('/api/check-word-match', methods=['POST'])
@login_required
def check_word_match_api():
    data = request.get_json()
    target = data.get('target_word')
    
    # In a real scenario, we might verify against server state
    # For now, if the frontend says it matches (triggered by logic), we confirm and update progress
    
    # Update progress
    user_id = session['user_id']
    progress = db.get_user_progress(user_id)
    
    # Add to completed
    if target:
        completed = progress.get('completed_exercises', [])
        completed.append({'type': 'word_building', 'target': target, 'date': time.time()})
        db.update_user_progress(user_id, {'completed_exercises': completed, 'total_score': progress.get('total_score', 0) + 10})
        
    return jsonify({'success': True, 'match': True, 'message': f'Correct! You spelled {target}'})

@app.route('/api/check-sign', methods=['POST'])
@login_required
def check_sign_api():
    # Legacy support
    return jsonify({'success': True, 'correct': True})

@app.route('/simple_video')
@login_required
def simple_video():
    """Video streaming route. Put this in the src of an img or video tag."""
    def generate():
        while True:
            frame = camera.get_frame()
            if frame is not None:
                # Encode the frame in JPEG format
                (flag, encodedImage) = cv2.imencode(".jpg", frame)
                if not flag:
                    continue
                yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + 
                       bytearray(encodedImage) + b'\r\n')
            else:
                # If no frame, yield a blank or waiting...
                time.sleep(0.1)
            time.sleep(0.03) # Cap stream framerate

    return Response(generate(), mimetype="multipart/x-mixed-replace; boundary=frame")

# --- Run ---
if __name__ == '__main__':
    print("🚀 App Starting...")
    port = int(os.environ.get('PORT', 5000))
    # Threaded=True is important for our camera thread to coexist with Flask
    app.run(host='0.0.0.0', port=port, debug=True, use_reloader=False) 
