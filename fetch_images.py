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

# Naya Website/API Setup (Agar exact api path kuch aur hai, toh yaha update kar sakte hain)
API_BASE_URL = "https://shreevibes.vercel.app/api/search" 
MAX_API_CALLS = 200      # 200 API calls limit per day
MAX_IMAGES_PER_CAT = 5   # Ek topic me kitni images chahiye

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
    """Smartly JSON se image URLs nikalta hai, format chahe jo ho"""
    if isinstance(data, list):
        return [item for item in data if isinstance(item, str) and item.startswith('http')]
    elif isinstance(data, dict):
        # Common keys jisme array of images hota hai
        for key in ['url', 'urls', 'images', 'data', 'results']:
            if key in data and isinstance(data[key], list) and len(data[key]) > 0:
                if isinstance(data[key][0], str):
                    return data[key]
                elif isinstance(data[key][0], dict):
                    # Agar dictionary ke andar hai toh 'url' ya 'image' nikalega
                    return [item.get('url', item.get('image', item.get('src'))) for item in data[key] if isinstance(item, dict)]
        
        # Agar single URL string form me de diya
        if 'url' in data and isinstance(data['url'], str):
            return [data['url']]
    return []

def fetch_and_upload_images():
    print("🚀 Starting Fast Search Image Fetcher...")
    
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

        # Search Query parameters
        api_url = f"{API_BASE_URL}?q={requests.utils.quote(category)}"
        print(f"  └── 📡 Searching API for: '{category}'")
        
        api_calls_made += 1
        try:
            # 1. Sirf ek baar hit karega (Search)
            response = requests.get(api_url, timeout=30)
            
            if response.status_code == 200:
                json_data = response.json()
                
                # 2. JSON se Top images nikalna
                img_urls = extract_urls_from_json(json_data)
                
                if img_urls:
                    # Sirf utni hi images lega jitni bachi hain (e.g., pehle se 2 done hain toh 3 aur lega)
                    needed_images = MAX_IMAGES_PER_CAT - images_done
                    urls_to_download = img_urls[:needed_images]
                    
                    print(f"      ✅ Found {len(img_urls)} images. Downloading {len(urls_to_download)} new images...")
                    
                    # 3. Ek ek karke images download aur save karega
                    for idx, img_url in enumerate(urls_to_download):
                        
                        if not img_url:
                            continue
                            
                        # Download image
                        img_response = requests.get(img_url, timeout=30)
                        if img_response.status_code == 200:
                            img_content = img_response.content
                            
                            # GitHub me save karna (Path: Topics/Topic/Category/images/1.jpg)
                            img_filename = f"{images_done + 1}.jpg"
                            github_path = f"Topics/{topic}/{category}/images/{img_filename}"
                            
                            try:
                                repo.create_file(
                                    path=github_path, 
                                    message=f"Auto: Added {img_filename} for {category}", 
                                    content=img_content,
                                    branch="main"
                                )
                                print(f"      📥 Saved: {github_path}")
                                
                                # Progress increase karna
                                images_done += 1
                                tracking_data[track_key] = images_done
                                
                            except GithubException as e:
                                if e.status == 422:
                                    print(f"      ⚠️ {img_filename} already exists. Skipping count.")
                                    images_done += 1
                                    tracking_data[track_key] = images_done
                                else:
                                    print(f"      ❌ Github Upload Error: {e.data.get('message')}")
                        else:
                            print(f"      ❌ Image URL load nahi hua: {img_url}")
                        
                        # Thoda delay taaki GitHub API overload na ho
                        time.sleep(1) 
                else:
                    print(f"      ❌ API JSON se URLs extract nahi ho paye: {json_data}")
            else:
                print(f"      ❌ API HTTP Error: {response.status_code}")
                
        except requests.exceptions.Timeout:
            print("      ❌ Timeout Error: Search API is taking too long.")
        except Exception as e:
            print(f"      ❌ Unexpected Error: {e}")
        
        # Ek topic pura hone ke baad thoda rest
        time.sleep(2)

    # 4. Save progress
    print("\n💾 Saving tracking progress to GitHub...")
    update_tracking_data(repo, tracking_data, tracking_sha)
    print("🎉 ALL TASKS FINISHED!")

if __name__ == "__main__":
    fetch_and_upload_images()
