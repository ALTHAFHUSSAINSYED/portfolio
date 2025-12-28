"""
Model Configuration for Agentic Auto-Blogger
Defines specific free models for each role in the Agentic Chain.
"""

# Agentic Role Definitions
# Each role is assigned a primary free model and a reliable fallback.

AGENT_ROLES = {
    "orchestrator": {
        "role": "Outline & High-Level Logic",
        "primary": "tngtech/deepseek-r1t2-chimera:free",
        "fallback": "mistralai/mistral-7b-instruct:free",
        "max_tokens": 2000, 
        "temperature": 0.6
    },
    "drafter": {
        "role": "Section Writer (Chunked)",
        "primary": "meta-llama/llama-3.3-70b-instruct:free",
        "fallback": "mistralai/mistral-7b-instruct:free",
        "max_tokens": 1500,  # Increased for richer content
        "temperature": 0.7
    },
    "critic": {
        "role": "Quality Validator & Logic",
        "primary": "deepseek/deepseek-r1-0528:free",
        "fallback": "mistralai/mistral-7b-instruct:free",
        "max_tokens": 1000, 
        "temperature": 0.3
    },
    "polisher": {
        "role": "Final Style & tone",
        "primary": "nousresearch/hermes-3-llama-3.1-405b:free",
        "fallback": "meta-llama/llama-3.1-8b-instruct:free",
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
    "max_requests_per_minute": 20,  # Conservative for free tier
    "backoff_factor": 2,
    "initial_wait": 2
}
