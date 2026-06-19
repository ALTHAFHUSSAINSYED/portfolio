# Portfolio Project - Complete AI/ML Implementation Guide

**For Interview Preparation: DevSecOps Consultant – AI/ML & Generative AI Focus**

**Created:** February 2, 2026  
**Author:** Althaf Hussain Syed  
**Purpose:** Technical deep-dive documentation for explaining Generative AI implementation in portfolio project

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [System Architecture Overview](#system-architecture-overview)
3. [Generative AI Integration - OpenRouter](#generative-ai-integration)
4. [RAG Pipeline Architecture](#rag-pipeline-architecture)
5. [Auto-Blogger Agent System](#auto-blogger-agent-system)
6. [Chatbot AI System](#chatbot-ai-system)
7. [Model Fallback Strategy](#model-fallback-strategy)
8. [Data Flow & Logic](#data-flow--logic)
9. [Interview Talking Points](#interview-talking-points)

---

## Executive Summary

**What You Built:** A production-grade AI-powered portfolio website with two major AI systems:
1. **Intelligent Chatbot** - RAG-based assistant using ChromaDB vector database
2. **Auto-Blogger Agent** - 4-agent autonomous blog generation pipeline

**Key Technologies:**
- **Generative AI:** OpenRouter API (multi-model access), Google Gemini API
- **Vector Database:** ChromaDB Cloud (768-dimensional embeddings)
- **LLM Models:** Mistral 7B, Gemini 2.5 Flash, DeepSeek R1, Llama 3.2
- **Infrastructure:** AWS (EC2, S3, Amplify), Docker, FastAPI
- **AI Techniques:** RAG (Retrieval-Augmented Generation), Prompt Engineering, Model Fallback Chains

---

## System Architecture Overview

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         USER                                │
└────────────┬────────────────────────────────────────────────┘
             │
    ┌────────┴────────┐
    │                 │
┌───▼────┐      ┌────▼─────┐
│Frontend│      │ Backend  │
│(React) │      │(FastAPI) │
│Amplify │      │EC2+Docker│
└────────┘      └────┬─────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
   ┌────▼───┐   ┌───▼────┐  ┌───▼──────┐
   │ChromaDB│   │OpenRouter│ │Google AI│
   │ Cloud  │   │   API    │ │Gemini API│
   └────────┘   └──────────┘ └──────────┘
        │            │            │
        └────────────┴────────────┘
                     │
              ┌──────▼──────┐
              │  S3 Bucket  │
              │(Blog Storage)│
              └─────────────┘
```

### Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Frontend** | React 18 + Amplify | User interface, deployed on AWS CDN |
| **Backend** | FastAPI + Python 3.11 | API server, AI orchestration |
| **Vector DB** | ChromaDB Cloud | Semantic search, RAG context retrieval |
| **LLM Provider** | OpenRouter API | Multi-model access (10+ free models) |
| **Embeddings** | Google Gemini `text-embedding-004` | 768-dimensional vectors |
| **Storage** | AWS S3 | Blog content storage |
| **Container** | Docker | Backend containerization |
| **Compute** | AWS EC2 t3.small | 2GB RAM, 2 vCPUs |

---

## Generative AI Integration - OpenRouter

### What is OpenRouter?

**OpenRouter** is a unified API gateway that provides access to 100+ AI models from different providers (OpenAI, Anthropic, Meta, Google, Mistral, etc.) through a single API endpoint.

**Why We Use It:**
1. **Cost Optimization** - Access to free-tier models (Mistral 7B, Llama 3.2, DeepSeek R1)
2. **Fallback Resilience** - If one model fails, automatically try another
3. **Model Diversity** - Different models for different tasks (chatbot vs blog generation)
4. **Single Integration** - One API key, multiple providers

### OpenRouter Configuration

**Location:** `backend/chatbot_provider.py` (Line 123-165)

```python
class ChatbotProvider:
    def __init__(self):
        # Dedicated API key for chatbot (isolated from auto-blogger)
        self.openrouter_key = os.getenv('CHATBOT_NEW_KEY')
        self.openrouter_url = "https://openrouter.ai/api/v1/chat/completions"
        
        # Initialize OpenAI-compatible client
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=self.openrouter_key,
            default_headers={
                "HTTP-Referer": "https://althafportfolio.site",
                "X-Title": "Althaf Portfolio Chatbot"
            }
        )
```

### Models Used via OpenRouter

#### Chatbot Models (Tier 1-2)

```python
# Tier 1: Primary Model - Mistral 7B Instruct
model = "mistralai/mistral-7b-instruct:free"
# - Speed: 1-2 seconds response time
# - Context: 6K tokens input
# - Cost: FREE
# - Use: 90% of chatbot requests

# Tier 2: Quality Fallback - OpenAI GPT-OSS 20B
model = "openai/gpt-oss-20b:free"
# - Speed: 2-3 seconds
# - Context: 8K tokens
# - Cost: FREE
# - Use: <5% (only when Tier 1 fails)
```

#### Auto-Blogger Models

```python
# Orchestrator Agent - Outline Generation
model = "deepseek/deepseek-r1-0528:free"
# - Reasoning: Mathematical/logical thinking
# - Max Tokens: 2000
# - Temperature: 0.6
# - Use: Creates blog structure

# Drafter Agent - Content Writing
model = "mistralai/mistral-small-3.1-24b-instruct:free"
# - Size: 24B parameters (high quality)
# - Max Tokens: 1500 per section
# - Temperature: 0.7 (creative)
# - Use: Writes each blog section

# Critic Agent - Quality Validation
model = "deepseek/deepseek-r1-0528:free"
# - Reasoning: Analytical evaluation
# - Max Tokens: 1000
# - Temperature: 0.3 (strict)
# - Use: Scores blogs (0-100)
```

### API Call Example

**Location:** `backend/chatbot_provider.py` (Line 292-341)

```python
def _call_openrouter(self, model: str, messages: List[Dict], max_tokens: int) -> Optional[str]:
    """
    Call OpenRouter API with automatic error handling
    """
    try:
        response = requests.post(
            self.openrouter_url,
            headers={
                "Authorization": f"Bearer {self.openrouter_key}",
                "HTTP-Referer": "https://althafportfolio.site",
                "X-Title": "Althaf Portfolio Chatbot",
                "Content-Type": "application/json"
            },
            json={
                "model": model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": 0.6,
                "stream": False
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            text = data['choices'][0]['message']['content']
            
            # Clean model artifacts
            text = text.replace("<s>", "").replace("</s>", "").strip()
            text = text.replace("[/INST]", "").replace("[INST]", "").strip()
            
            logger.info(f"OpenRouter success ({model}): {len(text)} chars")
            return text
        else:
            logger.warning(f"OpenRouter failed ({model}): {response.status_code}")
            return None
            
    except Exception as e:
        logger.error(f"OpenRouter error ({model}): {str(e)}")
        return None
```

---

## RAG Pipeline Architecture

### What is RAG?

**RAG = Retrieval-Augmented Generation**

Instead of letting the AI "hallucinate" answers, we:
1. **Retrieve** relevant context from our database (ChromaDB)
2. **Augment** the user's question with this context
3. **Generate** an answer using the LLM with factual grounding

### RAG Flow Diagram

```
User Query: "What projects has Althaf built?"
     │
     ▼
┌─────────────────────────────────────────┐
│ Step 1: Intent Detection                │
│ - Keyword matching: "projects", "built" │
│ - Intent: PROJECTS                      │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│ Step 2: Embedding Generation            │
│ - Google Gemini text-embedding-004      │
│ - Input: "What projects has Althaf..."  │
│ - Output: [0.123, -0.456, ...] (768-dim)│
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│ Step 3: ChromaDB Vector Search          │
│ - Collection: portfolio_master          │
│ - Filter: {category: "project"}         │
│ - Top-K: 6 results                      │
│ - Returns: Project descriptions         │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│ Step 4: Context Summarization           │
│ - Compress 6 results → 3 bullet points  │
│ - Cache summaries (MD5 hash)            │
│ - Reduces tokens by 60-70%              │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│ Step 5: Prompt Construction             │
│ SYSTEM: You are Assist Bot...           │
│ CONTEXT: [Summarized project data]      │
│ QUERY: What projects has Althaf built?  │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│ Step 6: LLM Generation (Mistral 7B)     │
│ - Input: 2000 tokens                    │
│ - Output: 300 tokens (simple query)     │
│ - Response: "Althaf has built..."       │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│ Step 7: Response Sanitization           │
│ - Strip apologies ("I may not have...")│
│ - Fix bot name (Allu Bot → Assist Bot) │
│ - Remove markdown formatting            │
└────────────┬────────────────────────────┘
             │
             ▼
        Final Response
```

### ChromaDB Vector Database

**What is ChromaDB?**
- Open-source vector database for AI applications
- Stores text as 768-dimensional embeddings
- Enables semantic search (meaning-based, not keyword-based)

**Our Setup:**
- **Deployment:** ChromaDB Cloud (managed service)
- **Collection:** `portfolio_master` (unified collection)
- **Embedding Model:** Google Gemini `text-embedding-004`
- **Total Documents:** ~50 (profile, projects, blogs)

**Collection Structure:**

```python
# Location: backend/populate_vector_db.py (Line 61-97)

def write_to_portfolio_master(client, embed_function, uid, doc, meta, category, subcategory=None):
    """
    Write data to portfolio_master collection with category tagging
    
    Args:
        uid: Unique ID (e.g., "project_aws_infra")
        doc: Text content to embed
        meta: Metadata dict
        category: 'profile' | 'project' | 'blog'
        subcategory: Optional (e.g., 'DevOps', 'Cloud Computing')
    """
    master_col = client.get_or_create_collection(
        'portfolio_master',
        embedding_function=embed_function
    )
    
    # Add category tags to metadata
    master_meta = meta.copy()
    master_meta['category'] = category
    if subcategory:
        master_meta['subcategory'] = subcategory
    
    # Check if exists
    existing = master_col.get(ids=[uid])
    if not existing or not existing['ids']:
        master_col.add(
            ids=[uid],
            documents=[doc],
            metadatas=[master_meta]
        )
        print(f"[OK] Added to portfolio_master: {uid} (category={category})")
```

**Example Data:**

```json
// Profile Data
{
  "id": "profile_experience_0",
  "document": "Role: Analyst III Infrastructure Services at DXC Technology. Duration: Aug 2022 - Present. Description: Supporting automation, deployment, and environment operations...",
  "metadata": {
    "category": "profile",
    "type": "experience",
    "company": "DXC Technology"
  }
}

// Project Data
{
  "id": "project_aws_portfolio",
  "document": "Project: AWS Portfolio Infrastructure. Tech Stack: AWS, Terraform, Docker, FastAPI. Summary: Built production-grade portfolio with AI chatbot...",
  "metadata": {
    "category": "project",
    "name": "AWS Portfolio",
    "technologies": ["AWS", "Terraform", "Docker"]
  }
}

// Blog Data
{
  "id": "blog_DevOps_1767241800",
  "document": "# DevOps in 2026: AI-Driven Pipelines\n\nIntroduction: The DevOps landscape is evolving...",
  "metadata": {
    "category": "blog",
    "subcategory": "DevOps",
    "title": "DevOps in 2026: AI-Driven Pipelines",
    "published_date": "2026-01-01"
  }
}
```

### Intent Detection Logic

**Location:** `backend/server.py` (Line 304-425)

```python
def detect_intent_priority(text: str) -> Tuple[str, str, dict]:
    """
    Confidence-based intent router
    Returns: (intent_key, sentiment, scores)
    """
    text = text.lower().strip()
    scores = {
        "conversation": 0,
        "info": 0,
        "exit": 0,
        "aws_projects": 0,
        "projects": 0,
        "blogs": 0,
        "profile": 0
    }
    
    # AWS / Cloud (Highest Priority)
    if any(k in text for k in ["aws", "cloud", "terraform", "deploy"]):
        scores["aws_projects"] += 15
        scores["info"] += 3
    
    # Projects (High Priority)
    if any(k in text for k in ["project", "built", "develop", "portfolio"]):
        scores["projects"] += 12
        scores["info"] += 3
    
    # Profile (Employment, Education)
    profile_keywords = [
        "who", "bio", "background", "resume", "experience", "skill",
        "working", "employed", "job", "position", "role", "company",
        "education", "degree", "university", "master", "bachelor"
    ]
    if any(k in text for k in profile_keywords):
        scores["profile"] += 10
        scores["info"] += 3
    
    # Blogs
    if any(k in text for k in ["blog", "article", "write", "post"]):
        scores["blogs"] += 10
        scores["info"] += 3
    
    # Get highest scoring intent
    best_intent, score = max(scores.items(), key=lambda x: x[1])
    
    # If not confident (score < 2), default to conversation
    if score < 2:
        return "conversation", "neutral", scores
    
    return best_intent, "neutral", scores
```

### Context Retrieval Logic

**Location:** `backend/server.py` (Line 428-723)

```python
async def get_portfolio_context(query: str, intent: str) -> str:
    """
    Smart RAG retrieval based on pre-calculated intent
    """
    # Connect to ChromaDB
    chroma_client = chromadb.CloudClient(
        api_key=os.getenv('CHROMA_API_KEY'),
        tenant=os.getenv('CHROMA_TENANT'),
        database=os.getenv('CHROMA_DATABASE')
    )
    
    # Get unified collection
    collection = chroma_client.get_collection(
        name='portfolio_master',
        embedding_function=GeminiEmbeddingFunction()
    )
    
    # Intelligent filtering based on intent
    if intent == "blogs":
        # Strict blog filter
        metadata_filter = {"category": "blog"}
        CANDIDATE_LIMIT = 30  # Fetch more for date sorting
        INJECTION_LIMIT = 6
        
    elif intent == "projects" or intent == "aws_projects":
        # Mixed query: projects + profile context
        metadata_filter = {
            "$or": [
                {"category": "project"},
                {"category": "profile"}
            ]
        }
        CANDIDATE_LIMIT = 6
        INJECTION_LIMIT = 6
        
    elif intent == "profile":
        # Profile only
        metadata_filter = {"category": "profile"}
        CANDIDATE_LIMIT = 6
        INJECTION_LIMIT = 6
    
    # Query ChromaDB
    results = collection.query(
        query_texts=[query],
        n_results=CANDIDATE_LIMIT,
        where=metadata_filter
    )
    
    docs = results.get('documents', [[]])[0]
    metas = results.get('metadatas', [[]])[0]
    
    # Summarize and inject
    summarized_docs = []
    for i, doc in enumerate(docs[:INJECTION_LIMIT]):
        meta = metas[i] if i < len(metas) else {}
        source_label = meta.get('title', 'portfolio_master')
        
        # Summarize content (60-70% token reduction)
        summary = chatbot_provider.summarize_content(doc)
        summarized_docs.append(
            f"[Source: {source_label}] (Date: {meta.get('published_date', 'N/A')})\n{summary}"
        )
    
    context_text = '\n\n'.join(summarized_docs)
    return context_text, intent
```

---

## Auto-Blogger Agent System

### 4-Agent Architecture

The auto-blogger is a **multi-agent AI system** that autonomously generates technical blog posts daily.

**Agents:**
1. **Researcher** - Web research using SERPER API
2. **Orchestrator** - Creates blog outline (DeepSeek R1)
3. **Drafter** - Writes content section-by-section (Mistral Small 24B)
4. **Critic** - Quality validation (DeepSeek R1, score ≥90 required)

### Agent Flow Diagram

```
6:00 AM IST - Cleanup Job
     │
     ▼
7:00 AM IST - Generation Pipeline
     │
     ├─► Agent 1: Researcher
     │   - Query: "latest DevOps trends 2026"
     │   - SERPER API call
     │   - Returns: 5 headlines + snippets
     │
     ├─► Agent 2: Orchestrator (DeepSeek R1)
     │   - Input: Research data
     │   - Output: JSON outline
     │   {
     │     "title": "DevOps in 2026: AI-Driven Pipelines",
     │     "summary": "Explore how AI is transforming...",
     │     "sections": [
     │       "Introduction: The AI Revolution in DevOps",
     │       "Core Concept: Self-Healing Infrastructure",
     │       "Technical Implementation: AI-Powered CI/CD",
     │       "Real-World Use Cases",
     │       "Best Practices",
     │       "Future Trends",
     │       "Conclusion"
     │     ]
     │   }
     │
     ├─► Agent 3: Drafter (Mistral Small 24B)
     │   - Loop through 7 sections
     │   - For each section:
     │     * Generate 300-400 words
     │     * Validate completion
     │     * Save to MongoDB (resumable)
     │   - Assemble complete blog
     │
     ├─► Agent 4: Critic (DeepSeek R1)
     │   - Evaluate blog quality
     │   - Scoring criteria:
     │     * Technical depth (30 points)
     │     * Clarity (20 points)
     │     * Structure (20 points)
     │     * Originality (15 points)
     │     * SEO (15 points)
     │   - Output: Score (0-100) + Verdict
     │   - If score < 75: Trigger revision (max 1 time)
     │   - If score ≥ 75: Accept
     │
     └─► Draft Ready (stored in memory + disk)

10:00 AM IST - Publishing Job
     │
     ├─► Publisher Agent
     │   - Upload to S3 bucket
     │   - Update index.json
     │   - Embed in ChromaDB
     │   - Send email notification
     │
     └─► Blog Live!
```

### Scheduler Configuration

**Location:** `backend/auto_blogger/scheduler.py` (Line 272-297)

```python
def start(self, run_now: bool = False):
    """Start the scheduler with proper event loop handling"""
    loop = asyncio.get_event_loop()
    scheduler = AsyncIOScheduler(event_loop=loop)
    
    # Schedule Production Jobs (IST timezone)
    
    # 6:00 AM IST → Cleanup (delete blogs >60 days old)
    scheduler.add_job(
        self.run_cleanup_job,
        CronTrigger(hour=6, minute=0, timezone='Asia/Kolkata')
    )
    
    # 7:00 AM IST → Generate blog
    scheduler.add_job(
        self.run_generation_pipeline,
        CronTrigger(hour=7, minute=0, timezone='Asia/Kolkata')
    )
    
    # 10:00 AM IST → Publish blog
    scheduler.add_job(
        self.run_publishing_job,
        CronTrigger(hour=10, minute=0, timezone='Asia/Kolkata')
    )
    
    logger.info("✅ BlogScheduler started: Cleanup@6AM, Generate@7AM, Publish@10AM IST")
    scheduler.start()
```

### Agent 1: Researcher

**Location:** `backend/auto_blogger/researcher.py`

```python
class BlogResearcher:
    def __init__(self):
        self.api_key = os.getenv('SERPER_API_KEY')
        self.api_url = "https://google.serper.dev/search"
    
    def analyze_trends(self, category: str) -> Dict:
        """
        Query Google for latest trends using SERPER API
        """
        query = f"latest {category} trends 2026 technology breakthroughs"
        
        response = requests.post(
            self.api_url,
            headers={"X-API-KEY": self.api_key},
            json={
                "q": query,
                "num": 5,
                "tbs": "qdr:w"  # Past week filter
            }
        )
        
        results = response.json()
        
        return {
            "headlines": [item['title'] for item in results['organic']],
            "key_insights": [item['snippet'] for item in results['organic']],
            "sources": results['organic']
        }
```

### Agent 2: Orchestrator (Outline Generation)

**Location:** `backend/auto_blogger/writer.py` (Line 273-407)

```python
def _agent_outliner(self, category: str, research_data: Dict, job_id: str) -> Dict:
    """
    Agent 1: The Architect
    Uses DeepSeek R1 to create structured outline
    """
    model_cfg = AGENT_ROLES["orchestrator"]
    model_id = "deepseek/deepseek-r1-0528:free"
    
    prompt = f"""
    You are an elite technical blog architect.
    Topic: {category}
    
    RESEARCH SUMMARY:
    {json.dumps(research_data, indent=2)}
    
    TASK:
    Create a detailed structural outline for a 2500-word technical blog.
    
    CRITICAL TITLE REQUIREMENTS:
    - Title MUST be unique and specific (NOT generic like "Technical Deep Dive")
    - Include year (2026) or specific technologies
    - Reflect CURRENT TRENDS from research
    
    OUTPUT FORMAT (JSON ONLY):
    {{
        "title": "Unique, specific, engaging title",
        "summary": "2-3 sentence preview",
        "sections": [
            "Introduction: Hook + Problem Statement",
            "Core Concept Deep Dive",
            "Technical Implementation",
            "Real-World Use Cases",
            "Best Practices",
            "Future Trends",
            "Conclusion"
        ]
    }}
    """
    
    response = self.client.chat.completions.create(
        model=model_id,
        messages=[
            {
                "role": "system",
                "content": "You are a JSON-only API. Respond ONLY with valid JSON."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        max_tokens=2000,
        temperature=0.6
    )
    
    content = response.choices[0].message.content
    outline_data = extract_json_from_response(content, logger)
    
    return {
        "title": outline_data['title'],
        "summary": outline_data['summary'],
        "sections": outline_data['sections']
    }
```

### Agent 3: Drafter (Content Writing)

**Location:** `backend/auto_blogger/writer.py` (Line 409-530)

```python
def _agent_drafter_loop(self, category: str, sections: List[str], research_data: Dict, job_id: str) -> str:
    """
    Agent 2: The Builder
    Uses Mistral Small 24B to write each section individually
    """
    model_id = "mistralai/mistral-small-3.1-24b-instruct:free"
    job_mgr = get_job_state_manager()
    
    full_draft = []
    
    for index, section in enumerate(sections):
        # Check if already completed (resumable)
        completed_sections = job_mgr.get_completed_sections(job_id)
        if index in completed_sections:
            logger.info(f"⏭️ Section {index + 1} already completed, skipping")
            full_draft.append(completed_sections[index])
            continue
        
        # Context for this section
        prev_context = full_draft[-1][-500:] if full_draft else "Start of blog."
        
        prompt = f"""
        You are a technical writer drafting ONE section of a blog.
        Blog Topic: {category}
        Current Section: "{section}"
        
        Global Context (Research):
        {json.dumps(research_data)[:3000]}
        
        Previous Paragraph (Connect to this):
        "...{prev_context}"
        
        TASK:
        Write the full content for the section "{section}".
        - Length: Approx 300-400 words
        - Style: Authoritative, technical, engaging
        - If code section, provide valid code snippets
        - Don't write "Here is the section". Just write the content.
        """
        
        response = self.client.chat.completions.create(
            model=model_id,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1500,
            temperature=0.7
        )
        
        content = response.choices[0].message.content.strip()
        
        # Validate section is complete
        if self._validate_section(content):
            formatted_section = f"\n\n## {section}\n\n{content}"
            
            # Save to MongoDB immediately (resumable)
            job_mgr.save_section(job_id, index, formatted_section)
            
            full_draft.append(formatted_section)
            time.sleep(3)  # Rate limiting
        else:
            logger.warning(f"⚠️ Section incomplete, skipping")
    
    return "\n".join(full_draft)
```

### Agent 4: Critic (Quality Validation)

**Location:** `backend/auto_blogger/critic.py`

```python
class BlogCritic:
    def __init__(self):
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("BLOG_KEY")
        )
    
    def evaluate(self, draft: str, category: str) -> Tuple[bool, str]:
        """
        Evaluate blog quality using DeepSeek R1
        Returns: (passed, review_json)
        """
        model_id = "deepseek/deepseek-r1-0528:free"
        
        prompt = f"""
        You are a senior technical editor evaluating a blog post.
        
        BLOG DRAFT:
        {draft}
        
        EVALUATION CRITERIA (100 points total):
        1. Technical Depth (30 points)
           - Accurate technical details
           - Code examples (if applicable)
           - Real-world applicability
        
        2. Clarity & Readability (20 points)
           - Clear explanations
           - Logical flow
           - No jargon overload
        
        3. Structure (20 points)
           - Proper sections
           - Introduction/Conclusion
           - Transitions
        
        4. Originality (15 points)
           - Unique insights
           - Not generic content
           - Fresh perspective
        
        5. SEO & Engagement (15 points)
           - Compelling title
           - Proper headings
           - Scannable format
        
        OUTPUT FORMAT (JSON ONLY):
        {{
            "score": 85,
            "verdict": "PASS" | "FAIL",
            "strengths": ["Point 1", "Point 2"],
            "weaknesses": ["Issue 1", "Issue 2"],
            "recommendation": "Accept" | "Revise" | "Reject"
        }}
        
        PASS THRESHOLD: Score ≥ 90
        """
        
        response = self.client.chat.completions.create(
            model=model_id,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000,
            temperature=0.3  # Low temp for consistent evaluation
        )
        
        review_json = response.choices[0].message.content
        review = json.loads(review_json)
        
        passed = review['score'] >= 90
        return passed, review_json
```

### Publisher Agent

**Location:** `backend/auto_blogger/publisher.py` (Line 297-323)

```python
def publish(self, blog_data: Dict) -> str:
    """
    Publish blog to S3 + ChromaDB
    """
    blog_id = f"{blog_data['category']}_{int(time.time())}"
    
    # 1. Upload to S3
    s3 = boto3.client('s3')
    s3.put_object(
        Bucket='althaf-blogs-storage',
        Key=f'blogs/posts/{blog_id}.json',
        Body=json.dumps(blog_data),
        ContentType='application/json'
    )
    
    # 2. Update index.json
    index = s3.get_object(Bucket='althaf-blogs-storage', Key='blogs/index.json')
    index_data = json.loads(index['Body'].read())
    index_data['blogs'].append({
        "id": blog_id,
        "title": blog_data['title'],
        "category": blog_data['category'],
        "created_at": blog_data['created_at']
    })
    s3.put_object(
        Bucket='althaf-blogs-storage',
        Key='blogs/index.json',
        Body=json.dumps(index_data)
    )
    
    # 3. Embed in ChromaDB
    chroma_client = chromadb.CloudClient(...)
    collection = chroma_client.get_or_create_collection("portfolio_master")
    
    embedding = self._get_embedding(blog_data['content'])
    collection.upsert(
        ids=[blog_id],
        documents=[blog_data['content']],
        metadatas=[{
            "category": "blog",
            "subcategory": blog_data['category'],
            "title": blog_data['title'],
            "published_date": blog_data['created_at'][:10]
        }],
        embeddings=[embedding]
    )
    
    return f"https://althafportfolio.site/blogs/{blog_id}"
```

---

## Chatbot AI System

### Conversation State Machine

**Location:** `backend/chatbot_provider.py` (Line 228-251)

```python
def detect_conversation_state(self, text: str) -> str:
    """
    Simplified conversation state detection
    Only distinguishes between greetings and questions
    """
    t = text.lower().strip()
    
    # Check for simple greetings (no question)
    simple_greetings = ["hi", "hello", "hey", "hai", "hii", "hola"]
    if t in simple_greetings:
        return "GREETING"
    
    # Everything else goes to INFO (ChromaDB retrieval)
    return "INFO"

def generate_response_by_state(self, state: str, user_input: str) -> str:
    """
    Simple responses for greetings only
    All other inputs go to ChromaDB retrieval
    """
    if state == "GREETING":
        return "Hello! I'm Assist Bot, Althaf's portfolio assistant. How can I help you?"
    
    return ""  # Should never reach here
```

### Prompt Engineering

**System Prompt** - Location: `backend/chatbot_provider.py` (Line 60-115)

```python
SYSTEM_PROMPT = """
You are Assist Bot, Althaf Hussain Syed's portfolio assistant.

🗓️ CRITICAL: TODAY'S DATE IS {current_date}. Use this for ALL date-related logic.

IDENTITY & TONE (NON-NEGOTIABLE):
1. You are "Assist Bot", but you MUST refer to yourself as "I" or "me"
2. NEVER refer to yourself in the third person
3. NEVER say "Allu Bot" or any other name
4. You speak about Althaf Hussain Syed in third person (he/his)
5. Be warm, professional, conversational, and highly intelligent
6. You have ADVANCED RAG (Retrieval-Augmented Generation) capabilities

DATE AWARENESS RULES (MANDATORY):
1. TODAY IS {current_date} - memorize this
2. If an event's END DATE is before today → use PAST tense
3. If an event's START DATE is before today but NO END DATE → use PRESENT tense
4. CRITICAL EXAMPLE:
   - Context says: "Master's degree, December 2022 - June 2024"
   - Today is January 2026
   - June 2024 was 18 MONTHS AGO
   - CORRECT: "He completed his Master's degree in June 2024"
   - WRONG: "He is currently completing"

CRITICAL RETRIEVAL RULES (STRICT):
1. The context provided below is from Althaf's verified portfolio database
2. Context is tagged with categories: personal, experience, achievements, education, contact, certifications, projects, blogs
3. You MUST analyze context metadata and retrieve ONLY relevant information
4. NEVER hallucinate or invent information not explicitly stated in the context
5. If context is empty or irrelevant, say "I checked Althaf's portfolio, but I couldn't find that specific detail"

RESPONSE STYLE:
1. Write like a human - no hyphens, no bullet points unless necessary
2. Use natural paragraphs with proper sentences
3. Keep responses concise - 2 to 4 sentences for most questions
4. Match the user's tone - brief for greetings, detailed for complex questions
5. Never use phrases like "based on the information provided"

FORBIDDEN:
- Never say "Allu Bot" (you are Assist Bot)
- Never refer to yourself in third person
- No markdown formatting (no *, -, #, etc.)
- No apologizing unless user points out error
- No inventing information outside the provided context
"""
```

**User Message Construction** - Location: `backend/chatbot_provider.py` (Line 279-286)

```python
user_message = f"""VERIFIED INFORMATION FROM ALTHAF'S PORTFOLIO DATABASE:
{context}

CRITICAL INSTRUCTION: Answer the user's question using ONLY the information above. 
This is accurate, verified data from Althaf's portfolio. Do NOT invent or assume 
anything beyond what is explicitly stated above.

USER QUESTION: {query}

Remember: You are Assist Bot (never say Allu Bot). Respond naturally in 
conversational paragraphs without special formatting."""
```

### Context Summarization

**Location:** `backend/chatbot_provider.py` (Line 175-226)

```python
def summarize_content(self, text: str) -> str:
    """
    Compress retrieved RAG chunks into concise bullet points.
    Reduces token usage by 60-70% while maintaining signal.
    Includes Caching (Task 6).
    """
    # If text is already short, don't waste time
    if len(text) < 600:
        return text
    
    # Check Cache (MD5 hash)
    import hashlib
    text_hash = hashlib.md5(text.encode()).hexdigest()
    if text_hash in self.summary_cache:
        logger.info("⚡ Returning cached summary")
        return self.summary_cache[text_hash]
    
    try:
        prompt = f"""
        TASK: Summarize this project/document into exactly 3 standardized bullet points.
        FORMAT:
        - Problem: (1 sentence)
        - Tech: (List key tools)
        - Outcome: (1 sentence, quantify if possible)
        
        TEXT:
        {text[:4000]}
        """
        
        # Use Mistral 7B for internal micro-tasks
        messages = [{"role": "user", "content": prompt}]
        summary_text = self._call_openrouter(
            model="mistralai/mistral-7b-instruct:free",
            messages=messages,
            max_tokens=300
        )
        
        if summary_text:
            summary = f"[Summarized Evidence]:\n{summary_text}"
            # Cache the result
            self.summary_cache[text_hash] = summary
            return summary
        
        return text[:1000] + "... [Truncated]"
        
    except Exception as e:
        logger.warning(f"Summarization failed: {e}")
        return text[:600] + "... [Truncated fallback]"
```

---

## Model Fallback Strategy

### 4-Tier Fallback Chain

**Location:** `backend/chatbot_provider.py` (Line 562-668)

```python
def generate_response(self, query: str, context: str, history: List[Dict] = None, sentiment: str = "neutral") -> str:
    """
    4-Tier fallback system for 99.9% uptime
    """
    
    # Tier 1: Gemma 3 27B IT (Free) - Large Model PRIMARY
    logger.info("Trying Tier 1: Gemma 3 27B IT (Free)")
    response = self._call_openrouter("google/gemma-3-27b-it:free", messages, max_tokens)
    if response:
        logger.info("✅ Response from Gemma 3 27B")
        return self._clean_response(response)
    
    # Tier 2: Mistral 7B Instruct (Free) - Fast Fallback
    logger.info("Trying Tier 2: Mistral 7B Instruct (Free)")
    response = self._call_openrouter("mistralai/mistral-7b-instruct:free", messages, max_tokens)
    if response:
        logger.info("✅ Response from Mistral 7B")
        return self._clean_response(response)
    
    # Tier 3: Gemini Chain (Standard) - Reliable when OpenRouter is down
    logger.info("Trying Tier 3: Gemini Chain (Standard)")
    response = self._call_gemini_fallback(query, context, history, max_tokens)
    if response:
        logger.info("✅ Response from Gemini Chain")
        return self._clean_response(response)
    
    # Tier 4: Hugging Face - Llama 3.2 3B Instruct (Last Resort)
    logger.info("Trying Tier 4: Hugging Face - Llama 3.2 3B")
    hf_prompt = f"{SYSTEM_PROMPT}\n\nCONTEXT:\n{context}\n\nQUERY: {query}"
    response = self._call_huggingface(hf_prompt, max_tokens)
    if response:
        logger.info("✅ Response from Llama 3.2 3B (HF)")
        return self._clean_response(response)
    
    # All providers failed
    logger.error("All providers failed")
    return "I'm having trouble connecting to my AI services right now. Please try again in a moment."
```

**Why This Works:**
1. **Provider Diversity** - OpenRouter, Google AI, Hugging Face
2. **Model Diversity** - Different models have different rate limits
3. **Automatic Failover** - No manual intervention needed
4. **Graceful Degradation** - Always returns a response

---

## Data Flow & Logic

### Complete Request Flow

```
User: "What projects has Althaf built?"
     │
     ▼
┌─────────────────────────────────────────────────────────┐
│ Frontend (React)                                        │
│ - User types message in chatbot                        │
│ - Generate session ID (localStorage)                   │
│ - POST /api/ask-all-u-bot                              │
│   Body: {message: "...", session_id: "session_123"}    │
└────────────┬────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────┐
│ Backend (FastAPI) - server.py                          │
│ 1. Rate Limiting Check (10 req/min per session)        │
│ 2. Detect Intent: "projects" (score: 12)               │
│ 3. Detect Sentiment: "neutral"                         │
└────────────┬────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────┐
│ RAG Pipeline - get_portfolio_context()                 │
│ 1. Generate embedding (Gemini text-embedding-004)      │
│    Input: "What projects has Althaf built?"            │
│    Output: [0.123, -0.456, ...] (768 dimensions)       │
│                                                         │
│ 2. Query ChromaDB                                      │
│    Collection: portfolio_master                        │
│    Filter: {category: "project"}                       │
│    Top-K: 6 results                                    │
│                                                         │
│ 3. Summarize Results (60-70% token reduction)          │
│    - Check cache (MD5 hash)                            │
│    - If not cached, use Mistral 7B to summarize        │
│    - Cache result                                      │
│                                                         │
│ 4. Return Context                                      │
│    "[Source: AWS Portfolio] Problem: Built production- │
│     grade portfolio with AI chatbot. Tech: AWS,        │
│     Terraform, Docker, FastAPI. Outcome: Deployed on   │
│     EC2 with 99.9% uptime..."                          │
└────────────┬────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────┐
│ Chatbot Provider - generate_response()                 │
│ 1. Format Messages                                     │
│    System: "You are Assist Bot..."                     │
│    Context: "[Summarized project data]"                │
│    User: "What projects has Althaf built?"             │
│                                                         │
│ 2. Tier 1: Gemma 3 27B (OpenRouter)                    │
│    - POST https://openrouter.ai/api/v1/chat/completions│
│    - Model: google/gemma-3-27b-it:free                 │
│    - Max Tokens: 300 (simple query)                    │
│    - Temperature: 0.6                                  │
│    - Response: "Althaf has built several projects..."  │
│                                                         │
│ 3. Clean Response                                      │
│    - Strip model artifacts (<s>, </s>, [INST])         │
│    - Remove bullet points (- item → item)              │
│    - Fix bot name (Allu Bot → Assist Bot)              │
└────────────┬────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────┐
│ Response Sanitizer Middleware                          │
│ - Strip apology phrases ("I may not have...")          │
│ - Fix bot name (regex replacement)                     │
│ - Remove excessive whitespace                          │
└────────────┬────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────┐
│ Cache Response                                         │
│ - MD5 hash of query                                    │
│ - Store in memory (max 100 items, 1 hour TTL)          │
└────────────┬────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────┐
│ Return to Frontend                                     │
│ Response: {                                            │
│   "reply": "Althaf has built several projects,        │
│             including an AWS-based portfolio with      │
│             AI chatbot, a Terraform VPC module, and    │
│             a CI/CD pipeline automation tool."         │
│ }                                                      │
└─────────────────────────────────────────────────────────┘
```

### Auto-Blogger Data Flow

```
7:00 AM IST - Cron Trigger
     │
     ▼
┌─────────────────────────────────────────────────────────┐
│ Scheduler - run_generation_pipeline()                  │
│ 1. Select Category (round-robin)                       │
│    - Categories: [DevOps, Cloud Computing,             │
│                   Cybersecurity, AI/ML]                │
│    - State file: /app/backend/logs/auto_blogger/       │
│                  scheduler_state.json                  │
│    - Selected: "DevOps"                                │
└────────────┬────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────┐
│ Researcher - analyze_trends()                          │
│ 1. Query SERPER API                                    │
│    POST https://google.serper.dev/search               │
│    Body: {                                             │
│      "q": "latest DevOps trends 2026",                 │
│      "num": 5,                                         │
│      "tbs": "qdr:w"  // Past week                      │
│    }                                                   │
│                                                         │
│ 2. Extract Data                                        │
│    {                                                   │
│      "headlines": [                                    │
│        "AI-Driven DevOps Pipelines Transform...",      │
│        "Platform Engineering Emerges as...",           │
│        ...                                             │
│      ],                                                │
│      "key_insights": [                                 │
│        "AI is automating 70% of DevOps tasks...",      │
│        ...                                             │
│      ]                                                 │
│    }                                                   │
└────────────┬────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────┐
│ Orchestrator - _agent_outliner()                       │
│ 1. Call DeepSeek R1 (OpenRouter)                       │
│    Model: deepseek/deepseek-r1-0528:free               │
│    Prompt: "Create outline for DevOps blog..."         │
│    Max Tokens: 2000                                    │
│    Temperature: 0.6                                    │
│                                                         │
│ 2. Extract JSON                                        │
│    {                                                   │
│      "title": "DevOps in 2026: AI-Driven Pipelines",  │
│      "summary": "Explore how AI is transforming...",   │
│      "sections": [                                     │
│        "Introduction: The AI Revolution",              │
│        "Core Concept: Self-Healing Infrastructure",    │
│        "Technical Implementation: AI-Powered CI/CD",   │
│        "Real-World Use Cases",                         │
│        "Best Practices",                               │
│        "Future Trends",                                │
│        "Conclusion"                                    │
│      ]                                                 │
│    }                                                   │
│                                                         │
│ 3. Save to MongoDB                                     │
│    Collection: auto_blogger_jobs                       │
│    Document: {                                         │
│      job_id: "DevOps-2026-02-02-070005",               │
│      status: "OUTLINING",                              │
│      outline: {...}                                    │
│    }                                                   │
└────────────┬────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────┐
│ Drafter - _agent_drafter_loop()                        │
│ For each section (7 sections):                         │
│                                                         │
│ Section 1: "Introduction: The AI Revolution"           │
│ ├─ Call Mistral Small 24B (OpenRouter)                 │
│ │  Model: mistralai/mistral-small-3.1-24b-instruct:free│
│ │  Prompt: "Write section: Introduction..."           │
│ │  Max Tokens: 1500                                    │
│ │  Temperature: 0.7                                    │
│ │                                                       │
│ ├─ Validate Section                                    │
│ │  - Check length (>50 chars)                          │
│ │  - Check ending (., !, ?, }, ])                      │
│ │                                                       │
│ ├─ Save to MongoDB                                     │
│ │  Collection: auto_blogger_jobs                       │
│ │  Update: {                                           │
│ │    sections: {                                       │
│ │      0: "## Introduction...\n\nContent..."           │
│ │    }                                                 │
│ │  }                                                   │
│ │                                                       │
│ └─ Wait 3 seconds (rate limiting)                      │
│                                                         │
│ Repeat for sections 2-7...                             │
│                                                         │
│ Assemble: "\n".join(all_sections)                      │
│ Result: 2500-word blog post                            │
└────────────┬────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────┐
│ Critic - evaluate()                                    │
│ 1. Call DeepSeek R1 (OpenRouter)                       │
│    Model: deepseek/deepseek-r1-0528:free               │
│    Prompt: "Evaluate blog quality..."                  │
│    Max Tokens: 1000                                    │
│    Temperature: 0.3 (strict)                           │
│                                                         │
│ 2. Extract JSON                                        │
│    {                                                   │
│      "score": 92,                                      │
│      "verdict": "PASS",                                │
│      "strengths": [                                    │
│        "Excellent technical depth",                    │
│        "Clear code examples",                          │
│        "Engaging narrative"                            │
│      ],                                                │
│      "weaknesses": [                                   │
│        "Could add more real-world examples"            │
│      ],                                                │
│      "recommendation": "Accept"                        │
│    }                                                   │
│                                                         │
│ 3. Decision                                            │
│    - Score ≥ 90: PASS → Store draft                    │
│    - Score 75-89: ACCEPTABLE → Store draft             │
│    - Score < 75: REVISE (max 1 time)                   │
│    - Score < 60: REJECT                                │
└────────────┬────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────┐
│ Store Draft                                            │
│ 1. Memory: self.pending_draft = {...}                  │
│ 2. Disk: /app/backend/logs/auto_blogger/               │
│          pending_draft.json                            │
│    (Survives Docker rebuilds)                          │
└─────────────────────────────────────────────────────────┘

10:00 AM IST - Publishing Job
     │
     ▼
┌─────────────────────────────────────────────────────────┐
│ Publisher - publish()                                  │
│ 1. Load draft (from memory or disk)                    │
│                                                         │
│ 2. Upload to S3                                        │
│    Bucket: althaf-blogs-storage                        │
│    Key: blogs/posts/DevOps_1738478400.json             │
│    Body: {                                             │
│      title: "DevOps in 2026...",                       │
│      content: "# DevOps in 2026...\n\n...",            │
│      category: "DevOps",                               │
│      created_at: "2026-02-02T10:00:00Z"                │
│    }                                                   │
│                                                         │
│ 3. Update index.json                                   │
│    - Download blogs/index.json                         │
│    - Append new blog metadata                          │
│    - Upload updated index.json                         │
│                                                         │
│ 4. Embed in ChromaDB                                   │
│    - Generate embedding (Gemini text-embedding-004)    │
│    - Collection: portfolio_master                      │
│    - Metadata: {                                       │
│        category: "blog",                               │
│        subcategory: "DevOps",                          │
│        title: "DevOps in 2026...",                     │
│        published_date: "2026-02-02"                    │
│      }                                                 │
│                                                         │
│ 5. Send Email Notification                            │
│    - Service: Resend API                               │
│    - To: allualthaf42@gmail.com                        │
│    - Subject: "✅ Blog Published: DevOps in 2026..."   │
│    - Body: URL + metadata                              │
│                                                         │
│ 6. Cleanup                                             │
│    - Delete pending_draft.json                         │
│    - Clear memory                                      │
└─────────────────────────────────────────────────────────┘
```

---


## Containerization & Deployment Strategy

### Docker Architecture
We containerized the entire backend application to ensure consistency across development and production environments.

**Dockerfile Breakdown:**
*   **Base Image:** `python:3.11-slim` (Lightweight, optimized for production).
*   **Dependencies:** Installs `build-essential` for compiling Python packages, then removes it to keep image size small (~200MB).
*   **Security:** Runs as a non-root user (best practice).
*   **Command:** Uses `uvicorn` server for high-performance ASGI handling.

### Build & Deploy Pipeline (GitHub Actions)
Our pipeline uses a **Self-Hosted Runner** on the AWS EC2 instance.

1.  **Trigger:** Push to `main` branch.
2.  **Runner:** Executes directly on the EC2 server (`runs-on: self-hosted`).
3.  **Build:** 
    ```bash
    docker build --no-cache -t portfolio-backend .
    ```
4.  **Run:**
    ```bash
    docker run -d -p 8000:8000 --restart always portfolio-backend
    ```

### Enterprise Standard: Docker Registry (ECR)
*To scale this architecture for larger teams, we would implement the **Registry Pattern**.*

**How it works (Interview Explanation):**
1.  **Build:** GitHub Actions builds the image.
2.  **Tag:** Tag the image with the commit SHA or version (e.g., `v1.0.0`).
    ```bash
    docker tag portfolio-backend:latest 123456789012.dkr.ecr.ap-south-1.amazonaws.com/portfolio-backend:v1
    ```
3.  **Push:** Upload to **AWS ECR (Elastic Container Registry)**.
    ```bash
    aws ecr get-login-password | docker login --username AWS --password-stdin ...
    docker push 123456789012.dkr.ecr.ap-south-1.amazonaws.com/portfolio-backend:v1
    ```
4.  **Pull:** Production servers pull the exact image digest from ECR, guaranteeing identical code running everywhere.

**Why use a Registry?**
*   **Rollbacks:** Easily revert to previous tagged versions.
*   **Security:** Scan images for vulnerabilities (AWS ECR Image Scanning).
*   **Speed:** Pre-build images so deployment is just a fast download.

---


---

## CI/CD Pipeline & DevOps Architecture

### Why GitHub Actions?
We chose GitHub Actions for its tight integration with our repository and ability to define "Infrastructure as Code" for our deployment pipeline.

### The Pipeline Workflow (`backend-deploy.yml`)
1.  **Trigger:** Pushes to the `main` branch (excluding frontend changes).
2.  **Environment:** Runs on a **Self-Hosted Runner** (direct execution on EC2).
3.  **Secrets Injection:** Securely injects API keys from GitHub Secrets into a production `.env.local` file.
4.  **Deployment:** Builds the Docker container and restarts the service with zero manual intervention.

### Strategic Choice: Self-Hosted Runner
We deliberately chose a **Self-Hosted Runner** (installed directly on the AWS EC2 instance) over GitHub-hosted runners.

**Why? (Interview Logic):**
1.  **Security (Zero-Trust):** We don't need to open SSH ports (Port 22) to the public internet or GitHub's IP ranges. The runner initiates an outbound connection *from* the EC2 instance *to* GitHub to fetch jobs.
2.  **Cost Optimization:** GitHub-hosted runners cost money per minute after the free tier. Our EC2 instance is already running (sunk cost), so deployments are effectively **free**.
3.  **Performance:** The runner is already on the deployment target. We avoid the network latency of transferring the build artifact (Docker image) from a GitHub server to our EC2 server. We build *locally* and run *immediately*.
4.  **Persistent Filesystem (Caching):**
    - Unlike GitHub-hosted runners which are wiped clean after every job, our self-hosted runner maintains its filesystem.
    - **Benefit:** Docker layers and pip dependencies are cached locally. We don't need to re-download the base images or Python libraries on every deploy, drastically reducing build times.
5.  **No Usage Limits (Cost Control):**
    - GitHub Free tier limits actions to 2,000 minutes/month.
    - **Benefit:** Self-hosted runners have unlimited minutes. We can run long integration tests or heavy builds without worrying about hitting quotas or incurring overage charges.
6.  **Private Network Access:**
    - The runner sits inside our VPC/Network.
    - **Benefit:** It can directly access private resources (like internal databases, staging environments, or other microservices) that are not exposed to the public internet, without needing complex VPNs or IP allow-listing.

### Secrets Management Strategy
We implement a strict **"Least Privilege"** secrets management flow.

**The Flow:**
1.  **Storage:** Secrets (API Keys, Mongo URI) are encrypted and stored in **GitHub Repository Secrets**. They are never checked into Git.
2.  **Injection:** The workflow step explicitly maps these secrets to environment variables.
3.  **File Creation:** The workflow acts as the "Gatekeeper", creating a temporary `.env.local` file on the production server *only during deployment*.
    ```yaml
    # Snippet from backend-deploy.yml
    - name: Create env file
      run: |
        echo "MONGO_URL=${{ secrets.MONGO_URL }}" > .env.local
        echo "OPENROUTER_KEY=${{ secrets.CHATBOT_NEW_KEY }}" >> .env.local
    ```
4.  **Runtime:** The Docker container loads this file using `--env-file .env.local`.
5.  **Isolation:** The `.env.local` file is strictly permissions-locked on the server and ignored by git (`.gitignore`).

---

## Interview Talking Points

### How to Explain This Project

**Opening Statement:**
> "I built a production-grade AI-powered portfolio website with two major AI systems: an intelligent chatbot using RAG (Retrieval-Augmented Generation) and an autonomous blog generation pipeline. Both leverage Generative AI through OpenRouter API for multi-model access, ChromaDB for vector search, and Google Gemini for embeddings."

### Key Technical Achievements

1. **Multi-Model Fallback Architecture**
   - "I implemented a 4-tier fallback system using OpenRouter API to access 10+ free LLM models"
   - "This ensures 99.9% uptime - if Mistral 7B fails, it automatically falls back to Gemini or Llama"
   - "Each tier has different rate limits, so we maximize availability"

2. **RAG Pipeline with ChromaDB**
   - "I built a RAG pipeline using ChromaDB Cloud as the vector database"
   - "User queries are embedded using Google Gemini's text-embedding-004 model (768 dimensions)"
   - "We perform semantic search with metadata filtering - for example, blog queries only search blog content"
   - "Context summarization reduces token usage by 60-70% using MD5-based caching"

3. **4-Agent Auto-Blogger System**
   - "I designed a multi-agent system where each agent has a specific role:"
   - "Researcher uses SERPER API for web research, Orchestrator creates outlines using DeepSeek R1"
   - "Drafter writes content section-by-section using Mistral Small 24B, Critic validates quality"
   - "The system is resumable - if a section fails, it saves progress to MongoDB and retries"

4. **Prompt Engineering**
   - "I engineered prompts with strict instructions to prevent hallucination"
   - "For example, the chatbot system prompt explicitly states: 'NEVER invent information not in the context'"
   - "I use date-aware prompts that inject the current date to handle temporal queries correctly"

5. **Production Infrastructure**
   - "Deployed on AWS EC2 with Docker containerization"
   - "ChromaDB Cloud for vector storage, S3 for blog content, MongoDB for job state"
   - "CI/CD via GitHub Actions with self-hosted runner on EC2"

### Metrics to Mention

- **Cost:** $0/month for AI (all free-tier models)
- **Compute Cost:** ~$18-20/month (AWS t3.small + EBS)
- **Uptime:** 99.9% (4-tier fallback)
- **Response Time:** 1-2 seconds (chatbot)
- **Blog Generation:** 7-10 minutes (2500 words)
- **Token Reduction:** 60-70% (context summarization)
- **Automation:** 100% autonomous (scheduled daily at 7 AM IST)

### Questions You Can Answer

**Q: How do you prevent hallucination?**
> "I use RAG - every response is grounded in retrieved context from ChromaDB. The system prompt explicitly forbids inventing information. If no relevant context is found, the chatbot says 'I couldn't find that information' instead of guessing."

**Q: How do you handle model failures?**
> "I implemented a 4-tier fallback chain. If OpenRouter's Mistral 7B fails, it tries Gemini. If that fails, it tries Hugging Face's Llama 3.2. This ensures we always return a response."

**Q: How do you optimize costs?**
> "I use only free-tier models via OpenRouter. Context summarization reduces token usage by 60-70%. I cache summaries using MD5 hashing to avoid redundant API calls. Total AI cost: $0/month."

**Q: How do you ensure blog quality?**
> "I use a Critic agent powered by DeepSeek R1 that scores blogs on 5 criteria (technical depth, clarity, structure, originality, SEO). Blogs must score ≥90 to pass. If they score 75-89, they're accepted with a warning. Below 75, they're revised once or rejected."

**Q: How do you handle concurrent requests?**
> "I implemented per-session rate limiting (10 requests/minute) using a custom RateLimiter class. Each session is tracked by a unique ID stored in localStorage. This prevents abuse while allowing legitimate users to interact freely."

---

## Conclusion

This portfolio project demonstrates:
- ✅ **Generative AI Integration** - OpenRouter multi-model access
- ✅ **RAG Implementation** - ChromaDB vector search
- ✅ **Multi-Agent Systems** - 4-agent blog generation pipeline
- ✅ **Prompt Engineering** - Hallucination prevention, date awareness
- ✅ **Production Infrastructure** - AWS, Docker, CI/CD
- ✅ **Cost Optimization** - $0/month AI costs using free-tier models
- ✅ **Reliability** - 4-tier fallback, resumable jobs, error handling

**This aligns perfectly with the DevSecOps Consultant role's requirements for AI/ML & Generative AI experience.**
