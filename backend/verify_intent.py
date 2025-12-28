
import sys
import os
import unittest

# Add current directory to path so we can import server
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from server import detect_intent_priority

class TestIntentRouting(unittest.TestCase):
    def test_checklist_cases(self):
        test_cases = [
            ("hello", "conversation", "Basic Greeting"),
            ("oh is it", "conversation", "Ambiguous/Filler"),
            ("nothing", "conversation", "Dismissal"),
            ("nah", "conversation", "Dismissal (Slang)"),
            ("relavnet", "conversation", "Misspelled 'Relevant' Feedback"),
            ("who is Althaf", "profile", "Profile Query"),
            ("show me AWS projects", "aws_projects", "Strong AWS Intent"),
            ("hello tell me about aws", "aws_projects", "Mixed Greeting + AWS"),
            ("random gibberish xyz", "conversation", "Unknown -> Safe Mode Fallback")
        ]
        
        print("\n--- RUNNING INTENT CHECKLIST VALIDATION ---")
        for query, expected_intent, desc in test_cases:
            intent, sentiment = detect_intent_priority(query)
            status = "✅ PASS" if intent == expected_intent else f"❌ FAIL (Got {intent})"
            print(f"[{status}] Query: '{query}' -> Expected: {expected_intent}. Desc: {desc}")
            
            # Assertions for automated failure
            self.assertEqual(intent, expected_intent, f"Failed on '{query}'")

if __name__ == '__main__':
    unittest.main()
