#!/usr/bin/env python3
"""
Basic Camera Test - Just camera, no hand tracking
"""

import cv2
import time

def main():
    print("🎥 Basic Camera Test - No Hand Tracking")
    print("=" * 40)
    
    # Try to open camera
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
            print("❌ No camera found at any index!")
            print("\n🔧 Troubleshooting:")
            print("1. Check if camera is connected")
            print("2. Close other apps using camera (Zoom, Teams, etc.)")
            print("3. Check Windows Camera app works")
            print("4. Restart computer")
            return
    
    # Get camera properties
    width = int(camera.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = camera.get(cv2.CAP_PROP_FPS)
    
    print(f"📊 Camera Properties:")
    print(f"   Resolution: {width}x{height}")
    print(f"   FPS: {fps}")
    
    # Test reading a frame
    ret, frame = camera.read()
    if not ret:
        print("❌ Failed to read frame from camera")
        camera.release()
        return
    
    print("✅ Successfully read frame from camera")
    print("🚀 Starting live camera feed...")
    print("📱 Press 'q' to quit, 's' to save image")
    print("=" * 40)
    
    frame_count = 0
    start_time = time.time()
    
    while True:
        ret, frame = camera.read()
        if not ret:
            print("❌ Failed to read frame")
            break
        
        # Flip frame horizontally for mirror effect
        frame = cv2.flip(frame, 1)
        
        # Display frame info
        cv2.putText(frame, f"Frame: {frame_count}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Calculate FPS
        frame_count += 1
        elapsed_time = time.time() - start_time
        if elapsed_time > 0:
            current_fps = frame_count / elapsed_time
            cv2.putText(frame, f"FPS: {current_fps:.1f}", (10, 60), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Display instructions
        cv2.putText(frame, "Press 'q' to quit, 's' to save", (10, frame.shape[0] - 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Show frame
        cv2.imshow("🎥 Basic Camera Test", frame)
        
        # Handle key presses
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            print("👋 Quitting basic camera test...")
            break
        elif key == ord('s'):
            filename = f"basic_camera_{int(time.time())}.jpg"
            cv2.imwrite(filename, frame)
            print(f"💾 Saved image as {filename}")
    
    # Cleanup
    camera.release()
    cv2.destroyAllWindows()
    print("✅ Basic camera test completed!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Camera test interrupted!")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Please check if camera is working in other applications")
