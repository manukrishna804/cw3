# Quick Setup Guide - Sign Language Learning App

## 🚀 Quick Start (5 minutes)

### Option 1: Demo Mode (No Setup Required)
```bash
python demo.py
```
This runs a fully functional demo without any external dependencies.

### Option 2: Full Web App Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the App**
   ```bash
   python run.py
   ```

3. **Open Browser**
   Navigate to `http://localhost:5000`

## 📋 What You Get

### 🎯 Core Features
- **Real-time Hand Tracking**: OpenCV + MediaPipe for gesture recognition
- **AI-Powered Exercises**: Google Gemini AI generates dynamic exercises
- **Progress Tracking**: Firebase backend stores learning progress
- **Beautiful UI**: Modern, responsive web interface

### 📚 Learning Modules
- **Alphabets (A-Z)**: Learn all 26 letters
- **Numbers (0-9)**: Master number signs
- **Basic Mannerisms**: HELLO, THANK YOU, PLEASE, etc.
- **Word Building**: AI-generated word spelling exercises

### 🎮 Exercise Flow
1. **Camera Setup**: Allow webcam access
2. **Exercise Display**: View target and instructions
3. **Hand Recognition**: Show signs to camera
4. **Real-time Feedback**: Get instant accuracy feedback
5. **Progress Update**: Complete exercises to advance

## 🔧 Configuration (Optional)

### For Full Functionality

1. **Google Gemini AI** (for dynamic exercises)
   - Get API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Add to `.env` file: `GEMINI_API_KEY=your-key-here`

2. **Firebase** (for progress tracking)
   - Create project at [Firebase Console](https://console.firebase.google.com/)
   - Enable Firestore Database
   - Download service account key as `firebase-credentials.json`

3. **Environment Variables**
   ```bash
   cp env_example.txt .env
   # Edit .env with your API keys
   ```

## 🎮 Demo Commands

When running `python demo.py`:

- `start` - Start a new exercise
- `sign A` - Simulate showing letter A
- `sign 1` - Simulate showing number 1
- `sign HELLO` - Simulate showing HELLO
- `progress` - Show learning progress
- `help` - Show available commands
- `quit` - Exit demo

## 📁 Project Structure

```
sign-language-learning-app/
├── app.py                 # Main Flask application
├── demo.py               # Interactive demo (no dependencies)
├── run.py                # Startup script
├── test_setup.py         # Setup verification
├── requirements.txt      # Python dependencies
├── templates/            # HTML templates
│   ├── index.html        # Home page
│   ├── exercise.html     # Exercise interface
│   └── progress.html     # Progress tracking
├── static/js/
│   └── hand_tracking.js  # Hand tracking logic
├── env_example.txt       # Environment template
├── README.md            # Full documentation
└── SETUP_GUIDE.md       # This file
```

## 🎯 Sign Patterns

### Quick Reference
- **A**: Thumb only `[1, 0, 0, 0, 0]`
- **1**: Index finger only `[0, 1, 0, 0, 0]`
- **L**: Thumb and index `[1, 1, 0, 0, 0]`
- **U**: Index and middle `[0, 1, 1, 0, 0]`
- **O**: All fingers `[1, 1, 1, 1, 1]`
- **HELLO**: Thumb and index `[1, 1, 0, 0, 0]`

## 🚨 Troubleshooting

### Common Issues

**Demo not working**
- Ensure Python 3.6+ is installed
- Run: `python --version`

**Web app not starting**
- Install dependencies: `pip install -r requirements.txt`
- Check port 5000 is available

**Camera issues**
- Ensure webcam permissions are granted
- Try refreshing the page
- Check browser security settings

**API errors**
- Verify API keys in `.env` file
- Check internet connection
- Ensure API quotas are not exceeded

## 🎉 Ready to Learn!

1. **Start with Demo**: `python demo.py`
2. **Try Web App**: `python run.py`
3. **Customize**: Edit sign patterns in `app.py`
4. **Extend**: Add new exercise types

---

**Happy Learning! 🤟** 