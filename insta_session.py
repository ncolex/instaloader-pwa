#!/usr/bin/env python3
import instaloader
import sys
import os

def create_instagram_session(username, password):
    """
    Create an Instagram session file that can be reused for downloads
    """
    L = instaloader.Instaloader()
    
    try:
        # Login to Instagram
        L.login(username, password)
        
        # Save session to file
        session_filename = f"session-{username}"
        L.save_session_to_file(session_filename)
        
        print(f"Session saved to {session_filename}")
        print("You can now use this session file for downloading Instagram content.")
        return True
    except Exception as e:
        print(f"Error logging in: {e}")
        return False

def download_with_session(target_username, session_file):
    """
    Download Instagram content using a saved session file
    """
    L = instaloader.Instaloader()
    
    try:
        # Load the session
        L.load_session_from_file(target_username, session_file)
        
        # Create download directory
        os.makedirs(f'./downloads/{target_username}', exist_ok=True)
        L.dirname_pattern = f'./downloads/{target_username}'
        L.save_metadata = False
        L.post_metadata_txt_pattern = ''
        
        # Download the profile
        L.download_profile(target_username, profile_pic=True, profile_pic_only=False)
        print(f"Download of {target_username} completed successfully!")
        return True
    except Exception as e:
        print(f"Error downloading: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  To create session: python3 insta_session.py <instagram_username> <instagram_password>")
        print("  To download using session: python3 insta_session.py <target_username> <session_file>")
        sys.exit(1)
    
    arg1 = sys.argv[1]
    arg2 = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not arg2:
        print("Please provide both Instagram username and password or target username and session file")
        sys.exit(1)
    
    # If first argument is likely a session file (not an Instagram username pattern)
    if os.path.isfile(arg1):
        # Download using session file
        session_file = arg1
        target_username = arg2
        download_with_session(target_username, session_file)
    else:
        # Create session
        username = arg1
        password = arg2
        create_instagram_session(username, password)