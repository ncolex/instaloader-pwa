import os
import instaloader
import sys

def download_profile_with_login(username, username_login=None, password=None):
    """
    Download all media from an Instagram profile using login credentials if needed
    """
    print(f"Starting download of profile: {username}")
    
    # Create an Instaloader instance
    loader = instaloader.Instaloader()
    loader.save_metadata = False
    loader.post_metadata_txt_pattern = ""
    loader.dirname_pattern = f"./downloads/{username}"  # Download to local directory
    
    # Login if credentials are provided
    if username_login and password:
        try:
            loader.login(username_login, password)
            print("Logged in successfully")
        except Exception as e:
            print(f"Login failed: {str(e)}")
            return False
    
    try:
        # Download the profile
        loader.download_profile(username, profile_pic=True, profile_pic_only=False)
        print(f"Download of profile {username} completed successfully!")
        
        return True
        
    except instaloader.exceptions.ProfileNotExistsException:
        print(f"Error: Profile '{username}' does not exist.")
    except instaloader.exceptions.LoginRequiredException:
        print(f"Error: Login required to access profile '{username}'.")
        print("Try providing Instagram login credentials.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    
    return False

def get_post_count_with_login(username, username_login=None, password=None):
    """
    Get the number of posts for a given username with optional login
    """
    try:
        L = instaloader.Instaloader()
        
        # Login if credentials are provided
        if username_login and password:
            L.login(username_login, password)
        
        profile = instaloader.Profile.from_username(L.context, username)
        posts = profile.get_posts()
        count = sum(1 for _ in posts)  # Count all posts
        return count
    except Exception as e:
        print(f"Error getting post count: {str(e)}")
        return 0

def download_with_session(username, session_file=None):
    """
    Download using a saved session file (more secure than username/password)
    """
    print(f"Starting download of profile: {username} using session")
    
    # Create an Instaloader instance
    loader = instaloader.Instaloader()
    loader.save_metadata = False
    loader.post_metadata_txt_pattern = ""
    loader.dirname_pattern = f"./downloads/{username}"  # Download to local directory
    
    # Load session if file is provided
    if session_file and os.path.isfile(session_file):
        try:
            loader.load_session_from_file(username_login, session_file)
            print("Session loaded successfully")
        except Exception as e:
            print(f"Session loading failed: {str(e)}")
            return False
    
    try:
        # Download the profile
        loader.download_profile(username, profile_pic=True, profile_pic_only=False)
        print(f"Download of profile {username} completed successfully!")
        
        return True
        
    except instaloader.exceptions.ProfileNotExistsException:
        print(f"Error: Profile '{username}' does not exist.")
    except instaloader.exceptions.LoginRequiredException:
        print(f"Error: Login required to access profile '{username}'.")
        print("Try providing Instagram login credentials or a valid session file.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    
    return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 download_instagram_profile_with_login.py <target_username> [session_file]")
        print("       python3 download_instagram_profile_with_login.py <target_username> <login_username> <password>")
        print("Example 1: python3 download_instagram_profile_with_login.py alvelalucas my_session")
        print("Example 2: python3 download_instagram_profile_with_login.py alvelalucas myusername mypassword")
        sys.exit(1)
    
    target_username = sys.argv[1]
    
    # Create downloads directory
    os.makedirs(f"./downloads/{target_username}", exist_ok=True)
    
    if len(sys.argv) == 3:  # Using session file
        session_file = sys.argv[2]
        print(f"Using session file: {session_file}")
        download_with_session(target_username, session_file)
    elif len(sys.argv) == 4:  # Using username and password
        login_username = sys.argv[2]
        password = sys.argv[3]
        print(f"Getting post count for {target_username}...")
        post_count = get_post_count_with_login(target_username, login_username, password)
        print(f"Found {post_count} posts for {target_username}")
        
        print(f"Starting download for {target_username}...")
        download_profile_with_login(target_username, login_username, password)
    else:  # No authentication
        print(f"Getting post count for {target_username}...")
        post_count = get_post_count_with_login(target_username)
        print(f"Found {post_count} posts for {target_username}")
        
        print(f"Starting download for {target_username}...")
        download_profile_with_login(target_username)