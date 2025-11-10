from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
import instaloader
from instaloader.exceptions import ProfileNotExistsException, LoginRequiredException, PrivateProfileNotFollowedException
import os
from typing import Optional, List
from pathlib import Path

def get_instaloader_instance():
    """Create an InstaLoader instance and login if credentials are available"""
    loader = instaloader.Instaloader()
    username = os.environ.get("INSTAGRAM_USERNAME")
    password = os.environ.get("INSTAGRAM_PASSWORD")
    if username and password:
        try:
            loader.login(username, password)
            print("Logged in to Instagram successfully.")
        except Exception as e:
            print(f"Failed to log in to Instagram: {e}")
    else:
        print("Instagram credentials not found in environment variables.")
    return loader

app = FastAPI(
    title="InstaLoader API",
    description="Instagram media downloader API",
    version="1.0.0"
)

# Job storage (in production, use Redis or database)
jobs = {}

class DownloadRequest(BaseModel):
    target: str  # Instagram username or URL
    download_type: str = "auto"  # "profile", "post", or "auto"

class JobStatus(BaseModel):
    job_id: str
    status: str  # "pending", "processing", "completed", "failed"
    progress: Optional[str] = None
    result: Optional[dict] = None

@app.get("/")
def read_root():
    return {"message": "InstaLoader API", "status": "running"}

@app.post("/api/download")
def start_download(request: DownloadRequest, background_tasks: BackgroundTasks):
    # Generate job ID
    import uuid
    job_id = str(uuid.uuid4())
    
    jobs[job_id] = {
        "status": "pending",
        "progress": "Initializing...",
        "result": None
    }
    
    # Determine if it's a profile or post download
    if request.download_type == "auto":
        if "instagram.com/p/" in request.target or "instagram.com/reel/" in request.target:
            download_type = "post"
        else:
            download_type = "profile"
    else:
        download_type = request.download_type
    
    # Add background task
    background_tasks.add_task(process_media_request, job_id, request.target, download_type)
    
    return {"job_id": job_id, "message": "Request received. Processing..."}

def process_media_request(job_id: str, target: str, download_type: str):
    jobs[job_id]["status"] = "processing"
    jobs[job_id]["progress"] = f"Fetching media URLs for {target}"
    
    try:
        media_urls = []
        if download_type == "profile":
            media_urls = get_profile_media_urls(target)
        elif download_type == "post":
            media_urls = get_post_media_urls(target)
        
        jobs[job_id]["status"] = "completed"
        jobs[job_id]["progress"] = f"Found {len(media_urls)} media items."
        jobs[job_id]["result"] = {
            "media_urls": media_urls,
            "message": "Media URLs fetched successfully."
        }
        
    except (ProfileNotExistsException, LoginRequiredException, PrivateProfileNotFollowedException) as e:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["progress"] = f"Error: {str(e)}"
        jobs[job_id]["result"] = {"error": str(e)}
    except Exception as e:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["progress"] = f"An unexpected error occurred: {str(e)}"
        jobs[job_id]["result"] = {"error": str(e)}

def get_profile_media_urls(username: str) -> List[str]:
    """Get all media URLs from an Instagram profile"""
    loader = get_instaloader_instance()
    profile = instaloader.Profile.from_username(loader.context, username)
    
    urls = []
    for post in profile.get_posts():
        if post.is_video:
            urls.append(post.video_url)
        else:
            urls.append(post.url)
    return urls

def get_post_media_urls(url: str) -> List[str]:
    """Get media URL(s) from a single Instagram post"""
    loader = get_instaloader_instance()
    
    if "p/" in url:
        shortcode = url.split("/p/")[1].split("/")[0]
    elif "reel/" in url:
        shortcode = url.split("/reel/")[1].split("/")[0]
    else:
        raise ValueError("Invalid Instagram URL")
        
    post = instaloader.Post.from_shortcode(loader.context, shortcode)
    
    urls = []
    if post.is_video:
        urls.append(post.video_url)
    else:
        # Handle sidecars (carousels)
        if post.typename == 'GraphImage':
            urls.append(post.url)
        elif post.typename == 'GraphSidecar':
            for node in post.get_sidecar_nodes():
                if node.is_video:
                    urls.append(node.video_url)
                else:
                    urls.append(node.display_url)
    return urls

@app.get("/api/status/{job_id}")
def get_job_status(job_id: str):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return JobStatus(
        job_id=job_id,
        status=jobs[job_id]["status"],
        progress=jobs[job_id]["progress"],
        result=jobs[job_id]["result"]
    )

@app.get("/api/profile-info/{username}")
def get_profile_info(username: str):
    try:
        loader = get_instaloader_instance()
        profile = instaloader.Profile.from_username(loader.context, username)
        
        return {
            "username": profile.username,
            "full_name": profile.full_name,
            "followers": profile.followers,
            "posts": profile.mediacount,
            "biography": profile.biography,
            "is_private": profile.is_private
        }
    except instaloader.exceptions.ProfileNotExistsException:
        raise HTTPException(status_code=404, detail=f"Profile {username} does not exist")
    except instaloader.exceptions.LoginRequiredException:
        raise HTTPException(status_code=401, detail="Login required to access this profile")
    except instaloader.exceptions.PrivateProfileNotFollowedException:
        raise HTTPException(status_code=403, detail=f"Profile {username} is private and not followed")
    except Exception as e:
        print(f"Error fetching profile info for {username}: {e}")
        raise HTTPException(status_code=400, detail=f"Error fetching profile info: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)