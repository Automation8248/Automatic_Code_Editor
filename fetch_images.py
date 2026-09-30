import os
import time
import json
import requests
from github import Github, GithubException, Auth

# ==========================================
# 1. main.py se DATA ko import karna
# ==========================================
try:
    from main import DATA
except ImportError:
    print("❌ Error: main.py file nahi mili ya usme DATA list nahi hai.")
    exit()

# ==========================================
# ⚙️ CONFIGURATION
# ==========================================
GITHUB_TOKEN = os.getenv("GH_TOKEN") 
REPO_NAME = "Automation8248/Faceless-fact-yt"

# Naya Railway Backend API
API_BASE_URL = "https://shreevibesbackend-production.up.railway.app/api/v1/search" 
MAX_API_CALLS = 200      # GitHub Actions run ki max limit
MAX_IMAGES_PER_CAT = 5   # Ek topic me 5 images

TRACKING_FILE_PATH = "tracking.json"

def get_tracking_data(repo):
    """GitHub se tracking file uthana"""
    try:
        file_content = repo.get_contents(TRACKING_FILE_PATH)
        return json.loads(file_content.decoded_content.decode('utf-8')), file_content.sha
    except GithubException as e:
        if e.status == 404:
            return {}, None
        raise

def update_tracking_data(repo, tracking_dict, sha):
    """Tracking progress GitHub par wapas save karna"""
    content = json.dumps(tracking_dict, indent=4)
    if sha:
        repo.update_file(TRACKING_FILE_PATH, "Auto: Updated image tracking", content, sha, branch="main")
    else:
        repo.create_file(TRACKING_FILE_PATH, "Auto: Created image tracking", content, branch="main")

def extract_urls_from_json(data):
    """Naye JSON format se 'large' images (.jpg, .png, etc) extract karna"""
    urls = []
    if isinstance(data, dict) and "results" in data:
        for item in data["results"]:
            img_url = item.get("large")
            # Check for direct image extension formats
            if img_url and any(img_url.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.webp']):
                urls.append(img_url)
    return urls

def fetch_and_upload_images():
    print("🚀 Starting Smart & Safe Image Fetcher...")
    
    if not GITHUB_TOKEN:
        print("❌ Error: GH_TOKEN is missing in environment!")
        return

    # GitHub Connection
    auth = Auth.Token(GITHUB_TOKEN)
    g = Github(auth=auth)
    repo = g.get_repo(REPO_NAME)
    
    tracking_data, tracking_sha = get_tracking_data(repo)
    api_calls_made = 0

    print(f"📊 Tracking data loaded. Total categories to process: {len(DATA)}\n")

    for item in DATA:
        if api_calls_made >= MAX_API_CALLS:
            print("🛑 Limit Reached: 200 API calls done for today.")
            break

        topic = str(item['Topic']).strip()
        category = str(item['Category']).strip()
        track_key = f"{topic}_{category}"
        images_done = tracking_data.get(track_key, 0)
        
        if images_done >= MAX_IMAGES_PER_CAT:
            print(f"⏭️ Skipped: {topic} -> {category} (Already has {MAX_IMAGES_PER_CAT} images)")
            continue
            
        print(f"⏳ Processing: {topic} -> {category}")

        # Construct API URL with count=25
        api_url = f"{API_BASE_URL}?q={requests.utils.quote(category)}&count=25"
        print(f"  └── 📡 Searching API for: '{category}'")
        
        api_calls_made += 1
        try:
            response = requests.get(api_url, timeout=30)
            
            # --- IP RATE LIMIT SAFETY: 30 requests per min (1 request har 2 sec) ---
            # Hum 2.5 sec ka delay de rahe hain taaki IP block na ho
            time.sleep(2.5) 
            
            if response.status_code == 200:
                json_data = response.json()
                
                # Extract image links
                img_urls = extract_urls_from_json(json_data)
                
                if img_urls:
                    needed_images = MAX_IMAGES_PER_CAT - images_done
                    urls_to_download = img_urls[:needed_images]
                    
                    print(f"      ✅ Found {len(img_urls)} valid images. Downloading {len(urls_to_download)} new images...")
                    
                    for idx, img_url in enumerate(urls_to_download):
                        if not img_url:
                            continue
                            
                        # Download image
                        try:
                            img_response = requests.get(img_url, timeout=30)
                            if img_response.status_code == 200:
                                img_content = img_response.content
                                
                                # File path format (Topics/World Records/Tallest Person/images/1.jpg)
                                # URL se original extension nikalna (.png ya .jpg)
                                ext = os.path.splitext(img_url.split('/')[-1])[1]
                                if not ext: ext = ".jpg" # fallback
                                
                                img_filename = f"{images_done + 1}{ext}"
                                github_path = f"Topics/{topic}/{category}/images/{img_filename}"
                                
                                try:
                                    repo.create_file(
                                        path=github_path, 
                                        message=f"Auto: Added {img_filename} for {category}", 
                                        content=img_content,
                                        branch="main"
                                    )
                                    print(f"      📥 Saved: {github_path}")
                                    images_done += 1
                                    tracking_data[track_key] = images_done
                                    
                                except GithubException as e:
                                    if e.status == 422: # File already exists
                                        print(f"      ⚠️ {img_filename} already exists. Skipping count.")
                                        images_done += 1
                                        tracking_data[track_key] = images_done
                                    else:
                                        print(f"      ❌ Github Upload Error: {e.data.get('message')}")
                            else:
                                print(f"      ❌ Image Download Failed (HTTP {img_response.status_code}): {img_url}")
                        except Exception as e:
                            print(f"      ❌ Error downloading {img_url}: {e}")
                        
                        # GitHub API overload se bachne ke liye chhota delay
                        time.sleep(1) 
                else:
                    print("      ❌ API returned JSON but no valid image URLs (.jpg/.png) found.")
            else:
                print(f"      ❌ API HTTP Error: {response.status_code}")
                
        except requests.exceptions.Timeout:
            print("      ❌ Timeout Error: Search API is taking too long.")
        except Exception as e:
            print(f"      ❌ Unexpected Error: {e}")

    # Aakhiri me JSON ko GitHub me save karna
    print("\n💾 Saving tracking progress to GitHub...")
    update_tracking_data(repo, tracking_data, tracking_sha)
    print("🎉 ALL TASKS FINISHED!")

if __name__ == "__main__":
    fetch_and_upload_images()
