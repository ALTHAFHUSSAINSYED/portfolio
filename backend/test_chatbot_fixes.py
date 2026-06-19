#!/usr/bin/env python3
"""
Chatbot Fixes Validation Script
Tests all 7 golden test cases from the behavioral improvements review.

NOTE (Task 14): This script tests the chatbot endpoint which automatically uses
the correct ChromaDB collection based on USE_LEGACY_COLLECTIONS env var:
- USE_LEGACY_COLLECTIONS=false (default): Uses portfolio_master with metadata filters
- USE_LEGACY_COLLECTIONS=true: Falls back to 3 separate collections (portfolio, Projects_data, Blogs_data)

Run this on EC2 after deploying the fixes.
Usage: python test_chatbot_fixes.py
"""

import requests
import json
import time
from typing import Dict, List, Tuple

# Configuration
API_URL = "http://localhost:8000/api/ask-all-u-bot"
SESSION_ID = "test_session_" + str(int(time.time()))

# ANSI color codes for output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"

class ChatbotTester:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.session_id = SESSION_ID
        
    def send_message(self, message: str) -> Dict:
        """Send message to chatbot and return response"""
        try:
            response = requests.post(
                API_URL,
                json={"message": message, "session_id": self.session_id},
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def validate_response(self, test_name: str, message: str, expected_keywords: List[str], 
                         forbidden_keywords: List[str], expected_source: str = None) -> bool:
        """
        Validate chatbot response against expectations
        
        Args:
            test_name: Name of the test
            message: User message to send
            expected_keywords: Keywords that SHOULD appear in response
            forbidden_keywords: Keywords that SHOULD NOT appear in response
            expected_source: Expected source (e.g., "SentimentGate")
        """
        print(f"\n{BLUE}{'='*80}{RESET}")
        print(f"{BLUE}Test: {test_name}{RESET}")
        print(f"{YELLOW}Input: {message}{RESET}")
        
        result = self.send_message(message)
        
        if "error" in result:
            print(f"{RED}❌ FAILED - API Error: {result['error']}{RESET}")
            self.failed += 1
            return False
        
        reply = result.get("reply", "")
        source = result.get("source", "")
        
        print(f"{YELLOW}Response: {reply}{RESET}")
        print(f"{YELLOW}Source: {source}{RESET}")
        
        # Check expected keywords
        missing_keywords = [kw for kw in expected_keywords if kw.lower() not in reply.lower()]
        if missing_keywords:
            print(f"{RED}❌ FAILED - Missing expected keywords: {missing_keywords}{RESET}")
            self.failed += 1
            return False
        
        # Check forbidden keywords
        found_forbidden = [kw for kw in forbidden_keywords if kw.lower() in reply.lower()]
        if found_forbidden:
            print(f"{RED}❌ FAILED - Found forbidden keywords: {found_forbidden}{RESET}")
            self.failed += 1
            return False
        
        # Check expected source
        if expected_source and source != expected_source:
            print(f"{RED}❌ FAILED - Expected source '{expected_source}', got '{source}'{RESET}")
            self.failed += 1
            return False
        
        print(f"{GREEN}✅ PASSED{RESET}")
        self.passed += 1
        return True
    
    def run_all_tests(self):
        """Run all 7 golden test cases"""
        print(f"\n{BLUE}{'='*80}{RESET}")
        print(f"{BLUE}CHATBOT BEHAVIORAL FIXES VALIDATION{RESET}")
        print(f"{BLUE}Session ID: {self.session_id}{RESET}")
        print(f"{BLUE}{'='*80}{RESET}")
        
        # Test 1: "oh shit" → calming response, no boundary
        self.validate_response(
            test_name="Test 1: LOW Profanity (Frustrated)",
            message="oh shit",
            expected_keywords=["wasn't what you expected", "clarify"],
            forbidden_keywords=["abusive", "disrespectful", "won't engage"],
            expected_source="SentimentGate"
        )
        
        time.sleep(5)
        
        # Test 2: "i haven't asked you this" → reset + clarification
        self.validate_response(
            test_name="Test 2: Frustration Signal",
            message="i haven't asked you this",
            expected_keywords=["wasn't what you expected", "clarify"],
            forbidden_keywords=["awards", "achievements", "certifications", "software engineer"],
            expected_source="SentimentGate"
        )
        
        time.sleep(5)
        
        # Test 3: "fuck off" → boundary response
        self.validate_response(
            test_name="Test 3: HIGH Profanity (Hostile)",
            message="fuck off",
            expected_keywords=["can't continue", "disrespectful"],
            forbidden_keywords=["clarify", "help you with"],
            expected_source="SentimentGate"
        )
        
        # Reset session for next tests
        self.session_id = "test_session_" + str(int(time.time()))
        time.sleep(5)
        
        # Test 4: "ok" → minimal acknowledgment, no info dump
        self.validate_response(
            test_name="Test 4: Filler/Acknowledgement",
            message="ok",
            expected_keywords=["👍"],  # Emoji response
            forbidden_keywords=["achievements", "awards", "projects", "software engineer", "details"]
        )
        
        time.sleep(5)
        
        # Test 5: "what is his blog?" → answer only, no biography
        self.validate_response(
            test_name="Test 5: Specific Question (No Biography)",
            message="what is his blog?",
            expected_keywords=["Kubernetes"], # Consistent subject matter
            forbidden_keywords=["software engineer", "passionate about", "Hello! I'm Allu Bot"]
        )
        
        time.sleep(5)
        
        # Test 6: Conversation flow with state transitions
        print(f"\n{BLUE}{'='*80}{RESET}")
        print(f"{BLUE}Test 6: Multi-State Conversation Flow{RESET}")
        print(f"{BLUE}{'='*80}{RESET}")
        
        # Reset session
        self.session_id = "test_session_" + str(int(time.time()))
        
        # START state
        self.validate_response(
            test_name="Test 6a: START State (Greeting)",
            message="hey",
            expected_keywords=["projects", "blogs", "experience"],
            forbidden_keywords=["software engineer", "achievements"]
        )
        
        time.sleep(5)
        
        # INFO state
        self.validate_response(
            test_name="Test 6b: INFO State (Project Query)",
            message="tell me about his projects",
            expected_keywords=["built", "automated"],  # Flexible - accepts various project descriptions
            forbidden_keywords=[]  # Just checking it responds
        )
        
        time.sleep(5)
        
        # CONFUSED → AMBIGUOUS
        self.validate_response(
            test_name="Test 6c: CONFUSED State",
            message="what?",
            expected_keywords=["explained", "clarify"],
            forbidden_keywords=["projects", "achievements"],
            expected_source="SentimentGate"
        )
        
        time.sleep(5)
        
        # SILENT state
        self.validate_response(
            test_name="Test 6d: SILENT State (Filler)",
            message="hmm",
            expected_keywords=["👍"],
            forbidden_keywords=["projects", "achievements", "details"]
        )
        
        time.sleep(5)
        
        # EXIT state
        self.validate_response(
            test_name="Test 6e: EXIT State (Goodbye)",
            message="bye",
            expected_keywords=["Understood", "come back"],
            forbidden_keywords=["projects", "achievements"]
        )
        
        time.sleep(5)
        
        # Post-EXIT (should be silence)
        result = self.send_message("hello?")
        if "error" in result:
             print(f"{RED}❌ Test 6f: Post-EXIT Silence - FAILED (API Error: {result['error']}){RESET}")
             self.failed += 1
        else:
            reply = result.get("reply", "NOT_EMPTY")
            if not reply:
                print(f"{GREEN}✅ Test 6f: Post-EXIT Silence - PASSED{RESET}")
                self.passed += 1
            else:
                print(f"{RED}❌ Test 6f: Post-EXIT Silence - FAILED (got: '{reply}'){RESET}")
                self.failed += 1
        
        # Test 7: Verify sentiment detection doesn't break normal queries
        self.session_id = "test_session_" + str(int(time.time()))
        time.sleep(5)  # Longer delay to avoid rate limiting
        
        self.validate_response(
            test_name="Test 7: Normal Query (No False Positives)",
            message="what are his skills?",
            expected_keywords=["Linux", "Terraform"], # Consistent skills
            forbidden_keywords=["frustrated", "clarify", "wasn't what you expected"]
        )
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        total = self.passed + self.failed
        pass_rate = (self.passed / total * 100) if total > 0 else 0
        
        print(f"\n{BLUE}{'='*80}{RESET}")
        print(f"{BLUE}TEST SUMMARY{RESET}")
        print(f"{BLUE}{'='*80}{RESET}")
        print(f"Total Tests: {total}")
        print(f"{GREEN}Passed: {self.passed}{RESET}")
        print(f"{RED}Failed: {self.failed}{RESET}")
        print(f"Pass Rate: {pass_rate:.1f}%")
        
        if self.failed == 0:
            print(f"\n{GREEN}{'='*80}{RESET}")
            print(f"{GREEN}🎉 ALL TESTS PASSED! Chatbot fixes are working correctly.{RESET}")
            print(f"{GREEN}{'='*80}{RESET}")
        else:
            print(f"\n{RED}{'='*80}{RESET}")
            print(f"{RED}⚠️  SOME TESTS FAILED. Review the output above for details.{RESET}")
            print(f"{RED}{'='*80}{RESET}")

if __name__ == "__main__":
    print(f"{BLUE}Starting Chatbot Validation Tests...{RESET}")
    print(f"{YELLOW}Make sure the backend server is running on localhost:8000{RESET}\n")
    
    tester = ChatbotTester()
    
    try:
        tester.run_all_tests()
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Tests interrupted by user{RESET}")
    except Exception as e:
        print(f"\n{RED}Fatal error: {e}{RESET}")
        import traceback
        traceback.print_exc()
