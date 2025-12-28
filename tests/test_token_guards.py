
import pytest
# Static Check for now as we might not be able to instantiate the full provider without API keys in CI env
import os

PROVIDER_PATH = os.path.join(os.path.dirname(__file__), '../backend/chatbot_provider.py')

def test_token_constants():
    """Verify Max Input/Output Token constants are within safe budget"""
    with open(PROVIDER_PATH, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Check MAX_INPUT_TOKENS
    import re
    input_match = re.search(r'MAX_INPUT_TOKENS\s*=\s*(\d+)', content)
    if input_match:
        max_in = int(input_match.group(1))
        assert max_in <= 4000, f"GATE FAILURE: Input Budget {max_in} > 4000"
    
    # Check MAX_OUTPUT_TOKENS
    output_match = re.search(r'MAX_OUTPUT_TOKENS\s*=\s*(\d+)', content)
    if output_match:
        max_out = int(output_match.group(1))
        assert max_out <= 1000, f"GATE FAILURE: Output Budget {max_out} > 1000"
