"""
Model Configuration for Agentic Auto-Blogger
Defines specific free, stable models for each role in the Agentic Chain.
Strict adherence to "Free Tier Safe" policy.
"""

# Agentic Role Definitions
# Usage Strategy:
# 1. Primary: Stable, high-performance free models
# 2. Fallback: Smaller, predictable models (No frontier/huge models)

AGENT_ROLES = {
    "orchestrator": {
        "role": "Outline & High-Level Logic",
        "primary": "deepseek/deepseek-chat:free", # DeepSeek Chat (valid model)
        "fallback": "thudm/glm-4-9b-chat:free", # GLM 4.5 Air equivalent
        "max_tokens": 2000, 
        "temperature": 0.6
    },
    "drafter": {
        "role": "Section Writer (Chunked)",
        "primary": "mistralai/mistral-7b-instruct:free", # Proven workhorse
        "fallback": "mistralai/mistral-small-24b-instruct-2501:free", # Stable small model
        "max_tokens": 1500,
        "temperature": 0.7
    },
    "critic": {
        "role": "Quality Validator & Logic",
        "primary": "deepseek/deepseek-chat:free", # Strong logic
        "fallback": "tngtech/deepseek-r1t2-chimera:free", # R1T Chimera
        "max_tokens": 1000, 
        "temperature": 0.3
    },
    "polisher": {
        "role": "Final Style & tone",
        "primary": "cognitivecomputations/dolphin-mixtral-8x7b:free", # Best proxy for Dolphin 24B
        "fallback": "mistralai/mistral-small-24b-instruct-2501:free",
        "max_tokens": 1000,
        "temperature": 0.6
    }
}

# General Settings
BLOG_SPECS = {
    "target_word_count": 2500,
    "min_word_count": 2200,
    "max_word_count": 2800,
    "target_tokens": 3500,
    "max_retries": 3,
    "retry_delay": 5,  # seconds
}

# Rate Limit Config (Simple backoff strategy)
RATE_LIMIT_CONFIG = {
    "max_requests_per_minute": 10,  # Conservative for free tier
    "backoff_factor": 2,
    "initial_wait": 3
}
