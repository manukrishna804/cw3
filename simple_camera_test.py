#!/usr/bin/env python3
"""
Simple Camera Test - Standalone version
Tests camera access and hand tracking without Flask
"""

import cv2
from cvzone.HandTrackingModule import HandDetector
import time
import numpy as np # Added missing import for np

def test_camera():
    """Test basic camera functionality"""
    print("🎥 Testing Camera Access...")
    
    # Try to open camera
    camera = cv2.VideoCapture(0)
    
    if not camera.isOpened():
        print("❌ Could not open camera at index 0")
        
        # Try other camera indices
        for i in range(1, 5):
            print(f"🔄 Trying camera index {i}...")
            camera = cv2.VideoCapture(i)
            if camera.isOpened():
                print(f"✅ Camera opened at index {i}")
                break
        
        if not camera.isOpened():
            print("❌ No camera found at any index")
            return False
    
    # Get camera properties
    width = int(camera.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = camera.get(cv2.CAP_PROP_FPS)
    
    print(f"📊 Camera Properties:")
    print(f"   Resolution: {width}x{height}")
    print(f"   FPS: {fps}")
    
    # Test reading a frame
    ret, frame = camera.read()
    if ret:
        print("✅ Successfully read frame from camera")
    else:
        print("❌ Failed to read frame from camera")
        camera.release()
        return False
    
    camera.release()
    return True

def test_hand_tracking():
    """Test hand tracking functionality"""
    print("\n🖐️ Testing Hand Tracking...")
    
    try:
        # Initialize hand detector
        hand_detector = HandDetector(
            maxHands=1,
            detectionCon=0.8,
            minTrackCon=0.5
        )
        print("✅ Hand detector initialized successfully")
        
        # Test with a sample image (black image)
        sample_image = cv2.imread("sample.jpg") if cv2.imread("sample.jpg") is not None else np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Test hand detection
        hands, processed_image = hand_detector.findHands(sample_image)
        print(f"✅ Hand detection test passed - Found {len(hands)} hands")
        
        return True
        
    except Exception as e:
        print(f"❌ Hand tracking test failed: {e}")
        return False

def interactive_camera_test():
    """Interactive camera test with real-time hand tracking"""
    print("\n🎮 Starting Interactive Camera Test...")
    print("📱 Press 'q' to quit, 's' to save image")
    
    # Initialize camera
    camera = cv2.VideoCapture(0)
    if not camera.isOpened():
        print("❌ Could not open camera for interactive test")
        return False
    
    # Initialize hand detector
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
    print("🖐️ Show your hand to the camera...")
    
    frame_count = 0
    start_time = time.time()
    
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
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Show frame
        cv2.imshow("Camera Test - Hand Tracking", frame)
        
        # Handle key presses
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            print("👋 Quitting interactive test...")
            break
        elif key == ord('s'):
            filename = f"hand_test_{int(time.time())}.jpg"
            cv2.imwrite(filename, frame)
            print(f"💾 Saved image as {filename}")
    
    # Cleanup
    camera.release()
    cv2.destroyAllWindows()
    return True

def main():
    """Main function"""
    print("🤟 Sign Language Learning - Camera Test")
    print("=" * 50)
    
    # Test 1: Basic camera access
    if not test_camera():
        print("\n❌ Camera test failed. Please check:")
        print("   - Camera is connected and working")
        print("   - No other application is using the camera")
        print("   - Camera drivers are installed")
        return
    
    # Test 2: Hand tracking
    if not test_hand_tracking():
        print("\n❌ Hand tracking test failed. Please check:")
        print("   - MediaPipe is properly installed")
        print("   - OpenCV version is compatible")
        return
    
    print("\n✅ All tests passed!")
    
    # Ask user if they want interactive test
    try:
        response = input("\n🎮 Do you want to run interactive camera test? (y/n): ").lower()
        if response == 'y':
            interactive_camera_test()
        else:
            print("👋 Camera test completed successfully!")
    except KeyboardInterrupt:
        print("\n👋 Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()
