import sys
import requests
import json
import time

# GitHub (या दूसरे Repo) से भेजा गया प्रॉम्प्ट रिसीव करना
user_prompt = sys.argv[1] if len(sys.argv) > 1 else "Hello, give me a short fact about AI."

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
    # लोकल सर्वर से जवाब मांगना
    response = requests.post(LOCAL_AI_URL, json=payload, timeout=300)
    response.raise_for_status() # HTTP एरर चेक करने के लिए
    
    output_text = response.json()["choices"][0]["message"]["content"]
    
    # आउटपुट को कंसोल में प्रिंट करना
    print("\n--- AI Response ---")
    print(output_text)
    print("-------------------\n")
    
    # रिस्पॉन्स को ai_output.txt में सेव करना
    with open("ai_output.txt", "w", encoding="utf-8") as f:
        f.write(output_text)
        
    print("Success! AI output saved to ai_output.txt")

except requests.exceptions.RequestException as e:
    print(f"Error connecting to local server. Make sure the server is fully loaded. Error: {e}")
