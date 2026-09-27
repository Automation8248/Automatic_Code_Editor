import os
import shutil
import sys
from huggingface_hub import hf_hub_download

# Aapka Hugging Face Token GitHub Secrets se aayega
HF_TOKEN = os.getenv("HF_TOKEN")

# Aapki Repo aur File ki details
REPO_ID = "automation8248/Income_AI_Models"

# Yahan hum path de rahe hain aur local_name me .exe laga rahe hain
FILES_TO_DOWNLOAD = [
    {
        "repo_path": "AI_Models/qwen3-4b-thinking-2507.Q4_K_M.gguf", 
        "local_name": "qwen3-4b-thinking-2507.Q4_K_M.gguf"
    },
    {
        "repo_path": "AI_Models/llamafile-0.10.6",   # HuggingFace par bina .exe ke
        "local_name": "llamafile-0.10.6.exe"         # Rename hokar yahan .exe ban jayega
    }
]

def main():
    print("--- Downloading and Renaming Files ---")
    for file_info in FILES_TO_DOWNLOAD:
        repo_path = file_info["repo_path"]
        local_name = file_info["local_name"]
        
        print(f"Fetching '{repo_path}'...")
        
        try:
            # File download karna (Cache me save hogi)
            downloaded_file_path = hf_hub_download(
                repo_id=REPO_ID,
                filename=repo_path,
                repo_type="dataset",
                token=HF_TOKEN
            )
            
            # Cache se nikal kar main folder me copy + rename karna
            destination = os.path.join(os.getcwd(), local_name)
            shutil.copy(downloaded_file_path, destination)
            
            print(f"Success! File saved and renamed as: {local_name}\n")
            
        except Exception as e:
            print(f"Download fail ho gaya for {local_name}: {e}")
            sys.exit(1) # Error aane par rok dega

    print("--- Creating start.bat File ---")
    # Notepad me likhne wala command (Tunnel aur chat support ke liye host/port add kiya hai)
    bat_command = r".\llamafile-0.10.6.exe --server --model qwen3-4b-thinking-2507.Q4_K_M.gguf --host 0.0.0.0 --port 8080 --nobrowser"
    
    # Python khud start.bat banayega aur command usme paste kar dega
    with open("start.bat", "w", encoding="utf-8") as bat_file:
        bat_file.write(bat_command)
        
    print("Success! start.bat file create ho gayi hai.")

if __name__ == "__main__":
    main()
