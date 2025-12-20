import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_openrouter():
    print("--- Diagnostic: OpenRouter API Test ---")
    
    # 1. Check if keys exist
    api_key_str = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENROUTER_API_KEYS")
    if not api_key_str:
        print("[ERROR] No OPENROUTER_API_KEY or OPENROUTER_API_KEYS found in .env")
        return

    keys = [k.strip() for k in api_key_str.split(",") if k.strip()]
    print(f"[INFO] Found {len(keys)} API Key(s)")

    # 2. Test each key
    for i, key in enumerate(keys):
        print(f"\nTesting Key #{i+1}: {key[:6]}...{key[-4:]}")
        
        headers = {
            "Authorization": f"Bearer {key}",
            "HTTP-Referer": "http://localhost:8000",
            "X-Title": "ResearchPilot Debug",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "mistralai/mistral-7b-instruct:free", # Use a free model for testing if possible, or a cheap one
            "messages": [{"role": "user", "content": "Test connection. Reply with 'OK'."}]
        }
        
        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=10
            )
            
            print(f"Status Code: {response.status_code}")
            if response.status_code == 200:
                print("[SUCCESS] API responded successfully.")
                print(f"Response: {response.json()['choices'][0]['message']['content']}")
            else:
                print(f"[FAILURE] API returned error: {response.text}")
                
        except Exception as e:
            print(f"[ERROR] Connection failed: {e}")

if __name__ == "__main__":
    test_openrouter()
