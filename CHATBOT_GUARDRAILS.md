# Chatbot Guardrails Implementation

## Overview
Implemented comprehensive guardrails for the Allu Bot chatbot to ensure professional, portfolio-focused interactions while minimizing API costs through strict content filtering.

## Guardrail Categories

### 1. Content Filtering (Inappropriate Topics)
**Purpose**: Block non-professional discussions
**Keywords blocked**: 
- Personal/intimate topics: dating, relationships, marriage, personal life
- Financial: money, salary, finances, investments, crypto, trading
- Politics: political topics, elections, government policies
- Adult content: inappropriate terms
- Entertainment: movies, sports, games, celebrities
- Random queries: weather, news, shopping, travel

**Response**: Redirects to technical/portfolio discussions

### 2. Topic Restriction (Professional Focus)
**Allowed Topics**:
- DevOps, cloud computing, programming
- AI/ML, IoT, cybersecurity, software architecture
- Althaf's portfolio, skills, experience, projects
- Technical certifications, education
- Programming languages, frameworks, databases

**Response**: Guides users toward appropriate technical topics

### 3. Portfolio Priority System
**Portfolio-covered keywords**: 
- Althaf, portfolio, skills, experience, projects, certifications
- DevOps tools, AWS, Azure, GCP, Jenkins, Docker, Kubernetes
- Contact information, education details

**Logic**: If query matches portfolio keywords, return portfolio data directly (no internet search)

### 4. API Cost Protection
**Credit Conservation Strategy**:
- **First Priority**: Portfolio knowledge base (no API cost)
- **Second Priority**: General tech queries with strict filtering
- **Last Resort**: Internet search with warning

**Internet Search Restrictions**:
- Only for queries starting with: "What is", "How does", "Explain", "Difference between"
- Must contain advanced tech keywords: ML, AI, blockchain, quantum computing, etc.
- Includes warning: "⚠️ *Using limited internet search for this tech query*"

### 5. Response Quality Controls
**Gemini API Usage**:
- Limited to 2-3 sentence responses for external queries
- Tech-focused prompts only
- Fallback to portfolio data if API fails

**Portfolio Responses**:
- Comprehensive, detailed information about Althaf
- Direct contact information
- Project descriptions with technologies and achievements
- Skills categorized by cloud, DevOps, and programming

## Implementation Details

### Key Functions:
- `handle_agent_query()`: Main guardrail logic
- Inappropriate keyword filtering
- Topic validation with allowed_topics list
- Portfolio-first response system
- Credit protection with internet search warnings

### Error Handling:
- All API failures fall back to portfolio information
- No generic error messages - always provide portfolio value
- Graceful degradation maintains professional focus

### User Experience:
- Clear guidance on appropriate topics
- Helpful suggestions for rephrasing queries
- Rich portfolio information always available
- Transparent about API usage with warnings

## Benefits Achieved

1. **Cost Control**: Minimized Serper API usage through portfolio-first responses
2. **Professional Brand**: All interactions remain technical and professional  
3. **Comprehensive Coverage**: Full portfolio information available offline
4. **User Guidance**: Clear directions for appropriate queries
5. **Quality Responses**: Rich, detailed portfolio information prioritized over generic web results

## Testing Scenarios

### ✅ Approved Queries:
- "Tell me about Althaf's AWS experience"
- "What DevOps tools does Althaf use?"
- "How to contact Althaf?"
- "What is Kubernetes?" (general tech)
- "Explain machine learning concepts"

### ❌ Blocked Queries:
- Personal life questions
- Financial advice requests  
- Entertainment discussions
- Political topics
- Non-technical random queries

### ⚠️ Limited Internet Access:
- Advanced tech concepts not in portfolio
- Includes API usage warning
- Brief, technical responses only

## Maintenance Notes

- Keyword lists can be expanded as needed
- Portfolio knowledge base is comprehensive and updatable
- API usage warnings help monitor costs
- All responses maintain professional tone and technical focus