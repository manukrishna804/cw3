# Sign Language Learning Platform

A comprehensive web application for learning sign language using Python Flask, OpenCV, and AI-powered exercise generation. The platform features real-time hand tracking, progress tracking with Firebase, and dynamic exercise generation using Google's Gemini AI.

## Features

### 🎯 Core Features
- **Real-time Hand Tracking**: Uses OpenCV and MediaPipe for accurate hand gesture recognition
- **AI-Powered Exercises**: Dynamic exercise generation using Google Gemini AI based on user progress
- **Progress Tracking**: Firebase backend for storing and tracking user learning progress
- **Beautiful UI**: Modern, responsive design with intuitive user experience

### 📚 Learning Modules
- **Alphabets (A-Z)**: Learn to sign all 26 letters of the alphabet
- **Numbers (0-9)**: Master number signs from 0 to 9
- **Basic Mannerisms**: Essential signs like HELLO, THANK YOU, PLEASE, etc.
- **Word Building**: AI-generated word spelling exercises

### 🎮 Exercise Types
1. **Beginner Level**: Sequential learning of alphabets, numbers, and basic mannerisms
2. **Intermediate Level**: Word building exercises with AI-generated words
3. **Progress-Based**: Exercises adapt to user's skill level and learning pace

## Technology Stack

### Backend
- **Python Flask**: Web framework for API and server-side logic
- **OpenCV**: Computer vision for hand tracking and gesture recognition
- **MediaPipe**: Hand landmark detection and tracking
- **Firebase**: Cloud database for user progress and data storage
- **Google Gemini AI**: AI-powered exercise generation

### Frontend
- **HTML5/CSS3**: Modern, responsive design
- **JavaScript**: Interactive UI and real-time updates
- **Chart.js**: Progress visualization and analytics
- **Font Awesome**: Beautiful icons and UI elements

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- Webcam for hand tracking
- Google Gemini AI API key
- Firebase project and credentials

### Step 1: Clone the Repository
```bash
git clone <repository-url>
cd sign-language-learning-app
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Environment Configuration
1. Copy the environment example file:
```bash
cp env_example.txt .env
```

2. Edit `.env` file with your API keys:
```env
SECRET_KEY=your-secure-secret-key
GEMINI_API_KEY=your-gemini-api-key
DEBUG=True
```

### Step 4: Firebase Setup
1. Create a Firebase project at [Firebase Console](https://console.firebase.google.com/)
2. Enable Firestore Database
3. Generate a service account key:
   - Go to Project Settings > Service Accounts
   - Click "Generate new private key"
   - Save the JSON file as `firebase-credentials.json` in the project root

### Step 5: Run the Application
```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Usage Guide

### Getting Started
1. **Home Page**: Overview of features and learning modules
2. **Start Exercise**: Begin your sign language learning journey
3. **Progress Tracking**: Monitor your learning progress and achievements

### Exercise Flow
1. **Camera Setup**: Allow camera access for hand tracking
2. **Exercise Display**: View the current exercise target and instructions
3. **Hand Recognition**: Show the required sign to the camera
4. **Real-time Feedback**: Get instant feedback on your sign accuracy
5. **Progress Update**: Complete exercises to advance your learning

### Learning Progression
- **Level 1**: Master alphabets (A-Z)
- **Level 2**: Learn numbers (0-9)
- **Level 3**: Practice basic mannerisms
- **Level 4**: Word building with AI-generated exercises

## API Endpoints

### Exercise Management
- `POST /api/start-exercise`: Start a new exercise session
- `POST /api/check-sign`: Check recognized sign against current exercise
- `POST /api/stop-exercise`: Stop the current exercise session

### Progress Tracking
- `GET /api/user-progress/<user_id>`: Get user progress data

## Project Structure

```
sign-language-learning-app/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── templates/            # HTML templates
│   ├── index.html        # Home page
│   ├── exercise.html     # Exercise interface
│   └── progress.html     # Progress tracking
├── static/               # Static assets
│   └── js/
│       └── hand_tracking.js  # Hand tracking logic
├── firebase-credentials.json  # Firebase service account
├── .env                  # Environment variables
└── README.md            # Project documentation
```

## Sign Patterns

### Alphabet Signs (A-Z)
- **A**: Thumb only `[1, 0, 0, 0, 0]`
- **B**: Four fingers up `[0, 1, 1, 1, 1]`
- **C**: Thumb, index, middle `[1, 1, 1, 0, 0]`
- **D**: Index finger only `[0, 1, 0, 0, 0]`
- **E**: Closed fist `[0, 0, 0, 0, 0]`
- ... and more

### Number Signs (0-9)
- **0**: Closed fist `[0, 0, 0, 0, 0]`
- **1**: Index finger only `[0, 1, 0, 0, 0]`
- **2**: Index and middle `[0, 1, 1, 0, 0]`
- ... and more

### Basic Mannerisms
- **HELLO**: Thumb and index `[1, 1, 0, 0, 0]`
- **THANK YOU**: Thumb up `[1, 0, 0, 0, 0]`
- **PLEASE**: Three fingers `[1, 1, 1, 0, 0]`
- ... and more

## Customization

### Adding New Signs
1. Update sign patterns in `app.py`
2. Add corresponding finger patterns
3. Update the recognition logic

### Modifying Exercise Generation
1. Edit the `generate_exercise()` method in `SignLanguageApp` class
2. Customize the Gemini AI prompts
3. Add new exercise types as needed

### UI Customization
1. Modify CSS styles in HTML templates
2. Update JavaScript functionality
3. Add new UI components

## Troubleshooting

### Common Issues

**Camera Access Denied**
- Ensure camera permissions are granted
- Check browser security settings
- Try refreshing the page

**Firebase Connection Error**
- Verify `firebase-credentials.json` is in the project root
- Check Firebase project settings
- Ensure Firestore is enabled

**Gemini AI Error**
- Verify API key is correct
- Check API quota and limits
- Ensure internet connection

**Hand Tracking Issues**
- Ensure good lighting conditions
- Keep hands clearly visible to camera
- Check camera resolution and quality

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- OpenCV community for computer vision tools
- Google for Gemini AI and Firebase services
- MediaPipe team for hand tracking technology
- Font Awesome for beautiful icons

## Support

For support and questions:
- Create an issue in the repository
- Check the troubleshooting section
- Review the documentation

---

**Happy Learning! 🎉** 