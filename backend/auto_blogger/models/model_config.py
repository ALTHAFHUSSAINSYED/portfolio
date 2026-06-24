"""
Model Configuration for Agentic Auto-Blogger
Defines specific free, stable models for each role in the Agentic Chain.
Strict adherence to "Free Tier Safe" policy.
Uses only validated OpenRouter model IDs.
"""

import os
import json
import logging
from dataclasses import dataclass

logger = logging.getLogger("ModelRegistry")

@dataclass
class AgentConfig:
    role: str
    primary: str
    fallback: str
    max_tokens: int
    temperature: float
    max_retries: int = 2
    timeout_seconds: int = 90
    enabled: bool = True

    def __getitem__(self, key):
        try:
            return getattr(self, key)
        except AttributeError:
            raise KeyError(key)
            
    def get(self, key, default=None):
        return getattr(self, key, default)

class AgentModelRegistry:
    def __init__(self, default_roles):
        self.default_roles = default_roles
        self.config_path = "/app/backend/logs/auto_blogger/dynamic_model_config.json"
        self._cached_config = {}
        self._last_mtime = 0
        self._promoted_overrides = {}
        
        self.REQUIRED_AGENTS = [
            "orchestrator",
            "researcher_summarizer",
            "drafter",
            "critic",
            "polisher"
        ]

    def _load_dynamic_config(self):
        if os.path.exists(self.config_path):
            try:
                mtime = os.path.getmtime(self.config_path)
                if mtime != self._last_mtime:
                    with open(self.config_path, 'r', encoding='utf-8') as f:
                        raw_data = json.load(f)
                    
                    validated = self._validate_and_parse(raw_data)
                    if validated:
                        self._cached_config = validated
                        self._last_mtime = mtime
                        logger.info("♻️ Dynamic model configuration successfully loaded & cached.")
            except Exception as e:
                logger.warning(f"⚠️ Failed to load dynamic config: {e}. Using defaults/cached version.")
        
        merged = {}
        for key in self.REQUIRED_AGENTS:
            default_val = self.default_roles[key]
            dynamic_val = self._cached_config.get(key, {})
            
            resolved_primary = dynamic_val.get("primary") or default_val["primary"]
            resolved_fallback = dynamic_val.get("fallback") or default_val["fallback"]
            
            if key in self._promoted_overrides:
                resolved_primary = self._promoted_overrides[key]
                
            merged[key] = AgentConfig(
                role=dynamic_val.get("role") or default_val["role"],
                primary=resolved_primary,
                fallback=resolved_fallback,
                max_tokens=dynamic_val.get("max_tokens") or default_val["max_tokens"],
                temperature=dynamic_val.get("temperature") or default_val["temperature"],
                max_retries=dynamic_val.get("max_retries") or default_val.get("max_retries", 2),
                timeout_seconds=dynamic_val.get("timeout_seconds") or default_val.get("timeout_seconds", 90),
                enabled=dynamic_val.get("enabled") if dynamic_val.get("enabled") is not None else default_val.get("enabled", True)
            )
        return merged

    def _validate_and_parse(self, data) -> dict:
        if not isinstance(data, dict):
            logger.error("Dynamic config root must be a JSON object.")
            return {}
            
        agents_data = data.get("agents")
        if not agents_data or not isinstance(agents_data, dict):
            logger.error("Dynamic config must contain an 'agents' dictionary.")
            return {}
            
        for key in self.REQUIRED_AGENTS:
            if key not in agents_data:
                logger.error(f"Missing required agent config for '{key}' in dynamic config.")
                return {}
            agent_cfg = agents_data[key]
            if not isinstance(agent_cfg, dict) or not agent_cfg.get("primary"):
                logger.error(f"Invalid primary model for agent '{key}' in dynamic config.")
                return {}
                
        return agents_data

    def __getitem__(self, key) -> AgentConfig:
        config = self._load_dynamic_config()
        if key not in config:
            raise KeyError(key)
        return config[key]
        
    def get(self, key, default=None) -> AgentConfig:
        try:
            return self[key]
        except KeyError:
            return default

    def _save_healed_config(self, key, healed_primary, healed_fallback):
        """
        Write the promoted primary and fallback model configuration back to the JSON file on disk,
        so that it survives container restarts, EC2 reboots, and redeployments.
        """
        raw_data = {"version": 1, "last_updated": "", "agents": {}}
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    raw_data = json.load(f)
            except Exception:
                pass
                
        if "agents" not in raw_data or not isinstance(raw_data["agents"], dict):
            raw_data["agents"] = {}
            
        agent_data = raw_data["agents"].get(key, {})
        default_val = self.default_roles[key]
        
        raw_data["agents"][key] = {
            "role": agent_data.get("role") or default_val["role"],
            "primary": healed_primary,
            "fallback": healed_fallback,
            "max_tokens": agent_data.get("max_tokens") or default_val["max_tokens"],
            "temperature": agent_data.get("temperature") or default_val["temperature"],
            "max_retries": agent_data.get("max_retries") or default_val.get("max_retries", 2),
            "timeout_seconds": agent_data.get("timeout_seconds") or default_val.get("timeout_seconds", 90),
            "enabled": agent_data.get("enabled") if agent_data.get("enabled") is not None else default_val.get("enabled", True)
        }
        
        from datetime import datetime
        raw_data["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S IST")
        
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(raw_data, f, indent=2)
            logger.info(f"💾 Healed model config saved to disk for agent '{key}': {healed_primary} <-> {healed_fallback}")
            self._cached_config[key] = raw_data["agents"][key]
            self._last_mtime = os.path.getmtime(self.config_path)
        except Exception as e:
            logger.error(f"Failed to persist healed model config: {e}")

    def promote_fallback(self, key):
        """
        Promote the fallback model of an agent to primary and demote primary to fallback.
        Updates memory cache and persists to disk.
        """
        config = self.get(key)
        if not config or not config.fallback:
            logger.warning(f"Cannot promote fallback for '{key}': no fallback model configured.")
            return
        
        new_primary = config.fallback
        new_fallback = config.primary
        logger.warning(f"🔄 Promoting fallback model '{new_primary}' to primary for agent '{key}'")
        self._promoted_overrides[key] = new_primary
        self._save_healed_config(key, new_primary, new_fallback)

    def validate_and_heal(self, client):
        """
        Validate all primary models on startup or runtime trigger.
        Promotes fallback models if primary endpoints fail.
        """
        import time
        logger.info("🩺 Starting model validation and self-healing check...")
        
        self._load_dynamic_config()
        
        for agent in self.REQUIRED_AGENTS:
            config = self.get(agent)
            
            if not config.enabled:
                logger.info(f"⏭️ Skipping validation for disabled agent '{agent}'")
                continue
                
            model_id = config.primary
            
            if "gemini" in model_id.lower() or ("google" in model_id.lower() and not ":free" in model_id):
                logger.info(f"⏭️ Skipping validation for direct/paid model: {model_id}")
                continue
                
            logger.info(f"Checking primary model for '{agent}': {model_id}...")
            
            try:
                client.chat.completions.create(
                    model=model_id,
                    messages=[{"role": "user", "content": "ping"}],
                    max_tokens=2,
                    timeout=config.timeout_seconds
                )
                logger.info(f"✅ Model {model_id} is healthy.")
            except Exception as e:
                logger.warning(f"⚠️ Primary model {model_id} failed validation: {e}")
                if config.fallback:
                    logger.warning(f"🔄 Promoting fallback model '{config.fallback}' to primary for agent '{agent}'")
                    new_primary = config.fallback
                    new_fallback = config.primary
                    
                    self._promoted_overrides[agent] = new_primary
                    self._save_healed_config(agent, new_primary, new_fallback)
                else:
                    logger.error(f"❌ No fallback model configured for agent '{agent}'")
            
            time.sleep(2)
        
        logger.info("🩺 Model validation and self-healing check complete.")

