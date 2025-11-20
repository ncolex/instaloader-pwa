import os
import instaloader
import sys

def download_profile(username):
    """
    Download all media from an Instagram profile
    """
    print(f"Starting download of profile: {username}")
    
    # Create an Instaloader instance
    loader = instaloader.Instaloader()
    loader.save_metadata = False
    loader.post_metadata_txt_pattern = ""
    loader.dirname_pattern = f"./downloads/{username}"  # Download to local directory
    
    try:
        # Download the profile
        loader.download_profile(username, profile_pic=True, profile_pic_only=False)
        print(f"Download of profile {username} completed successfully!")
        
        # Count the posts
        posts_count = loader.download_post_count
        print(f"Downloaded {posts_count} posts")
        
    except instaloader.exceptions.ProfileNotExistsException:
        print(f"Error: Profile '{username}' does not exist.")
    except instaloader.exceptions.LoginRequiredException:
        print(f"Error: Login required to access profile '{username}'.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

def get_post_count(username):
    """
    Get the number of posts for a given username
    """
    try:
        L = instaloader.Instaloader()
        profile = instaloader.Profile.from_username(L.context, username)
        posts = profile.get_posts()
        count = sum(1 for _ in posts)  # Count all posts
        return count
    except Exception as e:
        print(f"Error getting post count: {str(e)}")
        return 0

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 download_instagram_profile.py <username>")
        print("Example: python3 download_instagram_profile.py alvelalucas")
        sys.exit(1)
    
    username = sys.argv[1]
    
    # Create downloads directory
    os.makedirs(f"./downloads/{username}", exist_ok=True)
    
    print(f"Getting post count for {username}...")
    post_count = get_post_count(username)
    print(f"Found {post_count} posts for {username}")
    
    print(f"Starting download for {username}...")
    download_profile(username)