"""
Model Configuration for Agentic Auto-Blogger
Defines specific free models for each role in the Agentic Chain.
"""

# Agentic Role Definitions
# Each role is assigned a primary free model and a reliable fallback.

AGENT_ROLES = {
    "orchestrator": {
        "role": "Outline & High-Level Logic",
        "primary": "meta-llama/llama-3.1-405b-instruct:free",
        "fallback": "mistralai/mistral-7b-instruct:free",
        "max_tokens": 16000,
        "temperature": 0.7
    },
    "drafter": {
        "role": "Section Writer (Chunked)",
        "primary": "mistralai/mistral-7b-instruct:free",
        "fallback": "meta-llama/llama-3.1-8b-instruct:free",
        "max_tokens": 8192,
        "temperature": 0.75
    },
    "critic": {
        "role": "Quality Validator & Logic",
        "primary": "deepseek/deepseek-r1:free",
        "fallback": "meta-llama/llama-3.1-70b-instruct:free",
        "max_tokens": 16000,
        "temperature": 0.3
    },
    "polisher": {
        "role": "Final Style & tone",
        "primary": "google/gemma-2-9b-it:free",
        "fallback": "huggingfaceh4/zephyr-7b-beta:free",
        "max_tokens": 8192,
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
