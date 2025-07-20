// Hand tracking and sign recognition functionality
class HandTracker {
    constructor() {
        this.video = null;
        this.canvas = null;
        this.ctx = null;
        this.isTracking = false;
        this.onSignDetected = null;
        this.lastFingers = [0, 0, 0, 0, 0];
        this.stableCount = 0;
        this.lastRecognized = '';
        this.lastCaptureTime = 0;
        this.requiredStability = 10;
        this.cooldownTime = 1.5;
    }

    async initialize(videoElement, canvasElement) {
        this.video = videoElement;
        this.canvas = canvasElement;
        this.ctx = this.canvas.getContext('2d');

        try {
            const stream = await navigator.mediaDevices.getUserMedia({
                video: {
                    width: 640,
                    height: 480,
                    facingMode: 'user'
                }
            });
            
            this.video.srcObject = stream;
            await this.video.play();
            
            console.log('✅ Camera initialized successfully');
            return true;
        } catch (error) {
            console.error('❌ Error accessing camera:', error);
            return false;
        }
    }

    startTracking(callback) {
        this.onSignDetected = callback;
        this.isTracking = true;
        this.trackHands();
    }

    stopTracking() {
        this.isTracking = false;
    }

    async trackHands() {
        if (!this.isTracking) return;

        // In a real implementation, this would use OpenCV.js or MediaPipe
        // For now, we'll simulate hand tracking
        this.simulateHandTracking();
        
        requestAnimationFrame(() => this.trackHands());
    }

    simulateHandTracking() {
        // Simulate finger detection
        const fingers = this.simulateFingerDetection();
        
        // Update finger pattern display
        this.updateFingerDisplay(fingers);
        
        // Check for stable recognition
        this.checkStableRecognition(fingers);
        
        // Send data to backend for processing
        this.sendToBackend(fingers);
    }

    simulateFingerDetection() {
        // Simulate different finger patterns based on time
        const time = Date.now() / 1000;
        const pattern = Math.floor(time) % 5;
        
        const patterns = [
            [1, 0, 0, 0, 0], // Thumb only (A)
            [0, 1, 0, 0, 0], // Index only (1)
            [1, 1, 0, 0, 0], // Thumb and index (L)
            [0, 1, 1, 0, 0], // Index and middle (U)
            [1, 1, 1, 1, 1]  // All fingers (O)
        ];
        
        return patterns[pattern];
    }

    updateFingerDisplay(fingers) {
        // Update the finger pattern display
        const fingerPatternElement = document.getElementById('fingerPattern');
        if (fingerPatternElement) {
            fingerPatternElement.textContent = JSON.stringify(fingers);
        }
    }

    checkStableRecognition(fingers) {
        const currentTime = Date.now() / 1000;
        
        // Check if fingers are stable
        if (JSON.stringify(fingers) === JSON.stringify(this.lastFingers)) {
            this.stableCount++;
            
            if (this.stableCount >= this.requiredStability && 
                (currentTime - this.lastCaptureTime) > this.cooldownTime) {
                
                // Recognize the sign
                const recognized = this.recognizeSign(fingers);
                
                if (recognized && recognized !== this.lastRecognized) {
                    this.lastRecognized = recognized;
                    this.lastCaptureTime = currentTime;
                    
                    if (this.onSignDetected) {
                        this.onSignDetected(recognized, fingers);
                    }
                }
                
                this.stableCount = 0;
            }
        } else {
            this.stableCount = 0;
            this.lastRecognized = '';
        }
        
        this.lastFingers = [...fingers];
    }

