#!/usr/bin/env python3
"""
Camera Test for Sign Language Learning App
This version focuses only on camera access and hand tracking
"""

from flask import Flask, render_template, request, jsonify, Response
import cv2
from cvzone.HandTrackingModule import HandDetector
import numpy as np
import threading
import time

app = Flask(__name__)
app.secret_key = 'camera-test-key'

# Initialize camera and hand detector
camera = None
hand_detector = None
is_camera_active = False

def initialize_camera():
    """Initialize camera and hand detector"""
    global camera, hand_detector
    
    try:
        # Try to open camera (usually index 0)
        camera = cv2.VideoCapture(0)
        
        if not camera.isOpened():
            # Try different camera indices
            for i in range(1, 5):
                camera = cv2.VideoCapture(i)
                if camera.isOpened():
                    break
        
        if camera.isOpened():
            # Set camera properties
            camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            camera.set(cv2.CAP_PROP_FPS, 30)
            
            # Initialize hand detector
            hand_detector = HandDetector(
                maxHands=1,
                detectionCon=0.8,
                minTrackCon=0.5
            )
            
            print("✅ Camera initialized successfully!")
            return True
        else:
            print("❌ Could not open camera")
            return False
            
    except Exception as e:
        print(f"❌ Error initializing camera: {e}")
        return False

def generate_frames():
    """Generate camera frames with hand tracking"""
    global camera, hand_detector, is_camera_active
    
    while is_camera_active:
        if camera is None or not camera.isOpened():
            break
            
        success, frame = camera.read()
        if not success:
            break
            
        # Flip frame horizontally for mirror effect
        frame = cv2.flip(frame, 1)
        
        # Find hands in the frame
        hands, frame = hand_detector.findHands(frame, draw=True)
        
        # Process hand landmarks
        if hands:
            hand = hands[0]  # Get first hand
            landmarks = hand["lmList"]
            
            # Draw hand landmarks
            for lm in landmarks:
                cv2.circle(frame, (lm[0], lm[1]), 5, (255, 0, 255), cv2.FILLED)
            
            # Get finger positions
            fingers = hand_detector.fingersUp(hand)
            
            # Display finger count
            finger_text = f"Fingers: {sum(fingers)} - Pattern: {fingers}"
            cv2.putText(frame, finger_text, (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Display hand type
            hand_type = "Left" if hand["type"] == "Left" else "Right"
            cv2.putText(frame, f"Hand: {hand_type}", (10, 60), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Add status text
        status_text = "Camera Active - Show your hand!" if is_camera_active else "Camera Inactive"
        cv2.putText(frame, status_text, (10, frame.shape[0] - 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        # Convert frame to JPEG
        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            break
            
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/')
def index():
    """Main page with camera feed"""
    return render_template('camera_test.html')

@app.route('/video_feed')
def video_feed():
    """Video streaming route"""
    return Response(generate_frames(),
                   mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/start_camera')
def start_camera():
    """Start camera"""
    global is_camera_active
    
    if initialize_camera():
        is_camera_active = True
        return jsonify({'success': True, 'message': 'Camera started successfully'})
    else:
        return jsonify({'success': False, 'message': 'Failed to start camera'})

@app.route('/stop_camera')
def stop_camera():
    """Stop camera"""
    global is_camera_active, camera
    
    is_camera_active = False
    
    if camera:
        camera.release()
        camera = None
    
    return jsonify({'success': True, 'message': 'Camera stopped'})

@app.route('/camera_status')
def camera_status():
    """Get camera status"""
    global camera, is_camera_active
    
    if camera and camera.isOpened():
        return jsonify({
            'active': is_camera_active,
            'opened': True,
            'width': int(camera.get(cv2.CAP_PROP_FRAME_WIDTH)),
            'height': int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
        })
    else:
        return jsonify({
            'active': False,
            'opened': False,
            'width': 0,
            'height': 0
        })

if __name__ == '__main__':
    print("🎥 Starting Camera Test App...")
    print("📱 Open your browser and go to: http://localhost:5000")
    print("🔄 Press Ctrl+C to stop")
    
    try:
        app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)
    except KeyboardInterrupt:
        print("\n👋 Camera test stopped")
    finally:
        if camera:
            camera.release()
