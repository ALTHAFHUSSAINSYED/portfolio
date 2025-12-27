import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

KEYS = {
    "Auto-Blogger (CHATBOT_KEY)": os.getenv("CHATBOT_KEY"),
    "Chatbot (CHATBOT_NEW_KEY)": os.getenv("CHATBOT_NEW_KEY")
}

def check_credits():
    print("\n🔍 OpenRouter API Credit Check\n" + "="*40)
    
    for name, key in KEYS.items():
        if not key:
            print(f"❌ {name}: Key NOT FOUND in environment")
            continue
            
        masked = key[:8] + "..." if key else "None"
        print(f"🔑 Testing {name} [{masked}]")
        
        try:
            # OpenRouter standard auth check endpoint
            resp = requests.get(
                "https://openrouter.ai/api/v1/auth/key",
                headers={"Authorization": f"Bearer {key}"},
                timeout=10
            )
            
            if resp.status_code == 200:
                data = resp.json().get("data", {})
                limit = data.get("usage", 0)
                limit_label = data.get("limit")
                
                # Note: OpenRouter structure might vary, but /auth/key usually returns key info
                print(f"   ✅ STATUS: Active (200 OK)")
                print(f"   📊 Raw Response: {json.dumps(data, indent=2)}")
            elif resp.status_code == 401:
                print(f"   ❌ STATUS: Unauthorized (401) - Invalid Key")
            elif resp.status_code == 429:
                print(f"   ⚠️ STATUS: Rate Limited (429) - Quota Exceeded")
            else:
                print(f"   ❓ STATUS: {resp.status_code} - {resp.text}")
                
        except Exception as e:
            print(f"   💥 Error: {e}")
        print("-" * 40)

if __name__ == "__main__":
    check_credits()
