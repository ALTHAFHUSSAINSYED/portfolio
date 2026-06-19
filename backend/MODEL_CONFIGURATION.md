# Complete Model Configuration Overview

## 📊 System Architecture

Your portfolio uses **OpenRouter API** for all LLM interactions with a **multi-tier fallback system** for reliability.

---

## 🤖 AUTO-BLOGGER Models

**API Key Used**: `BLOG_KEY` (OpenRouter)  
**Purpose**: Generate 2,500-word technical blog posts

### Agent 1: Orchestrator (Blog Outliner)
**Role**: Creates blog structure and outline  
**Primary Model**: `deepseek/deepseek-r1-0528:free` (Reasoning Specialist)  
**Fallback Model**: `tngtech/deepseek-r1t-chimera:free`  
**Max Tokens**: 2000  
**Temperature**: 0.6

### Agent 2: Drafter (Section Writer)
**Role**: Writes each section of the blog (section by section)  
**Primary Model**: `mistralai/mistral-small-3.1-24b-instruct:free` (Proven Stability)  
**Fallback Model**: `meta-llama/llama-3.2-3b-instruct:free`  
**Max Tokens**: 1500  
**Temperature**: 0.7

### Agent 3: Critic (Quality Validator)
**Role**: Evaluates blog quality and provides feedback  
**Primary Model**: `deepseek/deepseek-r1-0528:free` (Strict Logic)  
**Fallback Model**: `z-ai/glm-4.5-air:free`  
**Max Tokens**: 1000  
**Temperature**: 0.3

### Agent 4: Polisher (Style & Tone)
**Role**: Final refinement of writing style  
**Primary Model**: `mistralai/mistral-small-3.1-24b-instruct:free` (Human Tone)  
**Fallback Model**: `meta-llama/llama-3.2-3b-instruct:free`  
**Max Tokens**: 1000  
**Temperature**: 0.6

### Agent 5: Researcher (No LLM)
**Role**: Gathers news and trends via web search  
**API**: SERPER API (`SERPER_API_KEY`)  
**No model used** - Direct Google Search API calls

---

## 💬 CHATBOT Models

**API Key Used**: `CHATBOT_KEY` (OpenRouter)  
**Purpose**: Answer portfolio questions with RAG (ChromaDB context)

### Tier 1: Primary (Fast & Reliable)
**Model**: `mistralai/mistral-7b-instruct:free`  
**Provider**: OpenRouter  
**Max Tokens**: 150-450 (dynamic based on query complexity)  
**Use Case**: 90%+ of queries  
**Status**: ✅ Most reliable on free tier

### Tier 2: Intelligent Fallback
**Model**: `meta-llama/llama-3.1-405b-instruct:free`  
**Provider**: OpenRouter  
**Max Tokens**: 150-450  
**Use Case**: When Tier 1 fails (rate limit, timeout)  
**Status**: ⚠️ Less stable on free tier (throttled)

### Tier 3: Hugging Face Fallback
**Model**: Llama 3.2 3B Instruct  
**Provider**: Hugging Face Gradio API (`CHATBOT` token)  
**Max Tokens**: 150-450  
**Use Case**: When OpenRouter fails completely  
**Status**: ✅ Secondary backup

### Tier 4: Emergency Fallback
**Model**: `models/gemini-2.5-flash`  
**Provider**: Google Gemini API (`GEMINI_API_KEY`)  
**Max Tokens**: 150-450  
**Use Case**: Last resort when all else fails  
**Status**: ✅ Always available (paid key)

---

## 📋 Complete Model List

### All Models Used (Alphabetical)

| Model Name | Provider | Component | Role | Tier/Agent |
|------------|----------|-----------|------|-----------|
| `gemma-2-9b-it:free` | Google (via OpenRouter) | Auto-blogger | Polisher Primary, Fallback for others | Agent 4, Fallback 1-3 |
| `gemini-2.5-flash` | Google Direct | Chatbot | Emergency Fallback | Tier 4 |
| `llama-3.1-405b-instruct:free` | Meta (via OpenRouter) | Chatbot | Intelligent Fallback | Tier 2 |
| `llama-3.2-3b-instruct` | Meta (via Hugging Face) | Chatbot | Secondary Fallback | Tier 3 |
| `mistral-7b-instruct:free` | Mistral AI (via OpenRouter) | Auto-blogger & Chatbot | Primary for all agents | Agent 1-3, Tier 1 |

---

## 🔑 API Keys Required

