# Sign Language Learning Platform (Revamped)

A comprehensive web application for learning sign language using Python Flask, OpenCV, and AI.

**Recently Updated**: This project has been refactored to support **Offline Mode** (SQLite) and **Online Mode** (Firebase) automatically.

## 🚀 How to Run

### Windows (Easiest)
Double-click `run_app.bat`.

### Command Line
```bash
python run.py
```
Open your browser at `http://localhost:5000`

## ✨ New Features

-   **Hybrid Database**: Automatically uses **SQLite** if Firebase credentials are missing. No setup required!
-   **Robust Camera**: Improved camera handling that won't crash your app.
-   **Modular Code**: Cleaned up into `camera_handler.py`, `db_handler.py`, and `app.py`.

## 🛠️ Setup Guide

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configuration (Optional)
-   **Offline Mode**: Works out of the box!
-   **Online Mode**:
    -   Add `firebase-credentials.json` to the root folder.
    -   Update `.env` with your `GEMINI_API_KEY` for AI features.

## 📂 Project Structure

-   `app.py`: Main Web Application
-   `camera_handler.py`: Computer Vision Logic (OpenCV/MediaPipe)
-   `db_handler.py`: Database Logic (SQLite/Firebase)
-   `run.py`: Startup Script
-   `templates/`: HTML Frontend

## 🎮 How to Play
1.  Register an account (Local or Cloud).
2.  Go to **Start Exercise**.
3.  Allow Camera access.
4.  Follow the instructions on screen (e.g., "Show Letter A").
5.  The AI will detect your hand and give feedback!
