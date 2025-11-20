from flask import Flask, render_template, request, redirect, url_for, flash, send_file, jsonify
import instaloader
import os
import tempfile
from threading import Thread
import time
import hashlib
import secrets
from functools import wraps
import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

app = Flask(__name__)
# Generate a secure random secret key
app.secret_key = secrets.token_hex(16)

# Store active downloads
active_downloads = {}

# Configuration for email sending (these would come from environment variables in a real app)
EMAIL_CONFIG = {
    'server': 'smtp.gmail.com',
    'port': 587,
    # In a real application, these would be set via environment variables
    'username': os.environ.get('EMAIL_USERNAME', ''),
    'password': os.environ.get('EMAIL_PASSWORD', '')
}

def validate_instagram_username(username):
    """Validate Instagram username format"""
    if not username:
        return False
    # Instagram usernames can only contain letters, numbers, periods, and underscores
    pattern = r'^[A-Za-z0-9._]{1,30}$'
    return bool(re.match(pattern, username))

def validate_instagram_login_identifier(identifier):
    """Validate Instagram login identifier which can be username, email or phone number"""
    if not identifier:
        return False

    # Check if it's an email address
    if '@' in identifier:
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(email_pattern, identifier))

    # Check if it's a phone number (can start with + or just digits)
    if identifier.startswith('+') or identifier.isdigit():
        # Phone numbers are typically 10-15 digits
        phone_pattern = r'^\+?[0-9]{10,15}$'
        return bool(re.match(phone_pattern, identifier))

    # Check if it's a username (can contain letters, numbers, periods, and underscores)
    username_pattern = r'^[A-Za-z0-9._]{1,30}$'
    return bool(re.match(username_pattern, identifier))

def secure_session_filename(username):
    """Generate a secure session filename using hashing"""
    # Hash the username to avoid exposing it directly in filesystem
    hashed = hashlib.sha256(username.encode()).hexdigest()[:12]
    return f"session_{hashed}.session"

def cleanup_session_files():
    """Clean up session files after a certain period"""
    session_dir = "./"
    for file in os.listdir(session_dir):
        if file.startswith("session_") and file.endswith(".session"):
            file_path = os.path.join(session_dir, file)
            # Remove session files older than 1 hour
            if time.time() - os.path.getmtime(file_path) > 3600:
                os.remove(file_path)

def create_instagram_session(login_identifier, password):
    """
    Create an Instagram session file that can be reused for downloads
    """
    # Validate inputs
    if not validate_instagram_login_identifier(login_identifier):
        return False, "Invalid Instagram login identifier format"

    L = instaloader.Instaloader()

    try:
        # Login to Instagram
        L.login(login_identifier, password)

        # Save session to file with secure name
        session_filename = secure_session_filename(login_identifier)
        L.save_session_to_file(session_filename)

        # Return the full path of the session file
        session_path = os.path.abspath(session_filename)
        return True, session_path
    except instaloader.exceptions.BadCredentialsException:
        return False, "Invalid login identifier or password"
    except instaloader.exceptions.TooManyRequestsException:
        return False, "Too many requests - please try again later"
    except instaloader.exceptions.ConnectionException as e:
        return False, f"Connection error: {str(e)}"
    except Exception as e:
        error_msg = str(e)
        if "window._sharedData" in error_msg:
            return False, "Instagram login failed - Instagram may have updated their login process. Consider using a saved session or updating instaloader."
        return False, f"An error occurred: {error_msg}"

def send_email_with_attachments(to_email, subject, body, attachment_paths):
    """
    Send an email with attachments
    """
    if not EMAIL_CONFIG['username'] or not EMAIL_CONFIG['password']:
        return False, "Email credentials not configured"

    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = EMAIL_CONFIG['username']
        msg['To'] = to_email
        msg['Subject'] = subject

        # Add body to email
        msg.attach(MIMEText(body, 'plain'))

        # Add attachments
        for file_path in attachment_paths:
            if os.path.exists(file_path):
                with open(file_path, "rb") as attachment:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment.read())

                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename= {os.path.basename(file_path)}'
                )

                msg.attach(part)

        # Create SMTP session
        server = smtplib.SMTP(EMAIL_CONFIG['server'], EMAIL_CONFIG['port'])
        server.starttls()  # Enable security
        server.login(EMAIL_CONFIG['username'], EMAIL_CONFIG['password'])

        # Send email
        text = msg.as_string()
        server.sendmail(EMAIL_CONFIG['username'], to_email, text)
        server.quit()

        return True, "Email sent successfully"
    except Exception as e:
        return False, f"Failed to send email: {str(e)}"