| Environment Variable | Service | Used By | Status |
|---------------------|---------|---------|--------|
| `BLOG_KEY` | OpenRouter | Auto-blogger + Chatbot | ✅ SET |
| `SERPER_API_KEY` | Serper.dev (Google) | Auto-blogger Research | ✅ SET |
| `CHATBOT` | Hugging Face | Chatbot Tier 3 | ✅ SET |
| `GEMINI_API_KEY` | Google Gemini | Chatbot Tier 4 | ✅ SET |

---

## ⚡ Model Selection Logic

### Auto-Blogger Flow
```
1. Orchestrator (Mistral 7B) → Outline
   ↓ (if fails)
   Fallback → Gemma 2 9B

2. Drafter (Mistral 7B) → Section 1
   ↓ (if fails)
   Fallback → Gemma 2 9B
   
   ... repeat for each section ...

3. Critic (Mistral 7B) → Evaluation
   ↓ (if fails)
   Fallback → Gemma 2 9B

4. Polisher (Gemma 2 9B) → Final styling
   ↓ (if fails)
   Fallback → Mistral 7B
```

### Chatbot Flow
```
User Query → Tier 1 (Mistral 7B)
   ↓ (if fails)
Tier 2 (Llama 405B)
   ↓ (if fails)
Tier 3 (HF Llama 3.2 3B)
   ↓ (if fails)
Tier 4 (Gemini 2.5 Flash)
   ↓ (if all fail)
Error Message
```

---

## 📊 Token Limits & Rate Limits

### Auto-Blogger (per section)
- **Orchestrator**: 1,000 tokens
- **Drafter**: 600 tokens per section
- **Critic**: 800 tokens
- **Polisher**: 600 tokens
- **Delay**: 5 seconds between sections

### Chatbot (per query)
- **Simple queries**: 150 tokens
- **Complex queries**: 450 tokens
- **No artificial delay** (single request)

### OpenRouter Free Tier Limits (Estimated)
- **RPM**: ~5-6 requests/minute
- **TPM**: ~5,000-10,000 tokens/minute
- **Output cap**: ~500-1,000 tokens per request
- **Daily limit**: ~50-100 requests

---

## 🎯 Why Mistral 7B for Everything?

**Decision Rationale:**
1. ✅ **Proven Stability**: Works reliably on free tier
2. ✅ **Used in Chatbot**: Already battle-tested
3. ✅ **Higher Token Allowance**: ~1,500-2,000 vs 500-1,000
4. ✅ **Better Availability**: More replicas, less throttling
5. ✅ **Consistent Quality**: Good for technical content

**Previous Issues with Llama 405B:**
- ❌ Strict rate limiting (only ~500 tokens output)
- ❌ Frequent throttling (few replicas)
- ❌ Silently returned None
- ❌ Unreliable on free tier

---

## 📝 Model Capabilities

### Mistral 7B Instruct
- **Parameters**: 7 billion
- **Context**: 8,192 tokens (8K)
- **Best for**: Instructions, Q&A, technical writing
- **Free tier**: ✅ Very stable
- **Cost (paid)**: ~$0.00025/request

### Gemma 2 9B IT
- **Parameters**: 9 billion
- **Context**: 8,192 tokens
- **Best for**: General chat, creative tasks
- **Free tier**: ✅ Stable
- **Cost (paid)**: ~$0.0003/request

### Llama 3.1 405B Instruct
- **Parameters**: 405 billion
- **Context**: 131,072 tokens (131K!)
- **Best for**: Complex reasoning, long context
- **Free tier**: ⚠️ Heavily throttled
- **Cost (paid)**: ~$0.005/request

### Gemini 2.5 Flash
- **Parameters**: Unknown (proprietary)
- **Context**: ~1,000,000 tokens (1M!)
- **Best for**: Multimodal, long context
- **Free tier**: ❌ Not available
- **Cost (paid)**: ~$0.00015/request

---

## 🔧 Configuration Files

- **Auto-blogger**: [`backend/auto_blogger/models/model_config.py`](file:///c:/portfolio/portfolio/backend/auto_blogger/models/model_config.py)
- **Chatbot**: [`backend/chatbot_provider.py`](file:///c:/portfolio/portfolio/backend/chatbot_provider.py)

---

## ✅ Current Status

**Auto-Blogger**: Using Mistral 7B → Fixed and ready to test  
**Chatbot**: Using Mistral 7B → ✅ Working perfectly  
**All fallbacks configured**: ✅ Multi-tier reliability  
**Free tier optimized**: ✅ Respects rate limits
