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
        "primary": "qwen/qwen3-235b-a22b-thinking-2507",  # Reasoning model for structured planning
        "fallback": "meta-llama/llama-3.3-70b-instruct:free",
        "max_tokens": 2000,
        "temperature": 0.3  # Lowered from 0.6 for more deterministic JSON output
    },
    "drafter": {
        "role": "Section Writer (Chunked)",
        "primary": "openai/gpt-oss-120b:free",  # Large model for content generation
        "fallback": "qwen/qwen3-coder:free",
        "max_tokens": 2500,  # Increased from 1500 to reduce cutoffs
        "temperature": 0.7
    },
    "critic": {
        "role": "Quality Validator & Logic",
        "primary": "meta-llama/llama-3.3-70b-instruct:free",  # Analysis & validation
        "fallback": "openai/gpt-oss-120b:free",
        "max_tokens": 1000,
        "temperature": 0.3
    },
    "polisher": {
        "role": "Final Style & tone",
        "primary": "qwen/qwen3-coder:free",  # Refinement & style
        "fallback": "openai/gpt-oss-120b:free",
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
