# AI-Based Iris Recognition Authentication System

A lightweight, prototype iris recognition system built with Python, OpenCV, and Tkinter. This application detects a user's eyes using OpenCV Haar Cascades, extracts ORB features from the eye region, and matches them to authenticate the user.

## Features
- **Registration**: Captures the user's iris features and saves them in a local SQLite database (`iris_auth.db`).
- **Authentication**: Compares live camera iris features against stored database features using ORB descriptor matching (Hamming distance).
- **Management**: Allows viewing of login attempt logs and deleting users.

## Folder Structure
```text
project_iris/
│
├── database.py         # SQLite database initialization and operations
├── iris_processing.py  # OpenCV Haar Cascades logic for eye detection and feature extraction
├── main.py             # Entry point of the application
├── matcher.py          # ORB feature matching logic using BFMatcher
├── requirements.txt    # Project dependencies
└── ui.py               # Tkinter GUI implementation
```

## Requirements
- Python 3.7+
- A working webcam

## Installation

1. Open a terminal or command prompt.
2. Navigate to the `project_iris` directory.
3. Install the required dependencies:
   ```cmd
   pip install -r requirements.txt
   ```

## Usage

1. Run the application:
   ```cmd
   python main.py
   ```
2. **To Register**: 
   - Look at the camera so that green bounding boxes appear around your eyes.
   - Enter a username in the "Username" field.
   - Click "Register".
3. **To Login**:
   - Look at the camera.
   - Click "Login". The system will compute the match score and grant or deny access based on the highest matching score across all registered users.
4. **Logs & Management**:
   - Click "View Logs" to see a history of authentication attempts.
   - Enter a username in the Registration field and click "Delete User" to remove someone from the database.

## Technical Details
- **OpenCV Haar Cascades** are used to detect faces and extract the eye regions efficiently.
- The eye region is cropped, grayscaled, blurred (for noise reduction), and histogram equalized.
- **ORB (Oriented FAST and Rotated BRIEF)** is used to extract keypoints and descriptors.
- Descriptors are matched using OpenCV's `BFMatcher`. A combined score (sum of good matches from both eyes) determines access.
