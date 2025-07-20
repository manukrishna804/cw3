# Authentication Setup Guide - Sign Language Learning App

## 🚀 Complete Authentication System

This guide will help you set up the complete authentication system with Firebase Auth and user progress tracking.

## 📋 What's New

### ✅ Authentication Features
- **User Registration**: Create accounts with email/password
- **User Login**: Secure authentication with Firebase Auth
- **Session Management**: Flask sessions for user state
- **Protected Routes**: Login-required decorators
- **User Dashboard**: Personalized learning dashboard
- **Progress Tracking**: User-specific progress in Firebase

### ✅ Improved Gemini Integration
- **Smart Word Generation**: Only uses letters the user has learned
- **Progress-Based Exercises**: Adapts to user's skill level
- **Learning Path**: Sequential progression from alphabets to words

### ✅ Firebase Integration
- **User Authentication**: Firebase Auth for secure login
- **Progress Storage**: Firestore for user learning data
- **Real-time Updates**: Live progress tracking

## 🔧 Setup Instructions

### Step 1: Install Dependencies

```bash
pip install flask firebase-admin google-generativeai python-dotenv
```

### Step 2: Firebase Project Setup

1. **Create Firebase Project**
   - Go to [Firebase Console](https://console.firebase.google.com/)
   - Click "Add project"
   - Name your project (e.g., "sign-language-learning")
   - Follow the setup wizard

2. **Enable Authentication**
   - In Firebase Console, go to "Authentication"
   - Click "Get started"
   - Go to "Sign-in method" tab
   - Enable "Email/Password" provider
   - Save changes

3. **Enable Firestore Database**
   - Go to "Firestore Database"
   - Click "Create database"
   - Choose "Start in test mode" (for development)
   - Select a location close to your users

4. **Generate Service Account Key**
   - Go to Project Settings (gear icon)
   - Click "Service accounts" tab
   - Click "Generate new private key"
   - Download the JSON file
   - Save as `firebase-credentials.json` in your project root

### Step 3: Environment Configuration

1. **Create .env file**
   ```bash
   cp env_example.txt .env
   ```

2. **Edit .env file**
   ```env
   # Flask Secret Key (generate a secure random key)
   SECRET_KEY=your-super-secret-key-change-this-in-production
   
   # Google Gemini AI API Key
   GEMINI_API_KEY=your-gemini-api-key-here
   
   # Debug mode
   DEBUG=True
   ```

3. **Get Gemini API Key**
   - Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create a new API key
   - Copy it to your .env file

### Step 4: Test Setup

Run the authentication test:

```bash
python test_auth.py
```

This will verify:
- ✅ Dependencies are installed
- ✅ Firebase credentials are valid
- ✅ App structure is correct
- ✅ All routes and templates exist

### Step 5: Run the Application

```bash
python app.py
```

Visit `http://localhost:5000` to see the app!

## 🎯 User Flow

### 1. **Registration**
- User visits `/register`
- Enters name, email, and password
- Account created in Firebase Auth
- User progress initialized in Firestore
- Redirected to dashboard

### 2. **Login**
- User visits `/login`
- Enters email and password
- Authenticated with Firebase Auth
- Session created with user info
- Redirected to dashboard

### 3. **Dashboard**
- Shows user stats and progress
- Quick access to exercises
- Recent activity feed
- Navigation to all features

### 4. **Learning**
- Start exercises from dashboard
- Real-time hand tracking
- AI-generated exercises based on progress
- Progress automatically saved to Firebase

## 🔐 Security Features

### Authentication
- **Firebase Auth**: Industry-standard authentication
- **Password Validation**: Minimum 6 characters
- **Email Validation**: Proper email format checking
- **Session Management**: Secure Flask sessions

### Authorization
- **Protected Routes**: Login required for sensitive pages
- **User Isolation**: Users can only access their own data
- **CSRF Protection**: Built into Flask

### Data Security
- **Firebase Security Rules**: Configure in Firebase Console
- **Environment Variables**: Sensitive data in .env file
- **HTTPS**: Use in production

## 📊 Database Structure

### Firestore Collections

```
users/
  {user_id}/
    level: "beginner" | "intermediate" | "advanced"
    completed_exercises: [
      {
        type: "alphabet" | "number" | "mannerism" | "word_building"
        target: "A" | "1" | "HELLO" | "CAT"
        completed_at: "2024-01-01T12:00:00Z"
      }
    ]
    total_score: 150
    created_at: "2024-01-01T12:00:00Z"
    last_updated: "2024-01-01T12:00:00Z"
```

## 🎮 Exercise Flow

### Beginner Level (0-2 exercises)
1. **Alphabet A**: Learn letter A
2. **Number 1**: Learn number 1
3. **Mannerism HELLO**: Learn basic greeting

### Intermediate Level (3+ exercises)
1. **Smart Word Generation**: AI creates words using only learned letters
2. **Progress Tracking**: Each exercise updates user progress
3. **Level Progression**: Automatic level advancement

## 🔧 Firebase Security Rules

Add these rules in Firebase Console > Firestore > Rules:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Users can only read/write their own data
    match /users/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
  }
}
```

## 🚨 Troubleshooting

### Common Issues

**Firebase Connection Error**
- Verify `firebase-credentials.json` is in project root
- Check Firebase project settings
- Ensure Firestore is enabled

**Authentication Error**
- Verify Firebase Auth is enabled
- Check email/password provider is active
- Ensure proper Firebase credentials

**Gemini API Error**
- Verify API key is correct in .env file
- Check API quota and limits
- Ensure internet connection

**Session Issues**
- Verify SECRET_KEY is set in .env
- Check browser cookies are enabled
- Clear browser cache if needed

### Debug Mode

Enable debug mode in .env:
```env
DEBUG=True
```

This will show detailed error messages and auto-reload on changes.

## 🎉 Ready to Use!

Your authentication system is now complete with:

- ✅ User registration and login
- ✅ Secure session management
- ✅ Firebase integration
- ✅ Smart AI exercise generation
- ✅ User-specific progress tracking
- ✅ Beautiful UI with modern design

Start learning sign language with your personalized experience!

## 📞 Support

If you encounter issues:

1. Run `python test_auth.py` to diagnose problems
2. Check the troubleshooting section above
3. Verify all setup steps are completed
4. Ensure Firebase project is properly configured

Happy Learning! 🤟 