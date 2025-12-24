import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

OPENROUTER_API_KEY = os.getenv("CHATBOT_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/models"

import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

OPENROUTER_API_KEY = os.getenv("CHATBOT_KEY") or os.getenv("OPENROUTER_API_KEY")
BASE_URL = "https://openrouter.ai/api/v1"

def list_free_models():
    """
    Calls OpenRouter's model list endpoint and returns free models.
    Filters by ':free' suffix or explicit zero pricing.
    """
    if not OPENROUTER_API_KEY:
        print("❌ Error: CHATBOT_KEY/OPENROUTER_API_KEY not found in environment.")
        return []

    url = f"{BASE_URL}/models"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://portfolio-site.com", # Required for some free models
        "X-Title": "Auto-Blogger"
    }

    try:
        print(f"📡 Connecting to OpenRouter API...")
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            print(f"❌ Error listing models: {response.status_code} - {response.text}")
            return []

        all_models = response.json().get("data", [])
        free_models = []

        print(f"✅ Fetched {len(all_models)} total models. Filtering...")

        for model in all_models:
            model_id = model.get("id") or model.get("name")
            if not model_id:
                continue

            # logic: ID ends with ":free" OR pricing is zero
            is_free_id = ":free" in model_id.lower()
            
            pricing = model.get("pricing", {})
            p_prompt = pricing.get("prompt")
            p_comp = pricing.get("completion")
            
            # Check if pricing is explicitly '0' or 0 (some API return strings, some numbers)
            # Safe check: convert to float if possible
            try:
                is_zero_price = (float(p_prompt) == 0.0 and float(p_comp) == 0.0)
            except (ValueError, TypeError):
                is_zero_price = False

            if is_free_id or is_zero_price:
                free_models.append({
                    "id": model_id,
                    "name": model.get("name", model_id),
                    "context_length": model.get("context_length", "Unknown"),
                    "description": model.get("description", "")
                })

        # Sort by context length (descending)
        def get_ctx(m):
            try:
                return int(m["context_length"])
            except:
                return 0
        free_models.sort(key=get_ctx, reverse=True)

        return free_models

    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        return []

def main():
    fm = list_free_models()
    if not fm:
        print("⚠️ No free models detected via API.")
        return

    print(f"\n🎉 Detected {len(fm)} free models available to your key:\n")
    print(f"{'Model ID':<50} | {'Context':<10} | {'Name'}")
    print("-" * 100)
    
    for idx, m in enumerate(fm, 1):
        desc = m['description'][:60] + "..." if m['description'] else ""
        print(f"{idx}. {m['id']:<45} | {m['context_length']:<10} | {m['name']}")
        # print(f"   Description: {desc}") 

    print("\n\n🧠 Recommended for Agentic Workflow:")
    print("-------------------------------------")
    # Heuristics for recommendations
    large_ctx = [m['id'] for m in fm if get_ctx(m) >= 32000]
    reasoning = [m['id'] for m in fm if 'deepseek' in m['id'].lower() or 'reason' in m['id'].lower()]
    instruct = [m['id'] for m in fm if 'instruct' in m['id'].lower() or 'chat' in m['id'].lower()]

    print(f"🔹 Long Context (Drafting): {large_ctx[:3]}")
    print(f"🔹 Reasoning (Logic/Critic): {reasoning[:3]}")
    print(f"🔹 Instruct/Chat (Polishing): {instruct[:3]}")

def get_ctx(m):
    try:
        return int(m["context_length"])
    except:
        return 0

if __name__ == "__main__":
    main()
