import os
import requests
import sys

API_URL = "https://shreecloud.up.railway.app/api/v1/upload"
API_KEY = os.getenv("SHREE_API_KEY")
FOLDER_NAME = "Income AI"

def download_file(url):
    local_filename = url.split('/')[-1]
    print(f"Downloading {local_filename} from {url}...")
    
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    return local_filename

def upload_file(file_path):
    print(f"Uploading {file_path} to {API_URL} in folder '{FOLDER_NAME}'...")
    
    headers = {
        "X-API-Key": API_KEY
    }
    
    # We pass the folder name as form data. 
    # If the API requires a different key like 'path' or 'directory', change "folder" below.
    data = {
        "folder": FOLDER_NAME 
    }
    
    with open(file_path, 'rb') as f:
        files = {'file': (os.path.basename(file_path), f)}
        response = requests.post(API_URL, headers=headers, files=files, data=data)
        
    if response.status_code in [200, 201]:
        print(f"Success! {file_path} uploaded.")
    else:
        print(f"Failed to upload {file_path}. Status: {response.status_code}, Response: {response.text}")

if __name__ == "__main__":
    if not API_KEY:
        print("Error: SHREE_API_KEY environment variable is not set.")
        sys.exit(1)

    if not os.path.exists("filelink.txt"):
        print("Error: filelink.txt not found.")
        sys.exit(1)

    with open("filelink.txt", "r") as file:
        urls = [line.strip() for line in file if line.strip()]

    for url in urls:
        downloaded_file = download_file(url)
        upload_file(downloaded_file)
        # Clean up local file after upload to save runner space
        os.remove(downloaded_file)
