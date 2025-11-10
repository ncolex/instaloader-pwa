#!/usr/bin/env python3
"""
Instagram login script for InstaLoader
"""

import instaloader
import getpass

def main():
    print("InstaLoader Login Script")
    print("========================")
    
    # Get Instagram credentials
    username = input("Enter Instagram username: ")
    password = getpass.getpass("Enter Instagram password: ")
    
    # Create an Instaloader instance
    loader = instaloader.Instaloader()
    
    try:
        print("Logging in to Instagram...")
        loader.login(username, password)
        print("Login successful! Session saved.")
    except Exception as e:
        print(f"Login failed: {e}")
        return

if __name__ == "__main__":
    main()