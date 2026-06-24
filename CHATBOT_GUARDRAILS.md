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

---

## 🚀 Behavioral Improvements Checklist

### Phase 1: Sentiment as First-Class Signal
- [ ] **Add sentiment detection function** (rule-based, deterministic)
  - Location: `backend/chatbot_provider.py` or new `backend/sentiment_detector.py`
  - Function: `detect_sentiment(text: str) -> str`
  - Returns: POSITIVE, NEUTRAL, CONFUSED, FRUSTRATED, HOSTILE
- [ ] **Define 5 sentiment states** with clear triggers
  - POSITIVE: Happy, appreciative language
  - NEUTRAL: Normal questions
  - CONFUSED: "what?", "about what", "I don't understand"
  - FRUSTRATED: "I haven't asked", "this is wrong", mild profanity
  - HOSTILE: Strong profanity, direct abuse
- [ ] **Implement sentiment gate before intent routing**
  - Must run BEFORE `detect_intent_priority()`
  - Must have veto power over downstream logic
  - Location: `server.py:866-1026` in `/ask-all-u-bot` endpoint
- [ ] **Create sentiment-aware response templates** (no RAG)
  - CONFUSED: "It seems I may not have explained that clearly. What would you like me to clarify?"
  - FRUSTRATED: "I see this is frustrating. Let's slow down-what were you expecting instead?"
  - HOSTILE: "I'm here to help, but I won't engage with abusive language."
- [ ] **Add state reset logic after emotional stabilization**
  - Reset `last_intent` to None
  - Reset `last_state` to "CONVERSATION"
  - Clear `exit_acknowledged` flag

### Phase 2: Response Mode Layer
- [ ] **Define 3 response modes** (separate from intent)
  - ANSWER_ONLY: Answer what was asked, nothing more
  - PRESENT_SUMMARY: Full portfolio presentation
  - CONVERSATION: Casual, minimal responses
- [ ] **Implement response mode mapping logic**
  ```python
  if state in ["START", "AMBIGUOUS", "SILENT"]:
      response_mode = "CONVERSATION"
  elif state == "INFO":
      response_mode = "ANSWER_ONLY"
  elif explicit_request_for_summary:
      response_mode = "PRESENT_SUMMARY"
  ```
- [ ] **Set default to ANSWER_ONLY** (not PRESENT_SUMMARY)
  - Prevents over-answering
  - Prevents unprompted info dumps
- [ ] **Add response_mode to session metadata**
  - Track per session: `session_metadata[session_id]["response_mode"]`

### Phase 3: Content Filtering Guards
- [ ] **Implement "Answer What Was Asked" guard**
  - Run before sending response
  - Validate response scope matches query scope
- [ ] **Define forbidden sections for ANSWER_ONLY mode**
  ```python
  forbid_sections = [
      "certifications",
      "awards",
      "background",
      "experience summary"
  ]
  ```
- [ ] **Add content scope validation before response generation**
  - Check if response contains forbidden sections
  - Strip or regenerate if scope violation detected
- [ ] **Prevent unprompted topic expansion**
  - No AI/ML mentions unless explicitly asked
  - No awards unless explicitly asked
  - No certifications unless explicitly asked

### Phase 4: Profanity Tolerance Band
- [ ] **Replace binary profanity check with severity levels**
  - Current: Any profanity → ABUSE
  - New: LOW severity → FRUSTRATED, HIGH severity → HOSTILE
- [ ] **Define LOW profanity list** (mild frustration)
  - "shit", "damn", "crap", "oh shit"
  - Should NOT trigger abuse boundary
- [ ] **Define HIGH profanity list** (direct abuse)
  - "fuck you", "fuck off", "go to hell", slurs
  - Should trigger abuse boundary
- [ ] **Implement contextual responses for LOW severity**
  - "Sounds like that was frustrating. Want me to clarify something?"
  - Stay in CONVERSATION state
  - Do NOT escalate tone
