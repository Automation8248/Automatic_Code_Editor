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
API_KEY = "ansh"
# Naya API URL update kar diya gaya hai
API_BASE_URL = "https://ansh-apis.is-dev.org/api/nano" 
MAX_API_CALLS = 200      # 200 calls daily limit
MAX_IMAGES_PER_CAT = 5  # Har folder me maximum 5 images
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

def fetch_and_upload_images():
    print("🚀 Starting Image Fetcher (Handles 30s Generation Time)...")
    
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
        
        # Tracking key e.g., "World Records_Tallest Person"
        track_key = f"{topic}_{category}"
        images_done = tracking_data.get(track_key, 0)
        
        if images_done >= MAX_IMAGES_PER_CAT:
            print(f"⏭️ Skipped: {topic} -> {category} (Already has {MAX_IMAGES_PER_CAT} images)")
            continue
            
        print(f"⏳ Processing: {topic} -> {category} (Need {MAX_IMAGES_PER_CAT - images_done} more images)")

        while images_done < MAX_IMAGES_PER_CAT and api_calls_made < MAX_API_CALLS:
            search_query = f"{category} {images_done + 1}"
            
            # Yahan 'search=' ki jagah 'prompt=' kar diya gaya hai
            api_url = f"{API_BASE_URL}?key={API_KEY}&prompt={requests.utils.quote(search_query)}"
            
            print(f"  └── 📡 Requesting API for image {images_done + 1} (Waiting for generation...)")
            
            api_calls_made += 1
            try:
                # 1. API Call with 120s timeout (Taaki 30 sec lagne par crash na ho)
                response = requests.get(api_url, timeout=120)
                
                if response.status_code == 200:
                    json_data = response.json()
                    
                    # 2. JSON se URL extract karna
                    img_url = json_data.get("url")
                    is_success = json_data.get("success", True) 
                    
                    if img_url and is_success:
                        print(f"      ✅ JSON received! Image URL: {img_url}")
                        
                        # 3. Image download karna
                        img_response = requests.get(img_url, timeout=60)
                        if img_response.status_code == 200:
                            img_content = img_response.content
                            
                            # 4. GitHub me save karna
                            img_filename = f"{images_done + 1}.jpg"
                            github_path = f"Topics/{topic}/{category}/images/{img_filename}"
                            
                            try:
                                repo.create_file(
                                    path=github_path, 
                                    message=f"Auto: Added {img_filename} for {category}", 
                                    content=img_content,
                                    branch="main"
                                )
                                print(f"      📥 Saved permanently to: {github_path}")
                                
                                # Progress increase karna
                                images_done += 1
                                tracking_data[track_key] = images_done
                                
                            except GithubException as e:
                                if e.status == 422:
                                    print("      ⚠️ File already exists. Skipping count.")
                                    images_done += 1
                                    tracking_data[track_key] = images_done
                                else:
                                    print(f"      ❌ Github Upload Error: {e.data.get('message')}")
                        else:
                            print("      ❌ Image URL khul nahi raha hai (Download failed).")
                    else:
                        print(f"      ❌ API JSON failed or URL missing: {json_data}")
                else:
                    print(f"      ❌ API HTTP Error: {response.status_code}")
                    
            except requests.exceptions.Timeout:
                print("      ❌ Timeout Error: API ne 120 seconds se zyada time le liya.")
            except Exception as e:
                print(f"      ❌ Unexpected Error: {e}")
            
            # Har image banne ke baad 2 second ruko taaki API server overload na ho
            time.sleep(2)

    # 5. Save the final count in tracking.json so it remembers tomorrow
    print("\n💾 Saving tracking progress to GitHub...")
    update_tracking_data(repo, tracking_data, tracking_sha)
    print("🎉 ALL TASKS FINISHED!")

if __name__ == "__main__":
    fetch_and_upload_images()