# Agentic Role Definitions (with recommended Multi-Agent Architecture defaults)
DEFAULT_AGENT_ROLES = {
    "orchestrator": {
        "role": "Outline & High-Level Logic",
        "primary": "qwen/qwen3-next-80b-a3b-instruct:free",
        "fallback": "meta-llama/llama-3.3-70b-instruct:free",
        "max_tokens": 2000,
        "temperature": 0.3,
        "max_retries": 2,
        "timeout_seconds": 90,
        "enabled": True
    },
    "researcher_summarizer": {
        "role": "Research Synthesis & Summarization",
        "primary": "openai/gpt-oss-120b:free",
        "fallback": "qwen/qwen3-next-80b-a3b-instruct:free",
        "max_tokens": 2000,
        "temperature": 0.5,
        "max_retries": 2,
        "timeout_seconds": 90,
        "enabled": True
    },
    "drafter": {
        "role": "Section Writer (Chunked)",
        "primary": "openai/gpt-oss-120b:free",
        "fallback": "meta-llama/llama-3.3-70b-instruct:free",
        "max_tokens": 2500,
        "temperature": 0.7,
        "max_retries": 2,
        "timeout_seconds": 90,
        "enabled": True
    },
    "critic": {
        "role": "Quality Validator & Logic",
        "primary": "meta-llama/llama-3.3-70b-instruct:free",
        "fallback": "openai/gpt-oss-120b:free",
        "max_tokens": 1000,
        "temperature": 0.3,
        "max_retries": 2,
        "timeout_seconds": 90,
        "enabled": True
    },
    "polisher": {
        "role": "Final Style & Tone",
        "primary": "qwen/qwen3-next-80b-a3b-instruct:free",
        "fallback": "meta-llama/llama-3.3-70b-instruct:free",
        "max_tokens": 1000,
        "temperature": 0.6,
        "max_retries": 2,
        "timeout_seconds": 90,
        "enabled": True
    }
}

