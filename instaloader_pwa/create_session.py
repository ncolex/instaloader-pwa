#!/usr/bin/env python3
import instaloader

# Create an instance of Instaloader
L = instaloader.Instaloader()

try:
    # Attempt to login using the email as identifier
    # Note: If this is indeed an email/phone login, Instagram may require special handling
    L.login('marisol33arg@gmail.com', 'Gradiva2016')  # Please note: This is just an example, do not store credentials in code
    print("Login successful!")
    
    # Save session to file
    L.save_session_to_file("session-marisol33arg")
    print("Session saved successfully!")
    
except instaloader.exceptions.TwoFactorAuthRequiredException:
    print("Two-factor authentication is required.")
except instaloader.exceptions.BadCredentialsException:
    print("Invalid credentials provided.")
except Exception as e:
    print(f"An error occurred: {e}")
    print("Instagram may have updated their authentication process, requiring an alternative method.")