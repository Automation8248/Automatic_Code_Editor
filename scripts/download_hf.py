import os
import shutil
import sys
from huggingface_hub import hf_hub_download

# Aapka Hugging Face Token GitHub Secrets se aayega
HF_TOKEN = os.getenv("HF_TOKEN")

# Aapki Repo aur File ki details
REPO_ID = "automation8248/Income_AI_Models"

# Hum dono files (GGUF aur EXE) ko download karwayenge
FILES_TO_DOWNLOAD = [
    {"path": "AI_Models/qwen3-4b-thinking-2507.Q4_K_M.gguf", "name": "qwen3-4b-thinking-2507.Q4_K_M.gguf"},
    {"path": "AI_Models/llamafile-0.10.6.exe", "name": "llamafile-0.10.6.exe"}
]

def main():
    for file_info in FILES_TO_DOWNLOAD:
        file_path_in_repo = file_info["path"]
        output_name = file_info["name"]
        
        print(f"'{file_path_in_repo}' download ho raha hai...")
        
        try:
            # File download karne ka function (Cache me save hoti hai)
            downloaded_file_path = hf_hub_download(
                repo_id=REPO_ID,
                filename=file_path_in_repo,
                repo_type="dataset",  # Kyunki humne dataset banaya tha
                token=HF_TOKEN
            )
            
            # Download hone ke baad file ko root folder me copy karna taaki start.bat usko dhoondh sake
            destination = os.path.join(os.getcwd(), output_name)
            shutil.copy(downloaded_file_path, destination)
            
            print(f"Success! File successfully download ho gayi hai.")
            print(f"File yahan save hui hai: {destination}\n")
            
        except Exception as e:
            print(f"Download fail ho gaya for {output_name}: {e}")
            sys.exit(1) # Agar download fail ho to action ko rok de

if __name__ == "__main__":
    main()
