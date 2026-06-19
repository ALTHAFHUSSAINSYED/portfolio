
import sys
import os
import re

# Simulate the function logic exactly to see scores
def detect_intent_debug(text):
    print(f"DEBUG: Processing '{text}'")
    
    # 1. NORMALIZE
    text = text.lower().strip()
    text = re.sub(r'[^a-z0-9\s]', '', text)
    text = re.sub(r'\s+', ' ', text)
    print(f"DEBUG: Normalized '{text}'")
    
    scores = {
        "conversation": 0,
        "aws_projects": 0,
        "projects": 0,
        "blogs": 0,
        "profile": 0
    }
    
    conversational_triggers = [
        'hi', 'hello', 'hey', 'good morning', 'hola', 'greetings',
        'bye', 'goodbye', 'thanks', 'ok', 'okay', 'cool', 'good',
        'oh', 'ah', 'wow', 'hmm', 'right', 'got it',
        'nothing', 'nothin', 'no', 'nope', 'nah', 'stop', 'cancel'
    ]
    
    if any(t == text or text.startswith(t + " ") for t in conversational_triggers):
        scores["conversation"] += 3
        print(f"DEBUG: Hit Conversational Trigger (+3)")

    if "relev" in text or "relav" in text:
        scores["conversation"] += 3
        return "conversation", "frustrated"

    if any(k in text for k in ["who", "about", "bio", "background", "resume", "experience", "skill", "contact", "email"]):
        scores["profile"] += 4
        print(f"DEBUG: Hit Profile Trigger (+4)")
        
    if any(k in text for k in ["project", "built", "work", "develop", "portfolio", "app", "website"]):
        scores["projects"] += 5
        print(f"DEBUG: Hit Projects Trigger (+5)")
        
    if any(k in text for k in ["aws", "cloud", "terraform", "deploy", "infrastructure", "pipeline", "ci/cd"]):
        scores["aws_projects"] += 5
        print(f"DEBUG: Hit AWS Trigger (+5)")
        
    if any(k in text for k in ["blog", "article", "write", "post", "read"]):
        scores["blogs"] += 5
        print(f"DEBUG: Hit Blogs Trigger (+5)")

    best_intent, score = max(scores.items(), key=lambda x: x[1])
    print(f"DEBUG: Final Scores: {scores}")
    print(f"DEBUG: Winner: {best_intent} ({score})")
    
    return best_intent

detect_intent_debug("hello tell me about aws")
