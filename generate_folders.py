import os
import time
import requests
import io
import pandas as pd
from github import Github, GithubException, Auth

# ==========================================
# ⚙️ CONFIGURATION SETTINGS
# ==========================================
# GitHub Actions se token uthayega
GITHUB_TOKEN = os.getenv("GH_TOKEN") 
REPO_NAME = "Automation8248/Faceless-fact-yt"
EXCEL_URL = "https://files.catbox.moe/a1eba7.xlsx"

def aggressive_create_file(repo, path, message, content):
    """File create karne ka aggressive function jo errors handle karega"""
    try:
        repo.create_file(path=path, message=message, content=content, branch="main")
        return True, "✅ Created"
    except GithubException as e:
        if e.status == 422:
            return False, "⏭️ Skipped (Already exists)"
        elif e.status == 403:
            # Agar GitHub aggressively block kare, toh 2 second ruk kar wapas try kare
            time.sleep(2)
            try:
                repo.create_file(path=path, message=message, content=content, branch="main")
                return True, "✅ Created on Retry"
            except:
                return False, f"❌ Failed on Retry: {e.data.get('message', str(e))}"
        else:
            return False, f"❌ Error: {e.data.get('message', str(e))}"

def create_github_files():
    print("🚀 Starting AGGRESSIVE Folder Generation...")
    
    if not GITHUB_TOKEN:
        print("❌ Error: GH_TOKEN secret is not set!")
        return

    try:
        # Naya Token Auth Format
        auth = Auth.Token(GITHUB_TOKEN)
        g = Github(auth=auth)
        repo = g.get_repo(REPO_NAME)
        print(f"✅ Connected to repository: {REPO_NAME}")
    except Exception as e:
        print(f"❌ GitHub connection failed: {e}")
        return

    # Excel Download
    try:
        print(f"🌐 Fetching data from: {EXCEL_URL}...")
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(EXCEL_URL, headers=headers)
        response.raise_for_status() 
        
        excel_data = io.BytesIO(response.content)
        df = pd.read_excel(excel_data, engine='openpyxl')
        print(f"✅ Data Loaded. Total Tasks: {len(df) * 2} files to create.\n")
    except Exception as e:
        print(f"❌ Excel fetch error: {e}")
        return

    print("-" * 50)
    
    # Fast Loop (No sleep delay)
    for index, row in df.iterrows():
        try:
            main_topic = str(row['Topic']).strip()      
            sub_category = str(row['Category']).strip() 
            
            if pd.isna(row['Topic']) or pd.isna(row['Category']) or main_topic == 'nan' or sub_category == 'nan':
                continue

            facts_path = f"Topics/{main_topic}/{sub_category}/facts.txt"
            images_path = f"Topics/{main_topic}/{sub_category}/images/1.txt"
            
            print(f"⚡ [{index + 1}/{len(df)}] {main_topic} -> {sub_category}")
            
            # Create facts.txt quickly
            status1, msg1 = aggressive_create_file(
                repo, facts_path, 
                f"Auto: Facts for {sub_category}", 
                f"Here are amazing facts about {sub_category}."
            )
            print(f"  ├── {msg1}: {facts_path}")

            # Create images/1.txt quickly
            status2, msg2 = aggressive_create_file(
                repo, images_path, 
                f"Auto: Image for {sub_category}", 
                f"Image URL for {sub_category} will be saved here."
            )
            print(f"  └── {msg2}: {images_path}")

            # Koi extra time.sleep() nahi lagaya hai, code ful speed par chalega

        except KeyError as e:
            print(f"❌ Column missing in Excel: {e}")
            break
            
    print("-" * 50)
    print("🎉 ALL DONE! Maximum speed execution finished.")

if __name__ == "__main__":
    create_github_files()
