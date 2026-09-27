import sys
import requests
import json
import time

# GitHub se bheja gaya prompt receive karna
user_prompt = sys.argv[1] if len(sys.argv) > 1 else "Hello, please confirm you are active."

LOCAL_AI_URL = "http://127.0.0.1:8080/v1/chat/completions"

payload = {
    "messages": [
        {"role": "system", "content": "You are a highly capable AI assistant running locally on a GitHub Windows runner."},
        {"role": "user", "content": user_prompt}
    ],
    "temperature": 0.7,
    "max_tokens": 1000
}

print(f"Sending prompt to Local AI: '{user_prompt}'")

try:
    # Local server ko request bhejna
    response = requests.post(LOCAL_AI_URL, json=payload, timeout=300)
    response.raise_for_status()
    
    output_text = response.json()["choices"][0]["message"]["content"]
    
    print("\n--- AI Response ---")
    print(output_text)
    print("-------------------\n")
    
    # Response ko txt file me save karna
    with open("ai_output.txt", "w", encoding="utf-8") as f:
        f.write(output_text)
        
    print("Success! AI output saved to ai_output.txt")

except requests.exceptions.RequestException as e:
    print(f"Error connecting to local server. Make sure the server is fully loaded. Error: {e}")