def download_profile_with_session(target_username, session_file, login_username, send_email=False, email_address=None):
    """
    Download Instagram content using a saved session file
    """
    # Validate target username (this should still be a valid Instagram username)
    if not validate_instagram_username(target_username):
        active_downloads[target_username] = f"Invalid target username: {target_username}"
        return False, f"Invalid target username: {target_username}"

    # Validate login username (could be email, phone or username)
    if not validate_instagram_login_identifier(login_username):
        active_downloads[target_username] = f"Invalid login username: {login_username}"
        return False, f"Invalid login username: {login_username}"

    # Validate that session_file is in expected format (not arbitrary paths)
    if '..' in session_file or session_file.startswith('/') or not session_file.endswith('.session'):
        active_downloads[target_username] = "Invalid session file"
        return False, "Invalid session file"

    L = instaloader.Instaloader()

    try:
        # Load the session
        L.load_session_from_file(login_username, session_file)

        # Create download directory
        download_dir = f'./downloads/{target_username}'
        os.makedirs(download_dir, exist_ok=True)
        L.dirname_pattern = download_dir
        L.save_metadata = False
        L.post_metadata_txt_pattern = ''

        # Download the profile
        profile = instaloader.Profile.from_username(L.context, target_username)
        posts = profile.get_posts()

        post_count = 0
        for post in posts:
            L.download_post(post, target=f'{target_username}')
            post_count += 1

            # Simple progress tracking (in a real app you might want to use websockets)
            active_downloads[target_username] = f"Downloaded {post_count} posts..."

        # Update status when complete
        download_completion_msg = f"Download of {target_username} completed successfully! ({post_count} posts)"
        active_downloads[target_username] = download_completion_msg

        # If email requested, send the downloaded files
        if send_email and email_address:
            # Get all files in the download directory
            attachment_paths = []
            for root, dirs, files in os.walk(download_dir):
                for file in files:
                    attachment_paths.append(os.path.join(root, file))

            if attachment_paths:
                success, msg = send_email_with_attachments(
                    email_address,
                    f"Instagram Download - {target_username}",
                    f"Download of Instagram profile {target_username} completed with {post_count} posts.",
                    attachment_paths
                )
                if success:
                    active_downloads[target_username] = f"{download_completion_msg} Files sent to {email_address}."
                else:
                    active_downloads[target_username] = f"{download_completion_msg} But failed to send email: {msg}"
            else:
                active_downloads[target_username] = f"{download_completion_msg} But no files found to send."

        return True, download_completion_msg
    except instaloader.exceptions.ProfileNotExistsException:
        error_msg = f"Profile {target_username} does not exist"
        active_downloads[target_username] = error_msg
        return False, error_msg
    except instaloader.exceptions.BadCredentialsException:
        error_msg = "Invalid credentials. Please check your session file and username."
        active_downloads[target_username] = error_msg
        return False, error_msg
    except Exception as e:
        error_msg = str(e)
        active_downloads[target_username] = f"Error: {error_msg}"
        return False, error_msg

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create_session', methods=['POST'])
def create_session():
    username = request.form.get('username')
    password = request.form.get('password')

    if not username or not password:
        flash('Please provide both username and password.')
        return redirect(url_for('index'))

    # Basic validation to prevent obvious attacks
    if len(password) < 6:
        flash('Password is too short.')
        return redirect(url_for('index'))

    success, result = create_instagram_session(username, password)

    if success:
        # Extract just the filename from the full path to show to the user
        import os
        session_filename = os.path.basename(result)
        flash(f'Session created successfully! File: {session_filename}')
        flash(f'Full path: {result}')
    else:
        flash(f'Error creating session: {result}')

    return redirect(url_for('index'))

@app.route('/download_profile', methods=['POST'])
def download_profile():
    target_username = request.form.get('target_username')
    session_file = request.form.get('session_file')
    login_username = request.form.get('login_username')
    send_email = request.form.get('send_email') == 'on'  # Checkbox value
    email_address = request.form.get('email_address', '').strip()

    if not target_username or not session_file or not login_username:
        flash('Please provide target username, session file, and login username.')
        return redirect(url_for('index'))

    # If sending email, validate the email address
    if send_email and not email_address:
        flash('Please provide an email address to send the downloads.')
        return redirect(url_for('index'))

    # Basic email validation
    if send_email and '@' not in email_address:
        flash('Please provide a valid email address.')
        return redirect(url_for('index'))

    # Validate target username (must be a valid Instagram username)
    if not validate_instagram_username(target_username):
        flash('Invalid target username format.')
        return redirect(url_for('index'))

    # Validate login username (could be email, phone or username)
    if not validate_instagram_login_identifier(login_username):
        flash('Invalid login identifier format (could be username, email, or phone).')
        return redirect(url_for('index'))

    # Check if session file exists and is in correct format
    if not os.path.exists(session_file) or not session_file.endswith('.session'):
        flash(f'Invalid or non-existent session file: {session_file}')
        return redirect(url_for('index'))

    # Initialize download status
    active_downloads[target_username] = "Starting download..."

    # Start download in a separate thread
    thread = Thread(
        target=download_profile_with_session,
        args=(target_username, session_file, login_username, send_email, email_address)
    )
    thread.daemon = True  # Thread will close when main process ends
    thread.start()

    flash(f'Download started for {target_username}. You can check the status below.')
    return redirect(url_for('index'))

@app.route('/status/<target_username>')
def download_status(target_username):
    # Validate username format
    if not validate_instagram_username(target_username):
        return jsonify({"status": "Invalid username"}), 400

    status = active_downloads.get(target_username, "No active download")
    return {"status": status}

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('./downloads', exist_ok=True)
    os.makedirs('./templates', exist_ok=True)

    # Perform cleanup of old session files
    cleanup_session_files()

    app.run(debug=True, host='0.0.0.0', port=5000)