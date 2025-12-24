"""
Model Configuration
Tier-based model fallback configuration for auto-blogger.
UPDATED based on Benchmark Results: Gemini 2.5 Flash Lite is currently the performing model.
"""

# Active Models Structure
# Tier 1: Gemini 2.5 Flash Lite (Proven fast & working)
# Tier 2: Gemini 2.5 Flash (Slower but working)
# Tier 3+: OpenRouter candidates (Placeholder until keys/IDs fixed)

MODELS_CONFIG = [
    {
        "tier": 1,
        "provider": "gemini",
        "model_id": "gemini-2.0-flash-lite-preview-02-05",  # Updated to correct ID if needed, using generic alias for now
        "alias": "gemini-2.0-flash-lite-preview-02-05", # Flash Lite returned high TPM
        "name": "Gemini 2.5 Flash Lite",
        "max_tokens": 8192,
    },
    {
        "tier": 2,
        "provider": "gemini", 
        "model_id": "gemini-2.0-flash",
        "alias": "gemini-2.0-flash",
        "name": "Gemini 2.5 Flash",
        "max_tokens": 8192,
    },
     {
        "tier": 3,
        "provider": "gemini", 
        "model_id": "gemini-1.5-flash",
        "alias": "gemini-1.5-flash",
        "name": "Gemini 1.5 Flash", 
        "max_tokens": 8192,  # Fallback
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
