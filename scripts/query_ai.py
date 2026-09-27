import sys
import requests
import time

user_prompt = sys.argv[1] if len(sys.argv) > 1 else "Hello, please confirm your status."
LOCAL_AI_URL = "http://127.0.0.1:8080/v1/chat/completions"

print("--- AI Server Status Check ---")
print("Waiting for AI server to load into RAM (Max 2 minutes)...")

# 2 minutes wait logic: 24 loops * 5 seconds = 120 seconds
server_ready = False
for i in range(24):
    try:
        # Har 5 second me server ko ping karega
        requests.get("http://127.0.0.1:8080/", timeout=2)
        server_ready = True
        print("\n[SUCCESS] AI Server is UP and running!")
        break
    except requests.exceptions.ConnectionError:
        print(f"Server is loading... Checking ({i+1}/24)")
        time.sleep(5)

if not server_ready:
    print("\n[ERROR] AI server did not start within 2 minutes. Llamafile crashed or RAM is full.")
    sys.exit(1)

payload = {
    "messages": [
        {"role": "system", "content": "You are a fast and reliable AI assistant running locally."},
        {"role": "user", "content": user_prompt}
    ],
    "temperature": 0.7,
    "max_tokens": 1000
}

print(f"\nSending prompt to Local AI: '{user_prompt}'")
print("Waiting for AI response...")

try:
    # Timeout 180 seconds (3 minutes) kar diya hai kyunki ye fast work karta hai
    response = requests.post(LOCAL_AI_URL, json=payload, timeout=180)
    
    if response.status_code == 200:
        output_text = response.json()["choices"][0]["message"]["content"]
        
        print("\n================ AI RESPONSE ================")
        print(output_text)
        print("=============================================\n")
        
        with open("ai_output.txt", "w", encoding="utf-8") as f:
            f.write(output_text)
            
        print("[SUCCESS] AI output saved to ai_output.txt")
    else:
        print(f"[ERROR] Server returned Status Code: {response.status_code}")
        print(f"Details: {response.text}")
        sys.exit(1)

except Exception as e:
    print(f"[CRITICAL ERROR] Request failed: {e}")
    sys.exit(1)
