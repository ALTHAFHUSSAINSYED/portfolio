# 🏗️ FINAL SYSTEM ARCHITECTURE (Dec 26, 2025)

## 📊 Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│              PORTFOLIO SYSTEM ARCHITECTURE               │
└─────────────────────────────────────────────────────────┘

┌──────────────────────┐         ┌──────────────────────┐
│   CHATBOT SYSTEM     │         │  AUTO-BLOGGER SYSTEM │
│                      │         │                      │
│  API: CHATBOT_NEW_KEY│         │  API: BLOG_KEY        │
│  Provider: OpenRouter│         │  Provider: OpenRouter│
└──────────────────────┘         └──────────────────────┘
         │                                  │
         │                                  │
    ┌────▼─────┐                       ┌────▼─────┐
    │ Mistral  │                       │ Mistral  │
    │   7B     │                       │   7B     │
    │ (Primary)│                       │ (Primary)│
    └──────────┘                       └──────────┘
         │                                  │
    ┌────▼─────┐                       ┌────▼─────┐
    │ Llama    │                       │ Gemma 2  │
    │  405B    │                       │   9B     │
    │(Fallback)│                       │(Fallback)│
    └──────────┘                       └──────────┘
```

---

## 💬 CHATBOT SYSTEM

### API Configuration
| Variable | Value | Purpose |
|----------|-------|---------|
| `CHATBOT_NEW_KEY` | `sk-or-v1-bdcbd5ad...` | **Dedicated** OpenRouter key for chatbot |
| `CHATBOT` | HuggingFace token | Tier 3 fallback (HF Gradio API) |
| `GEMINI_API_KEY` | Google API key | Tier 4 emergency fallback |

### Model Tier System

#### **Tier 1 - Primary (90% traffic)** ✅
- **Model**: `mistralai/mistral-7b-instruct:free`
- **Provider**: OpenRouter (via `CHATBOT_NEW_KEY`)
- **Max Tokens**: 150-450 (dynamic)
- **Why**: Most stable, fastest, proven reliable
- **Status**: Active ✅

#### **Tier 2 - Stable Fallback**
- **Model**: `google/gemma-2-9b-it:free`
- **Provider**: OpenRouter (via `CHATBOT_NEW_KEY`)
- **Max Tokens**: 150-450
- **Why**: Stable on free tier, better than 405B
- **Status**: Active fallback ✅

#### **Tier 3 - Secondary Fallback**
- **Model**: Llama 3.2 3B Instruct
- **Provider**: Hugging Face Gradio (via `CHATBOT` token)
- **Max Tokens**: 150-450
- **Why**: Independent provider, no OpenRouter dependency
- **Status**: Fallback only ✅

#### **Tier 4 - Emergency**
- **Model**: `models/gemini-2.5-flash`
- **Provider**: Google Gemini (via `GEMINI_API_KEY`)
- **Max Tokens**: 150-450
- **Why**: Paid, always available
- **Status**: Last resort ✅

### Chatbot Flow
```
User Query
    ↓
[Try Tier 1: Mistral 7B] ✅ 90% success
    ↓ (if fails)
[Try Tier 2: Llama 405B] ⚠️ Rate limited
    ↓ (if fails)
[Try Tier 3: HF Llama 3B] ✅ Independent
    ↓ (if fails)
[Try Tier 4: Gemini] ✅ Paid fallback
    ↓ (if all fail)
Error message to user
```

---

## 📝 AUTO-BLOGGER SYSTEM

### API Configuration
| Variable | Value | Purpose |
|----------|-------|---------|
| `BLOG_KEY` | `sk-or-v1-fb2f9e65...` | **Original** OpenRouter key for auto-blogger |
| `SERPER_API_KEY` | Serper.dev key | Web research (Google Search API) |

### Agent System (4 Agents)

#### **Agent 1 - Orchestrator (Blog Outliner)**
- **Role**: Creates blog structure and outline
- **Primary Model**: `mistralai/mistral-7b-instruct:free`
#### **Agent 1 - Orchestrator (The Architect)**
- **Role**: High-level planning, SEO strategy, and outline creation
- **Primary Model**: `deepseek/deepseek-r1:free` (Reasoning Specialist)
- **Fallback Model**: `thudm/glm-4-9b-chat:free`

---

#### **Agent 2 - Drafter (Section Writer)**
- **Role**: Writes each section (section-by-section loop)
- **Primary Model**: `mistralai/mistral-7b-instruct:free` (Proven Workhorse)
- **Fallback Model**: `mistralai/mistral-small-24b-instruct-2501:free`

---

#### **Agent 3 - Critic (Quality Validator)**
- **Role**: Evaluates blog quality, provides feedback
- **Primary Model**: `deepseek/deepseek-r1:free` (Strict Reasoning)
- **Fallback Model**: `tngtech/deepseek-r1t2-chimera:free`

---

#### **Agent 4 - Polisher (Style & Tone)**
- **Role**: Final refinement of writing style
- **Primary Model**: `cognitivecomputations/dolphin-mixtral-8x7b:free` (Human Tone)
- **Fallback Model**: `mistralai/mistral-small-24b-instruct-2501:free`
- **Max Tokens**: 1000
- **Status**: Active ✅

#### **Agent 5 - Researcher (No LLM)**
- **Role**: Gathers news, trends, sources
- **API**: SERPER API (via `SERPER_API_KEY`)
- **No AI model** - Direct Google Search API calls
- **Output**: JSON with headlines, snippets, sources
- **Status**: Active ✅

### Auto-Blogger Pipeline Flow
```
1. Researcher (SERPER API)
   ↓ (research_data)
   
