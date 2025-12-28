
import pytest
from server import detect_intent_priority

def test_conversational_inputs():
    """Verify strong conversational/dismissal inputs skip RAG"""
    intent, sentiment, scores = detect_intent_priority("hello")
    assert intent == "conversation"
    
    intent, sentiment, scores = detect_intent_priority("nothing")
    assert intent == "conversation"
    
    intent, sentiment, scores = detect_intent_priority("bye")
    assert intent == "conversation"

def test_ambiguous_inputs_fail_safe():
    """Verify low-confidence inputs default to conversation (Safety Threshold)"""
    intent, sentiment, scores = detect_intent_priority("os is it") # "os" typoes "oh"
    assert intent == "conversation"

    intent, sentiment, scores = detect_intent_priority("random gibberish 123") 
    assert intent == "conversation"

def test_domain_intents():
    """Verify strong domain keywords trigger specific intents"""
    intent, sentiment, scores = detect_intent_priority("show me aws projects")
    assert intent == "aws_projects"
    
    intent, sentiment, scores = detect_intent_priority("tell me about java projects")
    assert intent == "projects"
    
    intent, sentiment, scores = detect_intent_priority("write a blog about react")
    assert intent == "blogs"

def test_profile_fallback():
    """Verify profile queries routing"""
    intent, sentiment, scores = detect_intent_priority("who is althaf")
    assert intent == "profile"
    
    intent, sentiment, scores = detect_intent_priority("what is your experience")
    assert intent == "profile"
@pytest.mark.parametrize("query,expected_intent,expected_priority", [
    ("hello", "conversation", "neutral"),
    ("what projects have you worked on", "projects", "neutral"),
    ("show me aws infrastructure", "aws_projects", "neutral"),
    ("who is althaf", "profile", "neutral"),
    ("nothing much", "conversation", "closing"), # Expect closing sentiment
])
def test_intent_detection(query, expected_intent, expected_priority):
    intent, priority, scores = detect_intent_priority(query)
    assert intent == expected_intent
    # For closing, we check priority is closing. For others, neutral.
    # Note: Logic was updated to assume neutral if not specified in test
    # But closing check is explicit
    if expected_priority:
         assert priority == expected_priority
         
def test_mixed_intent_priority():
    # "hello" (+3) vs "aws" (+10) -> AWS wins
    intent, priority, scores = detect_intent_priority("hello tell me about aws")
    assert intent == "aws_projects"
