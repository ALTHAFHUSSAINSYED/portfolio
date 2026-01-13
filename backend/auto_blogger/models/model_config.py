"""
Model Configuration for Agentic Auto-Blogger
Defines specific free, stable models for each role in the Agentic Chain.
Strict adherence to "Free Tier Safe" policy.
Uses only validated OpenRouter model IDs.
"""

# Agentic Role Definitions
# Usage Strategy:
# 1. Primary: Stable, high-performance free models
# 2. Fallback: Smaller, predictable models (No frontier/huge models)

AGENT_ROLES = {
    "orchestrator": {
        "role": "Outline & High-Level Logic",
        "primary": "deepseek/deepseek-r1-0528:free",
        "fallback": "mistralai/mistral-small-3.1-24b-instruct:free",  # Changed from deepseek-r1t-chimera for diversity
        "max_tokens": 2000,
        "temperature": 0.3  # Lowered from 0.6 for more deterministic JSON output
    },
    "drafter": {
        "role": "Section Writer (Chunked)",
        "primary": "mistralai/mistral-small-3.1-24b-instruct:free",
        "fallback": "meta-llama/llama-3.2-3b-instruct:free",
        "max_tokens": 1500,
        "temperature": 0.7
    },
    "critic": {
        "role": "Quality Validator & Logic",
        "primary": "deepseek/deepseek-r1-0528:free",
        "fallback": "z-ai/glm-4.5-air:free",
        "max_tokens": 1000,
        "temperature": 0.3
    },
    "polisher": {
        "role": "Final Style & tone",
        "primary": "mistralai/mistral-small-3.1-24b-instruct:free",
        "fallback": "meta-llama/llama-3.2-3b-instruct:free",
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
