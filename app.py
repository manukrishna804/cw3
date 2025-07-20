from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
import cv2
from cvzone.HandTrackingModule import HandDetector
import time
import json
import os
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore, auth
import google.generativeai as genai
from dotenv import load_dotenv
from functools import wraps
import threading
import time

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-here')

# Initialize Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase-credentials.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

# Initialize Gemini AI
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-pro')

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

# Special gestures
SPACE_GESTURE = [1, 1, 1, 1, 0]  # Four fingers, no pinky (for word separation)
DELETE_GESTURE = [1, 0, 0, 0, 0]  # Only thumb (backspace)
FINISH_GESTURE = [1, 1, 1, 1, 1]  # All fingers (finish word)

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

def login_required(f):
    """Decorator to require login for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

class SignLanguageApp:
    def __init__(self):
        self.cap = None
        self.detector = HandDetector(maxHands=1)
        self.current_exercise = None
        self.user_progress = {}
        self.is_tracking = False
        
        # Word building variables (like in the reference code)
        self.current_word = ""
        self.completed_text = ""
        self.last_recognized = ""
        self.stable_count = 0
        self.required_stability = 15  # Need stable detection
        self.cooldown_time = 1.5  # Seconds between letter captures
        self.last_capture_time = 0
        
    def start_camera(self):
        try:
            if self.cap is None:
                self.cap = cv2.VideoCapture(0)
                if not self.cap.isOpened():
                    print("❌ Failed to open camera")
                    return False
                print("✅ Camera opened successfully")
            return True
        except Exception as e:
            print(f"❌ Camera error: {e}")
            return False
    
    def stop_camera(self):
        try:
            if self.cap:
                self.cap.release()
                self.cap = None
                print("✅ Camera released")
        except Exception as e:
            print(f"❌ Error releasing camera: {e}")
    
    def process_hand_gesture(self, fingers, current_time):
        """Process hand gesture with stable recognition logic"""
        # Find matching gesture
        recognized = "Unknown"
        
        # Check special gestures first
        if fingers == SPACE_GESTURE:
            recognized = "SPACE"
        elif fingers == DELETE_GESTURE:
            recognized = "DELETE"
        elif fingers == FINISH_GESTURE:
            recognized = "FINISH"
        else:
            # Check letter patterns
            for letter, pattern in sign_patterns.items():
                if fingers == pattern:
                    recognized = letter
                    break
        
        # Stable recognition logic (same as reference code)
        if recognized == self.last_recognized and recognized != "Unknown":
            self.stable_count += 1
            if self.stable_count >= self.required_stability and (current_time - self.last_capture_time) > self.cooldown_time:
                # Process the recognized gesture
                result = self.process_stable_gesture(recognized, current_time)
                self.stable_count = 0
                return result
        else:
            self.stable_count = 0
            self.last_recognized = recognized
        
        return {
            'recognized': recognized,
            'stable': False,
            'current_word': self.current_word,
            'completed_text': self.completed_text
        }
    
    def process_stable_gesture(self, recognized, current_time):
        """Process a stable gesture (same logic as reference code)"""
        if recognized == "SPACE":
            if self.current_word:
                self.completed_text += self.current_word + " "
                print(f">>> WORD ADDED: '{self.current_word}'")
                print(f">>> CURRENT TEXT: '{self.completed_text.strip()}'")
                self.current_word = ""
            self.last_capture_time = current_time
            
        elif recognized == "DELETE":
            if self.current_word:
                self.current_word = self.current_word[:-1]
                print(f">>> DELETED LETTER, CURRENT WORD: '{self.current_word}'")
            elif self.completed_text:
                self.completed_text = self.completed_text[:-1]
                print(f">>> DELETED FROM TEXT: '{self.completed_text}'")
            self.last_capture_time = current_time
            
        elif recognized == "FINISH":
            if self.current_word:
                self.completed_text += self.current_word
                print(f">>> FINAL WORD: '{self.current_word}'")
                print(f">>> COMPLETE TEXT: '{self.completed_text}'")
                self.current_word = ""
            self.last_capture_time = current_time
            
        elif recognized in sign_patterns:
            self.current_word += recognized
            print(f">>> LETTER: {recognized}")
            print(f">>> BUILDING WORD: '{self.current_word}'")
            self.last_capture_time = current_time
        
        return {
            'recognized': recognized,
            'stable': True,
            'current_word': self.current_word,
            'completed_text': self.completed_text
        }
    
    def reset_word_building(self):
        """Reset word building state"""
        self.current_word = ""
        self.completed_text = ""
        self.last_recognized = ""
        self.stable_count = 0
        self.last_capture_time = 0
    
    def get_user_progress(self, user_id):
        """Get user progress from Firebase"""
        try:
            doc = db.collection('users').document(user_id).get()
            if doc.exists:
                return doc.to_dict()
            # Initialize new user
            initial_progress = {
                'level': 'beginner', 
                'completed_exercises': [], 
                'current_exercise': None,
                'total_score': 0,
                'created_at': datetime.now(),
                'last_updated': datetime.now()
            }
            self.update_user_progress(user_id, initial_progress)
            return initial_progress
        except Exception as e:
            print(f"Error getting user progress: {e}")
            return {'level': 'beginner', 'completed_exercises': [], 'current_exercise': None, 'total_score': 0}
    
    def update_user_progress(self, user_id, exercise_data):
        """Update user progress in Firebase"""
        try:
            user_ref = db.collection('users').document(user_id)
            user_ref.set({
                'last_updated': datetime.now(),
                'level': exercise_data.get('level', 'beginner'),
                'completed_exercises': exercise_data.get('completed_exercises', []),
                'current_exercise': exercise_data.get('current_exercise'),
                'total_score': exercise_data.get('total_score', 0)
            }, merge=True)
            return True
        except Exception as e:
            print(f"Error updating user progress: {e}")
            return False
    
    def get_learned_letters(self, user_progress):
        """Get letters the user has learned from completed exercises"""
        learned_letters = set()
        completed = user_progress.get('completed_exercises', [])
        
        for exercise in completed:
            if exercise.get('type') == 'alphabet':
                learned_letters.add(exercise.get('target', ''))
            elif exercise.get('type') == 'word_building':
                # Extract letters from completed words
                word = exercise.get('word', '')
                learned_letters.update(list(word))
        
        return list(learned_letters)
    
    def generate_exercise(self, user_progress):
        """Generate exercise using Gemini AI based on user progress"""
        try:
            level = user_progress.get('level', 'beginner')
            completed = user_progress.get('completed_exercises', [])
            
            if level == 'beginner' and len(completed) < 3:
                # Initial exercises: alphabets, numbers, basic mannerisms
                if len(completed) == 0:
                    return {
                        'type': 'alphabet',
                        'target': 'A',
                        'description': 'Show the sign for letter A (thumb only)',
                        'pattern': sign_patterns['A'],
                        'level': 'beginner'
                    }
                elif len(completed) == 1:
                    return {
                        'type': 'number',
                        'target': '1',
                        'description': 'Show the sign for number 1 (index finger only)',
                        'pattern': number_patterns['1'],
                        'level': 'beginner'
                    }
                elif len(completed) == 2:
                    return {
                        'type': 'mannerism',
                        'target': 'HELLO',
                        'description': 'Show the sign for HELLO (thumb and index finger)',
                        'pattern': mannerism_patterns['HELLO'],
                        'level': 'beginner'
                    }
            else:
                # Generate word building exercises using Gemini with learned letters
                learned_letters = self.get_learned_letters(user_progress)
                
                if len(learned_letters) < 3:
                    # If not enough letters learned, continue with alphabet
                    available_letters = [letter for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' 
                                       if letter not in learned_letters]
                    if available_letters:
                        target_letter = available_letters[0]
                        return {
                            'type': 'alphabet',
                            'target': target_letter,
                            'description': f'Show the sign for letter {target_letter}',
                            'pattern': sign_patterns.get(target_letter, [0, 0, 0, 0, 0]),
                            'level': level
                        }
                
                # Generate word using only learned letters
                if model:
                    prompt = f"""
                    Generate a simple word building exercise for sign language learning.
                    User level: {level}
                    Previously completed exercises: {len(completed)}
                    Letters the user has learned: {learned_letters}
                    
                    Generate a simple, common word (3-5 letters) that uses ONLY the letters the user has learned.
                    The word should be appropriate for their level and not too difficult.
                    
                    IMPORTANT: Only use letters from this list: {learned_letters}
                    If there are fewer than 3 letters learned, suggest learning more letters first.
                    
                    Return only the word, nothing else.
                    """
                    
                    try:
                        response = model.generate_content(prompt)
                        word = response.text.strip().upper()
                    except Exception as e:
                        print(f"❌ Gemini AI error: {e}")
                        word = None
                else:
                    # Fallback word generation without AI
                    common_words = ['CAT', 'DOG', 'HAT', 'SUN', 'BIG', 'RED', 'BLUE', 'GREEN', 'BOOK', 'TREE']
                    available_words = [w for w in common_words if all(letter in learned_letters for letter in w)]
                    word = available_words[0] if available_words else None
                
                # Validate that the word only uses learned letters
                if all(letter in learned_letters for letter in word) and len(word) >= 3:
                    return {
                        'type': 'word_building',
                        'target': word,
                        'description': f'Spell the word "{word}" using sign language letters',
                        'level': level,
                        'letters': list(word)
                    }
                else:
                    # Fallback to alphabet learning
                    available_letters = [letter for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' 
                                       if letter not in learned_letters]
                    if available_letters:
                        target_letter = available_letters[0]
                        return {
                            'type': 'alphabet',
                            'target': target_letter,
                            'description': f'Show the sign for letter {target_letter}',
                            'pattern': sign_patterns.get(target_letter, [0, 0, 0, 0, 0]),
                            'level': level
                        }
                
        except Exception as e:
            print(f"Error generating exercise: {e}")
            return {
                'type': 'alphabet',
                'target': 'A',
                'description': 'Show the sign for letter A',
                'pattern': sign_patterns['A'],
                'level': 'beginner'
            }
    
    def recognize_sign(self, fingers):
        """Recognize sign from finger pattern"""
        # Check alphabet patterns
        for letter, pattern in sign_patterns.items():
            if fingers == pattern:
                return letter, 'alphabet'
        
        # Check number patterns
        for number, pattern in number_patterns.items():
            if fingers == pattern:
                return number, 'number'
        
        # Check mannerism patterns
        for mannerism, pattern in mannerism_patterns.items():
            if fingers == pattern:
                return mannerism, 'mannerism'
        
        # Check special gestures
        if fingers == SPACE_GESTURE:
            return 'SPACE', 'special'
        if fingers == DELETE_GESTURE:
            return 'DELETE', 'special'
        if fingers == FINISH_GESTURE:
            return 'FINISH', 'special'
        
        return None, None

# Initialize the app
sign_app = SignLanguageApp()

# Global variables for real-time hand tracking
hand_tracking_data = {
    'fingers': [0, 0, 0, 0, 0],
    'recognized': 'Unknown',
    'stable': False,
    'current_word': '',
    'completed_text': '',
    'hand_detected': False,
    'stable_count': 0,
    'cooldown_remaining': 0,
    'last_update': 0
}

def real_time_hand_tracking():
    """Real-time hand tracking thread - simplified to avoid conflicts"""
    global hand_tracking_data
    
    # Use the existing camera from SignLanguageApp if available
    if sign_app.cap and sign_app.cap.isOpened():
        cap = sign_app.cap
        use_existing_camera = True
    else:
        try:
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                print("❌ Failed to open camera for hand tracking")
                return
            use_existing_camera = False
        except Exception as e:
            print(f"❌ Camera error in hand tracking: {e}")
            return
    
    detector = HandDetector(maxHands=1)
    print("✅ Starting real-time hand tracking...")
    
    # Word building variables
    current_word = ""
    completed_text = ""
    last_recognized = ""
    stable_count = 0
    required_stability = 15
    cooldown_time = 1.5
    last_capture_time = 0
    
    try:
        while sign_app.is_tracking:
            success, img = cap.read()
            if not success:
                continue
            
            hands, img = detector.findHands(img)
            current_time = time.time()
            
            if hands:
                hand = hands[0]
                fingers = detector.fingersUp(hand)
                
                # Find matching gesture
                recognized = "Unknown"
                
                # Check special gestures first
                if fingers == SPACE_GESTURE:
                    recognized = "SPACE"
                elif fingers == DELETE_GESTURE:
                    recognized = "DELETE"
                elif fingers == FINISH_GESTURE:
                    recognized = "FINISH"
                else:
                    # Check letter patterns
                    for letter, pattern in sign_patterns.items():
                        if fingers == pattern:
                            recognized = letter
                            break
                
                # Stable recognition logic
                if recognized == last_recognized and recognized != "Unknown":
                    stable_count += 1
                    if stable_count >= required_stability and (current_time - last_capture_time) > cooldown_time:
                        # Process the recognized gesture
                        if recognized == "SPACE":
                            if current_word:
                                completed_text += current_word + " "
                                current_word = ""
                            last_capture_time = current_time
                            
                        elif recognized == "DELETE":
                            if current_word:
                                current_word = current_word[:-1]
                            elif completed_text:
                                completed_text = completed_text[:-1]
                            last_capture_time = current_time
                            
                        elif recognized == "FINISH":
                            if current_word:
                                completed_text += current_word
                                current_word = ""
                            last_capture_time = current_time
                            
                        elif recognized in sign_patterns:
                            current_word += recognized
                            last_capture_time = current_time
                        
                        stable_count = 0
                else:
                    stable_count = 0
                    last_recognized = recognized
                
                # Update global tracking data
                hand_tracking_data.update({
                    'fingers': fingers,
                    'recognized': recognized,
                    'stable': stable_count >= required_stability and (current_time - last_capture_time) > cooldown_time,
                    'current_word': current_word,
                    'completed_text': completed_text,
                    'hand_detected': True,
                    'stable_count': stable_count,
                    'cooldown_remaining': max(0, cooldown_time - (current_time - last_capture_time)),
                    'last_update': current_time
                })
                
            else:
                # No hand detected
                stable_count = 0
                hand_tracking_data.update({
                    'fingers': [0, 0, 0, 0, 0],
                    'recognized': 'Unknown',
                    'stable': False,
                    'current_word': current_word,
                    'completed_text': completed_text,
                    'hand_detected': False,
                    'stable_count': 0,
                    'cooldown_remaining': 0,
                    'last_update': current_time
                })
            
            # Small delay to control frame rate
            time.sleep(0.1)  # 10 FPS
    
    except Exception as e:
        print(f"❌ Error in hand tracking thread: {e}")
    
    finally:
        # Only release camera if we created it
        if not use_existing_camera and cap:
            cap.release()
        print("✅ Hand tracking thread stopped")

# Start hand tracking thread
hand_tracking_thread = None

def start_hand_tracking_thread():
    """Start the hand tracking thread"""
    global hand_tracking_thread
    if hand_tracking_thread is None or not hand_tracking_thread.is_alive():
        sign_app.is_tracking = True
        hand_tracking_thread = threading.Thread(target=real_time_hand_tracking, daemon=True)
        hand_tracking_thread.start()
        print("✅ Hand tracking thread started")
    else:
        print("⚠️  Hand tracking thread already running")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video-test')
def video_test():
    return render_template('video_test.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        name = data.get('name')
        
        if email and password and name:
            try:
                # Create user in Firebase Auth
                user_record = auth.create_user(
                    email=email,
                    password=password,
                    display_name=name
                )
                
                user_id = user_record.uid
                
                # Initialize user progress in Firestore
                initial_progress = {
                    'level': 'beginner',
                    'completed_exercises': [],
                    'current_exercise': None,
                    'total_score': 0,
                    'created_at': datetime.now(),
                    'last_updated': datetime.now(),
                    'email': email,
                    'name': name
                }
                sign_app.update_user_progress(user_id, initial_progress)
                
                # Set session
                session['user_id'] = user_id
                session['user_email'] = email
                session['user_name'] = name
                
                return jsonify({'success': True, 'redirect': url_for('dashboard')})
            except Exception as e:
                print(f"Registration error: {e}")
                return jsonify({'success': False, 'error': f'Registration failed: {str(e)}'})
        else:
            return jsonify({'success': False, 'error': 'All fields are required'})
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if email and password:
            try:
                # First, try to find user in Firebase Auth
                try:
                    user_record = auth.get_user_by_email(email)
                    user_id = user_record.uid
                    print(f"Found user in Firebase Auth: {user_id}")
                except auth.UserNotFoundError:
                    # User not in Firebase Auth, check if they exist in Firestore (old system)
                    print(f"User not found in Firebase Auth, checking Firestore...")
                    user_id = email.replace('@', '_').replace('.', '_')
                    user_doc = db.collection('users').document(user_id).get()
                    
                    if user_doc.exists:
                        # User exists in Firestore but not in Firebase Auth
                        # Create them in Firebase Auth now
                        try:
                            user_record = auth.create_user(
                                email=email,
                                password=password,
                                display_name=user_doc.to_dict().get('name', email.split('@')[0])
                            )
                            user_id = user_record.uid
                            print(f"Created user in Firebase Auth: {user_id}")
                        except Exception as e:
                            print(f"Failed to create user in Firebase Auth: {e}")
                            # Continue with Firestore user_id for now
                            pass
                    else:
                        return jsonify({'success': False, 'error': 'User not found. Please register first.'})
                
                # Verify user exists in Firestore
                user_doc = db.collection('users').document(user_id).get()
                if user_doc.exists:
                    user_data = user_doc.to_dict()
                    
                    session['user_id'] = user_id
                    session['user_email'] = email
                    session['user_name'] = user_data.get('name', email.split('@')[0])
                    
                    print(f"Login successful for user: {user_id}")
                    return jsonify({'success': True, 'redirect': url_for('dashboard')})
                else:
                    # User exists in Firebase Auth but not in Firestore
                    # Create basic user data in Firestore
                    initial_progress = {
                        'level': 'beginner',
                        'completed_exercises': [],
                        'current_exercise': None,
                        'total_score': 0,
                        'created_at': datetime.now(),
                        'last_updated': datetime.now(),
                        'email': email,
                        'name': email.split('@')[0]
                    }
                    sign_app.update_user_progress(user_id, initial_progress)
                    
                    session['user_id'] = user_id
                    session['user_email'] = email
                    session['user_name'] = email.split('@')[0]
                    
                    print(f"Created Firestore data for existing Firebase Auth user: {user_id}")
                    return jsonify({'success': True, 'redirect': url_for('dashboard')})
                    
            except Exception as e:
                print(f"Login error: {e}")
                return jsonify({'success': False, 'error': f'Login failed: {str(e)}'})
        else:
            return jsonify({'success': False, 'error': 'Email and password are required'})
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/exercise')
@login_required
def exercise():
    return render_template('exercise.html')

@app.route('/progress')
@login_required
def progress():
    return render_template('progress.html')

@app.route('/api/start-exercise', methods=['POST'])
@login_required
def start_exercise():
    user_id = session['user_id']
    
    # Get user progress
    user_progress = sign_app.get_user_progress(user_id)
    
    # Generate exercise
    exercise = sign_app.generate_exercise(user_progress)
    
    # Start camera
    if sign_app.start_camera():
        return jsonify({
            'success': True,
            'exercise': exercise,
            'user_progress': user_progress
        })
    else:
        return jsonify({
            'success': False,
            'error': 'Failed to start camera'
        })

@app.route('/api/hand-tracking', methods=['POST'])
@login_required
def hand_tracking():
    """Get real-time hand tracking data from OpenCV thread"""
    try:
        # Start hand tracking thread if not already running
        start_hand_tracking_thread()
        
        # Get current exercise context
        user_id = session['user_id']
        user_progress = sign_app.get_user_progress(user_id)
        current_exercise = sign_app.generate_exercise(user_progress)
        
        # Return the real-time tracking data
        return jsonify({
            'success': True,
            'fingers': hand_tracking_data['fingers'],
            'recognized_sign': hand_tracking_data['recognized'],
            'stable': hand_tracking_data['stable'],
            'current_word': hand_tracking_data['current_word'],
            'completed_text': hand_tracking_data['completed_text'],
            'exercise': current_exercise,
            'hand_detected': hand_tracking_data['hand_detected'],
            'stable_count': hand_tracking_data['stable_count'],
            'cooldown_remaining': hand_tracking_data['cooldown_remaining']
        })
            
    except Exception as e:
        print(f"Hand tracking error: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/check-sign', methods=['POST'])
@login_required
def check_sign():
    """Check if the recognized sign matches the current exercise"""
    data = request.get_json()
    fingers = data.get('fingers', [])
    current_exercise = data.get('exercise', {})
    user_id = session['user_id']
    
    recognized_sign, sign_type = sign_app.recognize_sign(fingers)
    
    if recognized_sign:
        # Check if it matches the current exercise
        if current_exercise.get('type') == 'word_building':
            # For word building, check if the letter is correct
            target_word = current_exercise.get('target', '')
            current_letters = data.get('current_letters', [])
            
            if recognized_sign in target_word and recognized_sign not in current_letters:
                current_letters.append(recognized_sign)
                is_complete = len(current_letters) == len(target_word)
                
                if is_complete:
                    # Update progress
                    user_progress = sign_app.get_user_progress(user_id)
                    completed = user_progress.get('completed_exercises', [])
                    completed.append({
                        'type': 'word_building',
                        'word': target_word,
                        'completed_at': datetime.now().isoformat()
                    })
                    
                    # Check if ready for next level
                    if len(completed) >= 5:
                        user_progress['level'] = 'intermediate'
                    
                    user_progress['completed_exercises'] = completed
                    user_progress['total_score'] = user_progress.get('total_score', 0) + 10
                    sign_app.update_user_progress(user_id, user_progress)
                
                return jsonify({
                    'success': True,
                    'recognized': recognized_sign,
                    'correct': True,
                    'current_letters': current_letters,
                    'is_complete': is_complete
                })
            else:
                return jsonify({
                    'success': True,
                    'recognized': recognized_sign,
                    'correct': False,
                    'message': 'Letter not needed or already used'
                })
        else:
            # For other exercise types
            target = current_exercise.get('target', '')
            if recognized_sign == target:
                # Update progress
                user_progress = sign_app.get_user_progress(user_id)
                completed = user_progress.get('completed_exercises', [])
                completed.append({
                    'type': current_exercise.get('type'),
                    'target': target,
                    'completed_at': datetime.now().isoformat()
                })
                
                user_progress['completed_exercises'] = completed
                user_progress['total_score'] = user_progress.get('total_score', 0) + 10
                sign_app.update_user_progress(user_id, user_progress)
                
                return jsonify({
                    'success': True,
                    'recognized': recognized_sign,
                    'correct': True,
                    'exercise_complete': True
                })
            else:
                return jsonify({
                    'success': True,
                    'recognized': recognized_sign,
                    'correct': False,
                    'message': f'Try showing the sign for {target}'
                })
    
    return jsonify({
        'success': True,
        'recognized': None,
        'correct': False,
        'message': 'No sign recognized'
    })

@app.route('/api/stop-exercise', methods=['POST'])
@login_required
def stop_exercise():
    try:
        # Stop hand tracking
        sign_app.is_tracking = False
        
        # Stop camera
        sign_app.stop_camera()
        
        # Reset word building state
        sign_app.reset_word_building()
        
        print("✅ Exercise stopped successfully")
        return jsonify({'success': True, 'message': 'Exercise stopped'})
    except Exception as e:
        print(f"❌ Error stopping exercise: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/user-progress/<user_id>')
@login_required
def get_user_progress(user_id):
    # Ensure user can only access their own progress
    if user_id != session['user_id']:
        return jsonify({'error': 'Unauthorized'}), 403
    
    progress = sign_app.get_user_progress(user_id)
    return jsonify(progress)

@app.route('/api/user-progress/current')
@login_required
def get_current_user_progress():
    user_id = session['user_id']
    progress = sign_app.get_user_progress(user_id)
    return jsonify({'success': True, 'progress': progress})

@app.route('/api/reset-word-building', methods=['POST'])
@login_required
def reset_word_building():
    """Reset word building state"""
    global hand_tracking_data
    
    # Reset the global tracking data
    hand_tracking_data.update({
        'current_word': '',
        'completed_text': '',
        'stable_count': 0,
        'cooldown_remaining': 0
    })
    
    # Also reset the sign app state
    sign_app.reset_word_building()
    
    return jsonify({'success': True, 'message': 'Word building reset'})

@app.route('/api/check-word-match', methods=['POST'])
@login_required
def check_word_match():
    """Check if current word matches the target exercise"""
    global hand_tracking_data
    
    data = request.get_json()
    target_word = data.get('target_word', '').upper()
    current_word = hand_tracking_data['current_word'].upper()
    
    if current_word == target_word:
        # Word completed successfully
        user_id = session['user_id']
        user_progress = sign_app.get_user_progress(user_id)
        completed = user_progress.get('completed_exercises', [])
        completed.append({
            'type': 'word_building',
            'word': target_word,
            'completed_at': datetime.now().isoformat()
        })
        
        user_progress['completed_exercises'] = completed
        user_progress['total_score'] = user_progress.get('total_score', 0) + 10
        sign_app.update_user_progress(user_id, user_progress)
        
        # Reset word building for next exercise
        sign_app.reset_word_building()
        
        # Reset global tracking data
        hand_tracking_data.update({
            'current_word': '',
            'completed_text': '',
            'stable_count': 0,
            'cooldown_remaining': 0
        })
        
        return jsonify({
            'success': True,
            'match': True,
            'message': f'Congratulations! You spelled "{target_word}" correctly!'
        })
    else:
        return jsonify({
            'success': True,
            'match': False,
            'current_word': current_word,
            'target_word': target_word,
            'message': f'Current: "{current_word}" | Target: "{target_word}"'
        })

@app.route('/api/start-hand-tracking', methods=['POST'])
@login_required
def start_hand_tracking():
    """Start the hand tracking thread"""
    try:
        start_hand_tracking_thread()
        return jsonify({'success': True, 'message': 'Hand tracking started'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/video_feed')
@login_required
def video_feed():
    """Stream video from the camera"""
    def generate_frames():
        # Make sure camera is started
        if not sign_app.cap or not sign_app.cap.isOpened():
            sign_app.start_camera()
        
        if not sign_app.cap or not sign_app.cap.isOpened():
            # Return a placeholder frame
            import numpy as np
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            # Add text to frame
            import cv2
            cv2.putText(frame, 'Starting camera...', (200, 240), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            ret, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            return
            
        while True:
            success, frame = sign_app.cap.read()
            if not success:
                break
                
            # Add hand tracking visualization
            if sign_app.detector:
                hands, frame = sign_app.detector.findHands(frame)
                if hands:
                    # Draw hand landmarks
                    for hand in hands:
                        # Draw hand outline
                        cv2.rectangle(frame, (hand['bbox'][0], hand['bbox'][1]), 
                                    (hand['bbox'][0] + hand['bbox'][2], hand['bbox'][1] + hand['bbox'][3]), 
                                    (0, 255, 0), 2)
                        
                        # Draw finger status
                        fingers = sign_app.detector.fingersUp(hand)
                        finger_names = ['Thumb', 'Index', 'Middle', 'Ring', 'Pinky']
                        for i, (finger, name) in enumerate(zip(fingers, finger_names)):
                            color = (0, 255, 0) if finger == 1 else (0, 0, 255)
                            cv2.putText(frame, f'{name}: {finger}', (10, 30 + i * 30), 
                                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            
            ret, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    
    return app.response_class(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/simple_video')
def simple_video():
    """Simple video stream without authentication for testing"""
    def generate_frames():
        # Use the existing camera from SignLanguageApp if available
        if sign_app.cap and sign_app.cap.isOpened():
            cap = sign_app.cap
            use_existing = True
        else:
            # Create new camera instance
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                print("❌ Cannot open camera")
                return
            use_existing = False
        
        print("✅ Camera opened for simple video stream")
        
        try:
            while True:
                success, frame = cap.read()
                if not success:
                    print("❌ Failed to read frame")
                    break
                
                # Resize frame for better performance
                frame = cv2.resize(frame, (640, 480))
                
                # Add simple hand tracking visualization
                if sign_app.detector:
                    hands, frame = sign_app.detector.findHands(frame)
                    if hands:
                        for hand in hands:
                            # Draw hand outline
                            cv2.rectangle(frame, (hand['bbox'][0], hand['bbox'][1]), 
                                        (hand['bbox'][0] + hand['bbox'][2], hand['bbox'][1] + hand['bbox'][3]), 
                                        (0, 255, 0), 2)
                            
                            # Draw finger count
                            fingers = sign_app.detector.fingersUp(hand)
                            extended_count = sum(fingers)
                            cv2.putText(frame, f'Fingers: {extended_count}', (10, 30), 
                                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                
                # Encode frame
                ret, buffer = cv2.imencode('.jpg', frame)
                if not ret:
                    continue
                    
                frame_bytes = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        except Exception as e:
            print(f"❌ Error in video stream: {e}")
        finally:
            if not use_existing and cap:
                cap.release()
    
    return app.response_class(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    print("🚀 Starting Sign Language Learning App...")
    print("📝 Make sure you have:")
    print("   - firebase-credentials.json in the project root")
    print("   - .env file with your API keys")
    print("   - Camera access enabled")
    print("=" * 50)
    
    # Don't start hand tracking automatically - let users start it when needed
    app.run(debug=True, host='0.0.0.0', port=5000) 