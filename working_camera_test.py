#!/usr/bin/env python3
"""
Working Camera Test - This will definitely work and stay open
"""

import cv2
from cvzone.HandTrackingModule import HandDetector
import time

def main():
    print("🎥 Working Camera Test")
    print("=" * 40)
    print("This test will open the camera and KEEP IT OPEN")
    print("You should see a camera window that stays open")
    print("=" * 40)
    
    # Initialize camera
    print("🔄 Opening camera...")
    camera = cv2.VideoCapture(0)
    
    if not camera.isOpened():
        print("❌ Could not open camera at index 0")
        # Try other indices
        for i in range(1, 5):
            print(f"🔄 Trying camera index {i}...")
            camera = cv2.VideoCapture(i)
            if camera.isOpened():
                print(f"✅ Camera opened at index {i}")
                break
        
        if not camera.isOpened():
            print("❌ No camera found!")
            return
    
    # Initialize hand detector
    print("🖐️ Initializing hand detector...")
    hand_detector = HandDetector(
        maxHands=1,
        detectionCon=0.8,
        minTrackCon=0.5
    )
    
    # Set camera properties
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    camera.set(cv2.CAP_PROP_FPS, 30)
    
    print("✅ Camera and hand detector ready!")
    print("🖼️ Camera window should open now...")
    print("📱 The window will stay open until you press 'q'")
    print("=" * 50)
    
    frame_count = 0
    start_time = time.time()
    
    # Create a named window that will stay open
    cv2.namedWindow("🎥 Working Camera Test", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("🎥 Working Camera Test", 640, 480)
    
    try:
        while True:
            ret, frame = camera.read()
            if not ret:
                print("❌ Failed to read frame")
                break
            
            # Flip frame horizontally for mirror effect
            frame = cv2.flip(frame, 1)
            
            # Find hands
            hands, frame = hand_detector.findHands(frame, draw=True)
            
            # Process hand data
            if hands:
                hand = hands[0]
                landmarks = hand["lmList"]
                
                # Get finger positions
                fingers = hand_detector.fingersUp(hand)
                finger_count = sum(fingers)
                
                # Display information
                cv2.putText(frame, f"Hand: {hand['type']}", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(frame, f"Fingers: {finger_count}", (10, 60), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(frame, f"Pattern: {fingers}", (10, 90), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                # Draw hand landmarks
                for lm in landmarks:
                    cv2.circle(frame, (lm[0], lm[1]), 5, (255, 0, 255), cv2.FILLED)
            else:
                cv2.putText(frame, "No hand detected", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
            # Display frame info
            cv2.putText(frame, f"Frame: {frame_count}", (10, frame.shape[0] - 60), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            # Calculate FPS
            frame_count += 1
            elapsed_time = time.time() - start_time
            if elapsed_time > 0:
                fps = frame_count / elapsed_time
                cv2.putText(frame, f"FPS: {fps:.1f}", (10, frame.shape[0] - 40), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            # Display instructions
            cv2.putText(frame, "Press 'q' to quit, 's' to save", (10, frame.shape[0] - 20), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
            
            # Show frame in the named window
            cv2.imshow("🎥 Working Camera Test", frame)
            
            # CRITICAL: This is what keeps the window open
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q'):
                print("👋 Quitting camera test...")
                break
            elif key == ord('s'):
                filename = f"working_camera_{int(time.time())}.jpg"
                cv2.imwrite(filename, frame)
                print(f"💾 Saved image as {filename}")
            
            # Small delay to prevent high CPU usage
            time.sleep(0.01)
            
    except KeyboardInterrupt:
        print("\n👋 Camera test interrupted by user")
    except Exception as e:
        print(f"❌ Error in camera loop: {e}")
    
    # Cleanup
    camera.release()
    cv2.destroyAllWindows()
    print("✅ Working camera test completed!")

if __name__ == "__main__":
    main()
