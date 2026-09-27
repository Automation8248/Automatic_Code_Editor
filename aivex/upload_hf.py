import os
import sys
import requests
from huggingface_hub import HfApi, login

# GitHub secrets se token
HF_TOKEN = os.getenv("HF_TOKEN")

# Aapka Hugging Face Dataset repo aur destination folder
HF_REPO_ID = "automation8248/Income_AI_Models"
UPLOAD_FOLDER = "AI_Models"
FILE_LINK_PATH = "aivex/filelink.txt"  # Naya path update kiya gaya

def download_file(url):
    local_filename = url.split('/')[-1].split('?')[0]
    print(f"Downloading {local_filename} from {url}...")
    
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024 * 1024):  # 1MB chunk
                if chunk:
                    f.write(chunk)
    return local_filename

def main():
    if not HF_TOKEN:
        print("Error: HF_TOKEN environment variable set nahi hai.")
        sys.exit(1)

    # Naye path par file check karna
    if not os.path.exists(FILE_LINK_PATH):
        print(f"Error: '{FILE_LINK_PATH}' nahi mila.")
        sys.exit(1)

    print("Hugging Face me login ho raha hai...")
    login(token=HF_TOKEN)
    api = HfApi()

    # Public Dataset repo create karna
    api.create_repo(
        repo_id=HF_REPO_ID,
        repo_type="dataset",
        private=False,  # Public visibility
        exist_ok=True
    )

    # Naye path se file read karna
    with open(FILE_LINK_PATH, "r") as file:
        urls = [line.strip() for line in file if line.strip()]

    for url in urls:
        file_path = download_file(url)
        print(f"Uploading '{file_path}' to '{HF_REPO_ID}/{UPLOAD_FOLDER}'...")
        
        # Hugging Face par upload karna
        api.upload_file(
            path_or_fileobj=file_path,
            path_in_repo=f"{UPLOAD_FOLDER}/{file_path}",
            repo_id=HF_REPO_ID,
            repo_type="dataset"
        )
        print(f"Success! '{file_path}' upload ho gayi.")

        # Storage clean karna
        if os.path.exists(file_path):
            os.remove(file_path)

if __name__ == "__main__":
    main()
