import os
import sys
import requests
from mega import Mega

MEGA_EMAIL = os.getenv("MEGA_EMAIL")
MEGA_PASSWORD = os.getenv("MEGA_PASSWORD")
FOLDER_NAME = "Income AI"

def download_file(url):
    local_filename = url.split('/')[-1].split('?')[0]
    print(f"Downloading {local_filename} from {url}...")
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024 * 1024):  # 1MB chunks
                if chunk:
                    f.write(chunk)
    return local_filename

def main():
    if not MEGA_EMAIL or not MEGA_PASSWORD:
        print("Error: MEGA_EMAIL ya MEGA_PASSWORD environment variable set nahi hai.")
        sys.exit(1)

    if not os.path.exists("filelink.txt"):
        print("Error: filelink.txt nahi mila.")
        sys.exit(1)

    # MEGA initialize aur login
    print("Logging into MEGA...")
    mega = Mega()
    m = mega.login(MEGA_EMAIL, MEGA_PASSWORD)

    # Check ya create "Income AI" folder
    folder = m.find(FOLDER_NAME)
    if not folder:
        print(f"Creating folder '{FOLDER_NAME}' on MEGA...")
        folder = m.create_folder(FOLDER_NAME)
        folder_node = folder[FOLDER_NAME]
    else:
        folder_node = folder[0]

    with open("filelink.txt", "r") as file:
        urls = [line.strip() for line in file if line.strip()]

    for url in urls:
        file_path = download_file(url)
        print(f"Uploading {file_path} to MEGA folder '{FOLDER_NAME}'...")
        
        # File upload karna
        uploaded_file = m.upload(file_path, folder_node)
        
        # Public download URL nikalna
        public_url = m.get_upload_link(uploaded_file)
        print(f"Upload Complete! Download Link: {public_url}")

        # Local runner space clean karna
        if os.path.exists(file_path):
            os.remove(file_path)

if __name__ == "__main__":
    main()
