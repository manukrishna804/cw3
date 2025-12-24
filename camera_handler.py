import cv2
from cvzone.HandTrackingModule import HandDetector
import threading
import time
import copy

class CameraHandler:
    def __init__(self):
        self.cap = None
        self.is_running = False
        self.thread = None
        # Shared state
        self.data_lock = threading.Lock()
        self.current_data = {
            'fingers': [0, 0, 0, 0, 0],
            'recognized': 'Unknown',
            'stable': False,
            'current_word': '',
            'completed_text': '',
            'hand_detected': False,
            'stable_count': 0,
            'cooldown_remaining': 0,
            'frame_feed': None 
        }
        
        # Gesture Constants
        self.SPACE_GESTURE = [1, 1, 1, 1, 0]
        self.DELETE_GESTURE = [1, 0, 0, 0, 0]
        self.FINISH_GESTURE = [1, 1, 1, 1, 1]
        
        # Initialize Patterns (Simplified for demo, can be expanded)
        self.sign_patterns = {
            "A": [1, 0, 0, 0, 0], "B": [0, 1, 1, 1, 1], "C": [1, 1, 1, 0, 0],
            "D": [0, 1, 0, 0, 0], "E": [0, 0, 0, 0, 0], "F": [1, 0, 1, 1, 1],
            "G": [1, 1, 0, 0, 0], "H": [0, 1, 1, 0, 0], "I": [0, 0, 0, 0, 1],
            "J": [0, 0, 0, 1, 0], "K": [0, 1, 1, 1, 0], "L": [1, 1, 0, 0, 0],
            "M": [1, 0, 1, 0, 1], "N": [1, 0, 0, 1, 0], "O": [1, 1, 1, 1, 1],
            "P": [1, 1, 1, 0, 1], "Q": [1, 0, 1, 1, 0], "R": [0, 1, 1, 0, 1],
            "S": [0, 0, 0, 0, 0], "T": [1, 0, 0, 0, 1], "U": [0, 1, 1, 0, 0],
            "V": [0, 1, 1, 0, 0], "W": [0, 1, 1, 1, 0], "X": [0, 1, 0, 1, 0],
            "Y": [1, 0, 0, 0, 1], "Z": [0, 0, 1, 0, 0]
        }
        
        self.current_exercise_target = None

    def start_camera(self):
        if self.is_running:
            return
        
        self.is_running = True
        self.thread = threading.Thread(target=self._process_feed, daemon=True)
        self.thread.start()

    def stop_camera(self):
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=1.0)
            
    def set_exercise_target(self, target):
        self.current_exercise_target = target

    def get_data(self):
        with self.data_lock:
            return copy.deepcopy(self.current_data)

    def get_frame(self):
        with self.data_lock:
            return self.current_data.get('frame_feed')

    def _process_feed(self):
        print("📷 Starting Camera Feed...")
        try:
            self.cap = cv2.VideoCapture(0)
            detector = HandDetector(maxHands=1)
            
            # Logic variables
            current_word = ""
            completed_text = ""
            last_recognized = "Unknown"
            stable_count = 0
            required_stability = 10
            cooldown_time = 1.5
            last_capture_time = 0
            
            while self.is_running:
                success, img = self.cap.read()
                if not success:
                    time.sleep(0.1)
                    continue
                
                # Flip for mirror effect
                img = cv2.flip(img, 1)
                
                # Draw landmarks for visual feedback
                hands, img = detector.findHands(img, draw=True, flipType=False) 
                
                detected_info = {}
                current_time = time.time()
                
                if hands:
                    hand = hands[0]
                    fingers = detector.fingersUp(hand)
                    detected_info['fingers'] = fingers
                    detected_info['hand_detected'] = True
                    
                    # Recognition
                    recognized = "Unknown"
                    if fingers == self.SPACE_GESTURE: recognized = "SPACE"
                    elif fingers == self.DELETE_GESTURE: recognized = "DELETE"
                    elif fingers == self.FINISH_GESTURE: recognized = "FINISH"
                    else:
                        found = False
                        # Direct pattern match
                        for char, pattern in self.sign_patterns.items():
                            if fingers == pattern:
                                recognized = char
                                found = True
                                break
                        
                        # Heuristics for difficult letters
                        if not found:
                            # A often looks like E/S/M (closed fist 00000)
                            if fingers == [0, 0, 0, 0, 0]: 
                                recognized = 'A' # Default to A for closed fist for beginner friendliness
                    
                    detected_info['recognized'] = recognized
                    
                    # Stability Check
                    if recognized == last_recognized and recognized != "Unknown":
                        stable_count += 1
                    else:
                        stable_count = 0
                        last_recognized = recognized
                    
                    detect_stable = (stable_count >= required_stability)
                    
                    if detect_stable and (current_time - last_capture_time > cooldown_time):
                        # Action Trigger
                        if recognized == "SPACE":
                             completed_text += current_word + " "
                             current_word = ""
                             last_capture_time = current_time
                        elif recognized == "DELETE":
                            if current_word: current_word = current_word[:-1]
                            last_capture_time = current_time
                        elif len(recognized) == 1: # Character
                            current_word += recognized
                            last_capture_time = current_time
                        
                        stable_count = 0 # Reset after capture
                    
                    detected_info['stable'] = detect_stable
                    detected_info['stable_count'] = stable_count
                    detected_info['current_word'] = current_word
                    detected_info['completed_text'] = completed_text
                    detected_info['cooldown_remaining'] = max(0, cooldown_time - (last_capture_time - current_time)) # Fix calc
                    
                else:
                    detected_info['hand_detected'] = False
                    detected_info['fingers'] = [0,0,0,0,0]
                    detected_info['recognized'] = "Unknown"
                    stable_count = 0
                
                # Update Shared State
                with self.data_lock:
                    self.current_data.update(detected_info)
                    self.current_data['frame_feed'] = img
                
                time.sleep(0.03) # ~30fps cap
                
        except Exception as e:
            print(f"❌ Camera Error: {e}")
        finally:
            if self.cap:
                self.cap.release()
            print("📷 Camera Feed Stopped")
