
import pytest
from server import detect_intent_priority

def test_conversational_inputs():
    """Verify strong conversational/dismissal inputs skip RAG"""
    intent, sentiment = detect_intent_priority("hello")
    assert intent == "conversation"
    
    intent, sentiment = detect_intent_priority("nothing")
    assert intent == "conversation"
    
    intent, sentiment = detect_intent_priority("bye")
    assert intent == "conversation"

def test_ambiguous_inputs_fail_safe():
    """Verify low-confidence inputs default to conversation (Safety Threshold)"""
    intent, sentiment = detect_intent_priority("os is it") # "os" typoes "oh"
    assert intent == "conversation"

    intent, sentiment = detect_intent_priority("random gibberish 123") 
    assert intent == "conversation"

def test_domain_intents():
    """Verify strong domain keywords trigger specific intents"""
    intent, sentiment = detect_intent_priority("show me aws projects")
    assert intent == "aws_projects"
    
    intent, sentiment = detect_intent_priority("tell me about java projects")
    assert intent == "projects"
    
    intent, sentiment = detect_intent_priority("write a blog about react")
    assert intent == "blogs"

def test_profile_fallback():
    """Verify profile queries routing"""
    intent, sentiment = detect_intent_priority("who is althaf")
    assert intent == "profile"
    
    intent, sentiment = detect_intent_priority("what is your experience")
    assert intent == "profile"

def test_mixed_intent_priority():
    """Verify Domain > Conversation (when both present)"""
    # "Hello" (3) vs "AWS" (5) -> Winner: AWS
    intent, sentiment = detect_intent_priority("hello tell me about aws")
    assert intent == "aws_projects"
