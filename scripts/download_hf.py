import os
import shutil
import sys
from huggingface_hub import hf_hub_download

# Aapka Hugging Face Token
HF_TOKEN = os.getenv("HF_TOKEN")

REPO_ID = "automation8248/Income_AI_Models"

FILES_TO_DOWNLOAD = [
    {
        "repo_path": "AI_Models/qwen3-4b-thinking-2507.Q4_K_M.gguf", 
        "local_name": "qwen3-4b-thinking-2507.Q4_K_M.gguf"
    },
    {
        "repo_path": "AI_Models/llamafile-0.10.6",   
        "local_name": "llamafile-0.10.6.exe"         
    }
]

def main():
    print("--- Downloading and Renaming Files ---")
    for file_info in FILES_TO_DOWNLOAD:
        repo_path = file_info["repo_path"]
        local_name = file_info["local_name"]
        
        print(f"Fetching '{repo_path}'...")
        
        try:
            downloaded_file_path = hf_hub_download(
                repo_id=REPO_ID,
                filename=repo_path,
                repo_type="dataset",
                token=HF_TOKEN
            )
            destination = os.path.join(os.getcwd(), local_name)
            shutil.copy(downloaded_file_path, destination)
            print(f"Success! File saved as: {local_name}\n")
            
        except Exception as e:
            print(f"Download fail ho gaya for {local_name}: {e}")
            sys.exit(1)

    print("--- Creating start.bat File ---")
    
    # Yahan sirf aapka bataya hua exact command likha hai, koi extra word nahi.
    bat_command = r".\llamafile-0.10.6.exe --server --model qwen3-4b-thinking-2507.Q4_K_M.gguf"
    
    with open("start.bat", "w", encoding="utf-8") as bat_file:
        bat_file.write(bat_command)
        
    print("Success! start.bat file create ho gayi hai (Strict Format).")

if __name__ == "__main__":
    main()