2. Orchestrator (Mistral 7B)
   ↓ (outline: list of sections)
   
3. Drafter Loop (Mistral 7B)
   ├─ Section 1 → 5s delay
   ├─ Section 2 → 5s delay
   ├─ Section 3 → 5s delay
   └─ ... (6-8 sections total)
   ↓ (draft: complete blog)
   
4. Critic (Mistral 7B)
   ↓ (evaluation: pass/fail + score)
   
   [If score < 85] → Revision loop
   ├─ Drafter revises based on feedback
   └─ Critic re-evaluates
   
5. Polisher (Gemma 2 9B)
   ↓ (polished final version)
   
6. Publisher
   ├─ Save to generated_blogs/*.json
   └─ Embed to ChromaDB
```

---

## 🔑 Complete Environment Variables

### Chatbot-Specific
```bash
CHATBOT_NEW_KEY=<See .env file - OpenRouter API key for chatbot>
CHATBOT=<HuggingFace_Token>
GEMINI_API_KEY=<Google_API_Key>
```

### Auto-Blogger-Specific
```bash
BLOG_KEY=<See .env file - OpenRouter API key for auto-blogger>
SERPER_API_KEY=<See .env file - Serper API key for web research>
```

### Shared/System
```bash
MONGO_URI=<MongoDB_Connection_String>
EMAIL_ADDRESS=allualthaf42@gmail.com
CHROMA_API_KEY=<ChromaDB_Cloud_Key>
CHROMA_TENANT_ID=<Tenant_ID>
CHROMA_DATABASE=<Database_Name>
```

---

## 📊 Model Summary Table

| Model | Size | Strengths | Auto-Blogger Role |
|-------|------|-----------|-------------------|
| **DeepSeek R1T2** | 671B (MoE) | Reasoning | Orchestrator (Primary) |
| **DeepSeek R1-0528** | 671B (MoE) | Logic | Critic (Primary) |
| **Llama 3.3 70B** | 70B | Prose/Writing | Drafter (Primary) |
| **Hermes 3 405B** | 405B | Nuance/Tone | Polisher (Primary) |
| **Mistral 7B** | 7B | Reliability | Universal Fallback |

---

## 🎯 Key Benefits of Current Architecture

### 1. **Traffic Isolation** ✅
- Chatbot and Auto-blogger use **separate OpenRouter quotas**
- No rate limit conflicts
- Concurrent operation safe

### 2. **Reliability** ✅
- Chatbot: 4-tier fallback system
- Auto-blogger: Proven stable models (Mistral 7B)
- All free tier optimized

### 3. **Free Tier Compliance** ✅
- Max tokens: 600-1,000 (within limits)
- 5-second delays between requests
- Respects ~5-6 RPM limit

### 4. **Production Ready** ✅
- Error handling at every tier
- Graceful degradation
- User-facing reliability

---

## 🔄 Rate Limit Allocation

### Chatbot (CHATBOT_NEW_KEY)
- **RPM**: ~5-6 requests/min
- **TPM**: ~5,000-10,000 tokens/min
- **Usage**: Bursty, short requests
- **Priority**: HIGH (user-facing)

### Auto-Blogger (BLOG_KEY)
- **RPM**: ~5-6 requests/min
- **TPM**: ~5,000-10,000 tokens/min  
- **Usage**: Sustained, long generation
- **Priority**: LOW (background)

---

## 📝 Quick Reference

**Chatbot Primary**: Mistral 7B (`CHATBOT_NEW_KEY`)  
**Auto-Blogger Primary**: Mistral 7B (`BLOG_KEY`)  
**Research**: SERPER API (no LLM)  
**Isolation**: ✅ Complete (separate keys)  
**Status**: ✅ Production ready

**Last Updated**: December 26, 2025, 7:13 PM IST