- [ ] **Keep boundary responses for HIGH severity only**
  - "I'm here to help, but I won't engage with abusive language."
  - Set `exit_acknowledged` flag

### Phase 5: ACK/SILENT Handling
- [ ] **Detect acknowledgement patterns**
  - "ok", "kk", "fine", "oh kk fine", "got it", "right"
  - Should trigger SILENT state
- [ ] **Implement SILENT state short-circuit**
  ```python
  if state == "SILENT":
      return "Alright. Let me know when you want to continue."
  ```
- [ ] **Return minimal responses for acknowledgements**
  - No portfolio data
  - No new topics
  - No achievements
- [ ] **Prevent content dumping on disengagement signals**
  - "nothing", "no", "nope" should NOT trigger info presentation

### Phase 6: State Transition Fixes
- [ ] **Review `determine_next_state()` logic**
  - Location: `server.py:123-159`
  - Currently: INFO state never downgrades
- [ ] **Add state downgrade paths**
  - INFO → AMBIGUOUS when user shows confusion
  - INFO → CONVERSATION when user acknowledges
  - INFO → EXIT when user disengages
- [ ] **Implement disengagement counter reset on re-engagement**
  - Reset to 0 when user asks new question
  - Only increment on consecutive "nothing", "no", "nope"
- [ ] **Add state transition logging for debugging**
  - Log: Previous state → New state
  - Log: Trigger (intent scores, sentiment, etc.)

### Phase 7: Testing & Validation
- [ ] **Test Case 1**: "oh shit" → calming response, no boundary
  - Expected: "Sounds like that was frustrating. Want me to clarify something?"
  - Should NOT trigger abuse boundary
- [ ] **Test Case 2**: "i haven't asked you this" → reset + clarification
  - Expected: Context reset, clarification offer
  - Should NOT continue dumping info
- [ ] **Test Case 3**: "fuck off" → boundary response
  - Expected: "I'm here to help, but I won't engage with abusive language."
  - Should trigger abuse boundary
- [ ] **Test Case 4**: "ok" → minimal acknowledgment, no info dump
  - Expected: "Alright. Let me know when you want to continue."
  - Should NOT present achievements/awards
- [ ] **Test Case 5**: "what is his blog?" → answer only, no biography
  - Expected: Blog info only, no "Hello! I'm Allu Bot…"
  - Should NOT inject identity/background
- [ ] **Test Case 6**: Conversation flow with multiple state transitions
  - Start → Info → Confused → Info → Silent → Exit
  - Verify smooth transitions without info dumping

### Phase 8: System Prompt Optimization
- [ ] **Review system prompt for presentation bias**
  - Check if prompt encourages "introducing yourself"
  - Check if prompt encourages "comprehensive answers"
- [ ] **Add explicit ANSWER_ONLY instructions**
  - "Answer only what was asked"
  - "Do not provide background unless requested"
  - "Do not expand to related topics unless asked"
- [ ] **Add sentiment awareness instructions**
  - "Detect user frustration and de-escalate"
  - "Prioritize user emotional state over information delivery"
- [ ] **Test prompt changes with edge cases**
  - Verify no regression in normal INFO queries
  - Verify improved behavior on CONFUSED/FRUSTRATED inputs

---

## 📊 Success Metrics

After implementing these improvements, the chatbot should demonstrate:

✅ **Reduced Over-Answering**: No unprompted biography/achievements  
✅ **Better Tone Calibration**: Calm responses to frustration  
✅ **Improved State Transitions**: Smooth INFO → AMBIGUOUS → SILENT flows  
✅ **Contextual Profanity Handling**: "oh shit" doesn't trigger abuse  
✅ **User Control**: Acknowledgements don't trigger info dumps  

**Key Performance Indicators**:
- User frustration signals (per session): Target < 1
- Unprompted topic expansions: Target 0
- Abuse boundary false positives: Target 0
- Average conversation length: Target 3-5 exchanges (not 10+)