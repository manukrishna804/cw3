#!/usr/bin/env python3
"""
Debug Camera Test - Find out why camera window closes immediately
"""

import cv2
import time

def main():
    print("🔍 Debug Camera Test")
    print("=" * 40)
    
    # Test 1: Check if we can create a simple window
    print("🖥️ Test 1: Creating simple window...")
    test_image = cv2.imread("test_image.jpg") if cv2.imread("test_image.jpg") is not None else None
    
    if test_image is None:
        # Create a simple test image
        test_image = cv2.imread("sample.jpg") if cv2.imread("sample.jpg") is not None else None
        
        if test_image is None:
            # Create a black image with text
            test_image = cv2.imread("hand_test_*.jpg") if cv2.imread("hand_test_*.jpg") is not None else None
            
            if test_image is None:
                # Create a completely new image
                test_image = cv2.imread("basic_camera_*.jpg") if cv2.imread("basic_camera_*.jpg") is not None else None
                
                if test_image is None:
                    # Create a blank image
                    test_image = np.zeros((480, 640, 3), dtype=np.uint8)
                    cv2.putText(test_image, "Test Image", (200, 240), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    
    print("✅ Test image created/loaded")
    
    # Test 2: Try to show the image
    print("🖼️ Test 2: Showing test image...")
    try:
        cv2.imshow("Test Window", test_image)
        print("✅ cv2.imshow() called successfully")
        
        # Wait a bit to see if window appears
        print("⏳ Waiting 3 seconds to see if window appears...")
        time.sleep(3)
        
        # Check if window is visible
        print("🔍 Checking window status...")
        
    except Exception as e:
        print(f"❌ Error showing image: {e}")
        return
    
    # Test 3: Try to open camera
    print("\n🎥 Test 3: Opening camera...")
    camera = cv2.VideoCapture(0)
    
    if not camera.isOpened():
        print("❌ Could not open camera")
        return
    
    print("✅ Camera opened successfully")
    
    # Test 4: Read a frame
    print("📸 Test 4: Reading camera frame...")
    ret, frame = camera.read()
    if not ret:
        print("❌ Could not read frame")
        camera.release()
        return
    
    print("✅ Frame read successfully")
    print(f"📊 Frame size: {frame.shape}")
    
    # Test 5: Show camera frame
    print("🖼️ Test 5: Showing camera frame...")
    try:
        cv2.imshow("Camera Frame", frame)
        print("✅ Camera frame displayed")
        
        # Wait for user input
        print("⏳ Waiting for key press...")
        print("📱 Press any key to continue...")
        
        # Wait for key press
        key = cv2.waitKey(0)
        print(f"🔑 Key pressed: {key}")
        
    except Exception as e:
        print(f"❌ Error showing camera frame: {e}")
    
    # Test 6: Try continuous camera feed
    print("\n🎥 Test 6: Continuous camera feed...")
    print("📱 Press 'q' to quit, 'c' to continue...")
    
    frame_count = 0
    start_time = time.time()
    
    try:
        while True:
            ret, frame = camera.read()
            if not ret:
                print("❌ Failed to read frame")
                break
            
            # Flip frame
            frame = cv2.flip(frame, 1)
            
            # Add text
            cv2.putText(frame, f"Frame: {frame_count}", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, "Press 'q' to quit", (10, 60), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Show frame
            cv2.imshow("Continuous Camera Feed", frame)
            
            # Handle key press
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                print("👋 Quitting continuous feed...")
                break
            elif key == ord('c'):
                print("🔄 Continuing...")
            
            frame_count += 1
            
            # Limit to 100 frames for testing
            if frame_count > 100:
                print("🔄 Reached 100 frames, stopping...")
                break
            
            # Small delay
            time.sleep(0.01)
            
    except KeyboardInterrupt:
        print("\n👋 Continuous feed interrupted")
    except Exception as e:
        print(f"❌ Error in continuous feed: {e}")
    
    # Cleanup
    camera.release()
    cv2.destroyAllWindows()
    print("✅ Debug camera test completed!")

if __name__ == "__main__":
    try:
        import numpy as np
        main()
    except Exception as e:
        print(f"❌ Main error: {e}")
        print("Please check your OpenCV installation")
