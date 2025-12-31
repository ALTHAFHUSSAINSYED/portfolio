import sys
import os
import unittest
from unittest.mock import MagicMock, patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock optional dependencies to ensure test runs even if some libs are missing
sys.modules["google"] = MagicMock()
sys.modules["google.genai"] = MagicMock()
sys.modules["gradio_client"] = MagicMock()

from backend.chatbot_provider import ChatbotProvider, COMPILED_PROMPT_TEMPLATE
from backend.middleware.response_sanitizer import strip_apology_boilerplate

class TestPhase9(unittest.TestCase):

    # --- 1. Middleware Test ---
    def test_apology_strip(self):
        bad_text = "It seems I may not have explained well. Althaf is a developer."
        clean = strip_apology_boilerplate(bad_text)
        self.assertNotIn("It seems I may not have", clean)
        self.assertEqual(clean, "explained well. Althaf is a developer.")

    def test_apology_strip_start(self):
        bad_text = "Apologies for the confusion, here is the answer."
        clean = strip_apology_boilerplate(bad_text)
        self.assertTrue(clean.endswith("here is the answer."))

    # --- 2. Logic Tests ---
    def test_is_behavior_question(self):
        cb = ChatbotProvider()
        self.assertTrue(cb.is_behavior_question("why did you say that?"))
        self.assertTrue(cb.is_behavior_question("why earlier you said X?"))
        self.assertFalse(cb.is_behavior_question("what is his skill?"))

    def test_explain_decision(self):
        cb = ChatbotProvider()
        # Test Blog Logic
        reason = cb.explain_previous_decision("why recent blog changed?", [])
        self.assertIn("date filter", reason)
        
        # Test Intent Logic
        reason = cb.explain_previous_decision("why did you change answer?", [])
        self.assertIn("intent became specific", reason)

    # --- 3. Prompt Normalization Check ---
    def test_prompt_template_exists(self):
        self.assertIn("IDENTITY CONTRACT", COMPILED_PROMPT_TEMPLATE)
        self.assertIn("No apologies", COMPILED_PROMPT_TEMPLATE)

if __name__ == '__main__':
    unittest.main()
