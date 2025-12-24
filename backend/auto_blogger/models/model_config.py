"""
Model Configuration
Tier-based model fallback configuration for auto-blogger.
"""

# Active Models Structure
# Tier 1: Llama 3.1 8B (OpenRouter) - Backup/Primary when Gemini Quota Exhausted
# Tier 2: Gemini 2.5 Flash Lite
# Tier 3: Gemini 2.5 Flash
# Tier 4: Gemini 1.5 Flash

MODELS_CONFIG = [
    {
        "tier": 1,
        "provider": "openrouter",
        "model_id": "meta-llama/llama-3.1-8b-instruct",
        "name": "Llama 3.1 8B (OpenRouter)",
        "max_tokens": 8192,
    },
    {
        "tier": 2,
        "provider": "gemini",
        "model_id": "gemini-2.0-flash-lite-preview-02-05", 
        "alias": "gemini-2.0-flash-lite", 
        "name": "Gemini 2.5 Flash Lite",
        "max_tokens": 8192,
    },
    {
        "tier": 3,
        "provider": "gemini", 
        "model_id": "gemini-2.0-flash",
        "alias": "gemini-2.0-flash",
        "name": "Gemini 2.5 Flash",
        "max_tokens": 8192,
    },
     {
        "tier": 4,
        "provider": "gemini", 
        "model_id": "gemini-1.5-flash",
        "alias": "gemini-1.5-flash",
        "name": "Gemini 1.5 Flash", 
        "max_tokens": 8192,
    }
]

# Benchmark Weights
BENCHMARK_CRITERIA = {
    "quality_weight": 0.4,
    "speed_weight": 0.2,
    "rpm_weight": 0.2, 
    "tpm_weight": 0.2,
}

BLOG_SPECS = {
    "target_word_count": 2500,
    "min_word_count": 2400,
    "max_word_count": 2600,
    "target_tokens": 3500,
}