    recognizeSign(fingers) {
        // Sign patterns for recognition
        const signPatterns = {
            "A": [1, 0, 0, 0, 0],
            "B": [0, 1, 1, 1, 1],
            "C": [1, 1, 1, 0, 0],
            "D": [0, 1, 0, 0, 0],
            "E": [0, 0, 0, 0, 0],
            "F": [1, 0, 1, 1, 1],
            "G": [1, 1, 0, 0, 0],
            "H": [0, 1, 1, 0, 0],
            "I": [0, 0, 0, 0, 1],
            "J": [0, 0, 0, 1, 0],
            "K": [0, 1, 1, 1, 0],
            "L": [1, 1, 0, 0, 0],
            "M": [1, 0, 1, 0, 1],
            "N": [1, 0, 0, 1, 0],
            "O": [1, 1, 1, 1, 1],
            "P": [1, 1, 1, 0, 1],
            "Q": [1, 0, 1, 1, 0],
            "R": [0, 1, 1, 0, 1],
            "S": [0, 0, 0, 0, 0],
            "T": [1, 0, 0, 0, 1],
            "U": [0, 1, 1, 0, 0],
            "V": [0, 1, 1, 0, 0],
            "W": [0, 1, 1, 1, 0],
            "X": [0, 1, 0, 1, 0],
            "Y": [1, 0, 0, 0, 1],
            "Z": [0, 0, 1, 0, 0]
        };

        const numberPatterns = {
            "0": [0, 0, 0, 0, 0],
            "1": [0, 1, 0, 0, 0],
            "2": [0, 1, 1, 0, 0],
            "3": [0, 1, 1, 1, 0],
            "4": [0, 1, 1, 1, 1],
            "5": [1, 1, 1, 1, 1],
            "6": [1, 0, 0, 0, 0],
            "7": [1, 1, 0, 0, 0],
            "8": [1, 1, 1, 0, 0],
            "9": [1, 0, 1, 1, 1]
        };

        const mannerismPatterns = {
            "HELLO": [1, 1, 0, 0, 0],
            "THANK YOU": [1, 0, 0, 0, 0],
            "PLEASE": [1, 1, 1, 0, 0],
            "GOOD": [1, 1, 0, 0, 0],
            "BAD": [0, 0, 0, 0, 0],
            "YES": [1, 1, 1, 1, 1],
            "NO": [0, 0, 0, 0, 0],
            "SORRY": [1, 0, 0, 0, 1]
        };

        // Check alphabet patterns
        for (const [letter, pattern] of Object.entries(signPatterns)) {
            if (JSON.stringify(fingers) === JSON.stringify(pattern)) {
                return letter;
            }
        }

        // Check number patterns
        for (const [number, pattern] of Object.entries(numberPatterns)) {
            if (JSON.stringify(fingers) === JSON.stringify(pattern)) {
                return number;
            }
        }

        // Check mannerism patterns
        for (const [mannerism, pattern] of Object.entries(mannerismPatterns)) {
            if (JSON.stringify(fingers) === JSON.stringify(pattern)) {
                return mannerism;
            }
        }

        return null;
    }

    drawHandLandmarks(landmarks) {
        if (!this.ctx || !this.canvas) return;

        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        this.ctx.drawImage(this.video, 0, 0, this.canvas.width, this.canvas.height);

        // Draw hand landmarks
        this.ctx.strokeStyle = '#00FF00';
        this.ctx.lineWidth = 2;
        this.ctx.fillStyle = '#FF0000';

        landmarks.forEach(landmark => {
            this.ctx.beginPath();
            this.ctx.arc(landmark.x * this.canvas.width, landmark.y * this.canvas.height, 5, 0, 2 * Math.PI);
            this.ctx.fill();
        });
    }
    
    async sendToBackend(fingers) {
        try {
            const response = await fetch('/api/hand-tracking', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    fingers: fingers,
                    timestamp: Date.now()
                })
            });
            
            if (response.ok) {
                const data = await response.json();
                if (data.success) {
                    // Update UI with backend data
                    this.updateBackendData(data);
                }
            }
        } catch (error) {
            console.error('❌ Error sending data to backend:', error);
        }
    }
    
    updateBackendData(data) {
        // Update UI elements with backend recognition data
        const recognizedElement = document.getElementById('recognizedSign');
        if (recognizedElement && data.recognized_sign) {
            recognizedElement.textContent = data.recognized_sign;
        }
        
        const stableElement = document.getElementById('stableStatus');
        if (stableElement) {
            stableElement.textContent = data.stable ? 'Stable' : 'Unstable';
            stableElement.className = data.stable ? 'stable' : 'unstable';
        }
        
        const currentWordElement = document.getElementById('currentWord');
        if (currentWordElement && data.current_word) {
            currentWordElement.textContent = data.current_word;
        }
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = HandTracker;
} 