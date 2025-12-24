#!/usr/bin/env python3
"""
Display Test - Check if OpenCV windows can open
"""

import cv2
import numpy as np

def main():
    print("🖥️ Testing OpenCV Display...")
    print("=" * 30)
    
    # Create a simple test image
    print("🎨 Creating test image...")
    test_image = np.zeros((400, 600, 3), dtype=np.uint8)
    
    # Add some text and shapes
    cv2.putText(test_image, "OpenCV Display Test", (50, 100), 
               cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    cv2.putText(test_image, "If you see this window, display works!", (50, 150), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    cv2.putText(test_image, "Press any key to close", (50, 200), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
    
    # Draw a circle
    cv2.circle(test_image, (300, 300), 50, (255, 0, 0), -1)
    
    print("🖼️ Showing test image...")
    print("📱 A window should open with a test image")
    print("🔑 Press any key to close the window")
    
    # Show the image
    cv2.imshow("🖥️ OpenCV Display Test", test_image)
    
    # Wait for key press
    print("⏳ Waiting for key press...")
    cv2.waitKey(0)
    
    # Close window
    cv2.destroyAllWindows()
    print("✅ Display test completed!")
    print("✅ OpenCV windows are working!")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ Display test failed: {e}")
        print("This might indicate a display/OpenCV issue")


