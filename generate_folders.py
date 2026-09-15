import os
import time
import requests
import io
import pandas as pd
from github import Github, GithubException, Auth

# ==========================================
# ⚙️ CONFIGURATION SETTINGS
# ==========================================
GITHUB_TOKEN = os.getenv("GH_TOKEN") 
REPO_NAME = "Automation8248/Faceless-fact-yt"
EXCEL_URL = "https://files.catbox.moe/a1eba7.xlsx"

def create_github_files():
    print("🔄 Initializing GitHub connection...")
    
    if not GITHUB_TOKEN:
        print("❌ Error: GH_TOKEN secret is not set in GitHub Actions!")
        return

    try:
        # Warning hatane ke liye naya Auth format
        auth = Auth.Token(GITHUB_TOKEN)
        g = Github(auth=auth)
        repo = g.get_repo(REPO_NAME)
        print(f"✅ Connected to repository: {REPO_NAME}")
    except Exception as e:
        print(f"❌ GitHub connection failed: {e}")
        return

    try:
        print(f"🌐 Downloading data from URL: {EXCEL_URL}...")
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(EXCEL_URL, headers=headers)
        response.raise_for_status() 
        
        excel_data = io.BytesIO(response.content)
        df = pd.read_excel(excel_data, engine='openpyxl')
        
        print(f"✅ Sheet loaded successfully. Total items to process: {len(df)}\n")
    except Exception as e:
        print(f"❌ Excel file fetch/load error: {e}")
        return

    print("-" * 50)
    
    for index, row in df.iterrows():
        try:
            main_topic = str(row['Topic']).strip()      
            sub_category = str(row['Category']).strip() 
            
            if pd.isna(row['Topic']) or pd.isna(row['Category']) or main_topic == 'nan' or sub_category == 'nan':
                continue

            facts_path = f"Topics/{main_topic}/{sub_category}/facts.txt"
            images_path = f"Topics/{main_topic}/{sub_category}/images/1.txt"
            
            print(f"⏳ [{index + 1}/{len(df)}] Processing: {main_topic} -> {sub_category}")
            
            # Create facts.txt
            try:
                repo.create_file(
                    path=facts_path,
                    message=f"Auto: Created facts file for {sub_category}",
                    content=f"Here are amazing facts about {sub_category}.",
                    branch="main" 
                )
                print(f"  ├── ✅ Created: {facts_path}")
            except GithubException as e:
                if e.status == 422:
                    print(f"  ├── ⏭️ Skipped: (Already exists)")
                else:
                    print(f"  ├── ❌ Error: {e.data.get('message', str(e))}")

            # Create images/1.txt
            try:
                repo.create_file(
                    path=images_path,
                    message=f"Auto: Created image placeholder for {sub_category}",
                    content=f"Image URL for {sub_category} will be saved here.",
                    branch="main"
                )
                print(f"  └── ✅ Created: {images_path}")
            except GithubException as e:
                if e.status == 422:
                    print(f"  └── ⏭️ Skipped: (Already exists)")
                else:
                    print(f"  └── ❌ Error: {e.data.get('message', str(e))}")
            
            time.sleep(1)

        except KeyError as e:
            print(f"❌ Column missing in Excel: {e}")
            break
            
    print("-" * 50)
    print("🎉 All tasks completed successfully!")

if __name__ == "__main__":
    create_github_files()
