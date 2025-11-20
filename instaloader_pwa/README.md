# InstaLoader Web Application

A simple web interface for downloading Instagram profiles using instaloader.

## Features

- Create Instagram sessions securely
- Download public and private Instagram profiles
- Track download progress in real-time
- Automatic cleanup of session files for security

## Requirements

- Python 3.7+
- Instagram account (to create session)

## Installation

1. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

2. Run the application:
   ```
   python app.py
   ```

3. Open your browser and go to `http://localhost:5000`

## Usage

1. **Create Session:** 
   - Enter your Instagram username and password
   - Click "Create Session"
   - You'll receive a session file name (e.g., session_xxxxxx.session)

2. **Download Profile:**
   - Enter the target Instagram username you want to download
   - Enter the session file name from step 1
   - Enter the Instagram username associated with the session
   - Click "Download Profile"

## Security Notes

- Session files are automatically deleted after 1 hour
- Passwords are not stored, only used to create session cookies
- Session filenames are hashed for privacy
- Input validation is implemented to prevent directory traversal attacks

## Important Note about Instagram Login

Instagram has updated their authentication process, and direct login through this application may not work. As an alternative, you can:

1. Create a session file manually using instaloader from the command line:
   ```
   # First, login using instaloader directly
   instaloader --login=your_username
   # This will prompt for your password and save a session
   ```

2. Find the session file (usually in ~/.config/instaloader/session-your_username)

3. Copy this session file to the application directory and use its name in the form

4. Then you can use the download functionality with the saved session

## Limitations

- Instagram may limit download requests
- Private profiles require you to be following them
- Large profiles may take a long time to download