AGENT_ROLES = AgentModelRegistry(DEFAULT_AGENT_ROLES)

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

def run_agent_completion(client, agent_key: str, messages: list, max_tokens: int = None, temperature: float = None) -> str:
    """
    Run chat completion for a given agent.
    Handles timeout, retries, cost tracking logging, and runtime fallback promotion.
    """
    import time
    
    config = AGENT_ROLES[agent_key]
    primary_model = config.primary
    fallback_model = config.fallback
    
    models_to_try = [primary_model]
    if fallback_model and primary_model != fallback_model:
        models_to_try.append(fallback_model)
        
    last_error = None
    for idx, model_id in enumerate(models_to_try):
        is_primary = (idx == 0)
        # Use config.max_retries for primary, otherwise 1 retry
        max_retries = config.max_retries if is_primary else 1
        attempts = max_retries + 1
        
        for attempt in range(attempts):
            logger.info(f"Calling model {model_id} for agent '{agent_key}' (attempt {attempt + 1}/{attempts})...")
            try:
                start_time = time.time()
                response = client.chat.completions.create(
                    model=model_id,
                    messages=messages,
                    max_tokens=max_tokens or config.max_tokens,
                    temperature=temperature if temperature is not None else config.temperature,
                    timeout=config.timeout_seconds
                )
                latency = time.time() - start_time
                content = response.choices[0].message.content
                
                # Retrieve tokens safely
                prompt_tokens = getattr(response.usage, "prompt_tokens", 0) if response.usage else 0
                completion_tokens = getattr(response.usage, "completion_tokens", 0) if response.usage else 0
                
                # Log cost tracker block exactly as requested:
                logger.info(
                    f"\nAgent: {agent_key}\n"
                    f"Model: {model_id}\n"
                    f"Input Tokens: {prompt_tokens}\n"
                    f"Output Tokens: {completion_tokens}\n"
                    f"Latency: {latency:.2f}s\n"
                )
                
                return content
            except Exception as e:
                last_error = e
                logger.warning(f"Error calling model {model_id} on attempt {attempt + 1}: {e}")
                if attempt < attempts - 1:
                    sleep_time = 2 ** (attempt + 1)
                    logger.info(f"Retrying in {sleep_time}s...")
                    time.sleep(sleep_time)
                else:
                    if is_primary and fallback_model:
                        try:
                            AGENT_ROLES.promote_fallback(agent_key)
                        except Exception as pe:
                            logger.error(f"Failed to promote fallback for agent '{agent_key}': {pe}")
    # Attempt direct Gemini API fallback before giving up completely
    logger.warning(f"⚠️ All OpenRouter models failed for agent '{agent_key}'. Attempting direct Gemini API fallback...")
    try:
        try:
            from backend.gemini_service import GeminiClient
        except ImportError:
            try:
                from gemini_service import GeminiClient
            except ImportError:
                import sys
                import os
                sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
                from backend.gemini_service import GeminiClient
        
        gemini_client = GeminiClient()
        if gemini_client.is_available:
            # Use gemini-2.5-flash as the fallback model for direct Gemini (gemini-2.5-pro has 0 quota on free tier keys)
            fallback_gemini_model = "gemini-2.5-flash"
                
            logger.info(f"🚀 Direct Gemini Client initialized. Calling model '{fallback_gemini_model}' for agent '{agent_key}'...")
            start_time = time.time()
            response = gemini_client.chat.completions.create(
                model=fallback_gemini_model,
                messages=messages,
                max_tokens=max_tokens or config.max_tokens,
                temperature=temperature if temperature is not None else config.temperature,
                timeout=config.timeout_seconds
            )
            latency = time.time() - start_time
            content = response.choices[0].message.content
            
            logger.info(
                f"\n[Direct Gemini Fallback Success]\n"
                f"Agent: {agent_key}\n"
                f"Model: {fallback_gemini_model}\n"
                f"Latency: {latency:.2f}s\n"
            )
            return content
        else:
            logger.error("Direct Gemini API is not available (is_available = False).")
    except Exception as gemini_err:
        logger.error(f"❌ Direct Gemini API fallback failed: {gemini_err}")
        
    raise RuntimeError(f"All models failed for agent '{agent_key}'. Last error: {last_error}")

