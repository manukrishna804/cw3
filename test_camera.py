#!/usr/bin/env python3
"""
Simple test to verify camera and OpenCV hand tracking
"""

import cv2
from cvzone.HandTrackingModule import HandDetector
import time

def test_camera():
    """Test basic camera functionality"""
    print("📹 Testing Camera Access...")
    
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Failed to open camera")
        return False
    
    print("✅ Camera opened successfully")
    
    # Test a few frames
    for i in range(5):
        ret, frame = cap.read()
        if ret:
            print(f"   ✅ Frame {i+1}: {frame.shape}")
        else:
            print(f"   ❌ Frame {i+1}: Failed to read")
            cap.release()
            return False
    
    cap.release()
    print("✅ Camera test passed!")
    return True

def test_hand_detection():
    """Test hand detection with camera"""
    print("\n🤚 Testing Hand Detection...")
    
    cap = cv2.VideoCapture(0)
    detector = HandDetector(maxHands=1)
    
    if not cap.isOpened():
        print("❌ Failed to open camera for hand detection")
        return False
    
    print("✅ Starting hand detection test...")
    print("   Show your hand to the camera for 5 seconds...")
    
    start_time = time.time()
    hand_detected = False
    
    while time.time() - start_time < 5:
        ret, frame = cap.read()
        if not ret:
            continue
        
        hands, frame = detector.findHands(frame)
        
        if hands:
            hand = hands[0]
            fingers = detector.fingersUp(hand)
            print(f"   ✅ Hand detected! Fingers: {fingers}")
            hand_detected = True
            break
        
        # Show frame
        cv2.imshow("Hand Detection Test", frame)
        if cv2.waitKey(1) & 0xFF == 27:  # ESC to exit
            break
    
    cap.release()
    cv2.destroyAllWindows()
    
    if hand_detected:
        print("✅ Hand detection test passed!")
        return True
    else:
        print("❌ No hand detected in 5 seconds")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Camera and Hand Detection...\n")
    
    # Test 1: Basic camera
    camera_ok = test_camera()
    
    # Test 2: Hand detection
    hand_ok = test_hand_detection()
    
    # Summary
    print("\n" + "="*50)
    print("📊 CAMERA TEST SUMMARY")
    print("="*50)
    print(f"Camera Access: {'✅ PASS' if camera_ok else '❌ FAIL'}")
    print(f"Hand Detection: {'✅ PASS' if hand_ok else '❌ FAIL'}")
    
    if camera_ok and hand_ok:
        print("\n🎉 All camera tests passed!")
        print("🚀 OpenCV hand tracking should work in the web app!")
    else:
        print("\n⚠️ Some tests failed.")
        print("\n💡 Troubleshooting:")
        print("   1. Check if camera is connected and working")
        print("   2. Make sure no other app is using the camera")
        print("   3. Try running: python -c 'import cv2; print(cv2.__version__)'")
        print("   4. Check if cvzone is installed: pip install cvzone")

if __name__ == "__main__":
    main() 