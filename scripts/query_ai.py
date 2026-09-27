import sys
import requests
import time

user_prompt = sys.argv[1] if len(sys.argv) > 1 else "Hello, please confirm your status."
LOCAL_AI_URL = "http://127.0.0.1:8080/v1/chat/completions"

print("--- AI Server Status Check ---")
print("Waiting for AI server to load into RAM. This can take 5-10 minutes on a free GitHub runner...")

# Real User Logic: Ek normal user ki tarah hum patience rakhenge. 
# 120 baar check karega (har 5 second mein) = Total 10 Minutes wait time.
server_ready = False
for i in range(120):
    try:
        # Har 5 second me server ko 'ping' karke dekhega ki on hua ya nahi
        requests.get("http://127.0.0.1:8080/", timeout=2)
        server_ready = True
        print("\n[SUCCESS] AI Server is UP and running!")
        break
    except requests.exceptions.ConnectionError:
        print(f"Server is still loading... Waiting ({i+1}/120)")
        time.sleep(5)

if not server_ready:
    print("\n[ERROR] AI server did not start even after 10 minutes. Llamafile crashed or RAM is full.")
    sys.exit(1)

payload = {
    "messages": [
        {"role": "system", "content": "You are a highly capable AI assistant running locally on a GitHub Windows runner."},
        {"role": "user", "content": user_prompt}
    ],
    "temperature": 0.7,
    "max_tokens": 1000
}

print(f"\nSending prompt to Local AI: '{user_prompt}'")
print("Waiting for AI to generate response (this might take a few minutes)...")

try:
    # Timeout 15 minute (900 seconds) kar diya hai taaki AI aaram se lamba answer likh sake
    response = requests.post(LOCAL_AI_URL, json=payload, timeout=900)
    
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
