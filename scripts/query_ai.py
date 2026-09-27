import sys
import requests
import time

user_prompt = sys.argv[1] if len(sys.argv) > 1 else "Hello, please confirm you are active."
LOCAL_AI_URL = "http://127.0.0.1:8080/v1/chat/completions"

print("--- AI Server Status Check ---")
print("Waiting for AI server to load into RAM (isme 1-2 minute lag sakte hain)...")

# Logic: AI server start hone ka wait karega (Max 3 minute)
server_ready = False
for i in range(36):  # 36 * 5 = 180 seconds (3 mins) wait time
    try:
        # Check if local server is responding
        requests.get("http://127.0.0.1:8080/", timeout=2)
        server_ready = True
        print("\n🟢 SUCCESS: AI Server is UP and running!")
        break
    except requests.exceptions.ConnectionError:
        print(f"Server abhi load ho raha hai... Wait kar rahe hain ({i+1}/36)")
        time.sleep(5)

if not server_ready:
    print("\n🔴 ERROR: AI server start nahi hua. Llamafile crash ho gaya hoga ya RAM full ho gayi hogi.")
    sys.exit(1)

payload = {
    "messages": [
        {"role": "system", "content": "You are a helpful AI assistant running locally."},
        {"role": "user", "content": user_prompt}
    ],
    "temperature": 0.7,
    "max_tokens": 1000
}

print(f"\nSending prompt to AI: '{user_prompt}'")
print("AI ka response likhne ka wait kar rahe hain...\n")

try:
    # Timeout 600 seconds (10 minute) diya hai taaki AI aaram se soch kar likh sake
    response = requests.post(LOCAL_AI_URL, json=payload, timeout=600)
    
    # Check karega ki Response sahi (200 OK) aaya hai ya nahi
    if response.status_code == 200:
        output_text = response.json()["choices"][0]["message"]["content"]
        
        print("================ AI RESPONSE ================")
        print(output_text)
        print("=============================================\n")
        
        with open("ai_output.txt", "w", encoding="utf-8") as f:
            f.write(output_text)
        print("🟢 SUCCESS: AI output 'ai_output.txt' me save ho gaya hai.")
        
    else:
        print(f"🔴 ERROR: Server ne error diya. Status Code: {response.status_code}")
        print(f"Error Details: {response.text}")
        sys.exit(1)

except Exception as e:
    print(f"🔴 CRITICAL ERROR: Request fail ho gayi. Reason: {e}")
    sys.exit(1)
