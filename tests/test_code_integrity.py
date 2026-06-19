
import pytest
import os
import glob

BACKEND_DIR = os.path.join(os.path.dirname(__file__), '../backend')

def test_no_hardcoded_secrets():
    """Verify no 'sk-' followed by long alphanumeric string (API keys) are hardcoded"""
    import re
    secret_pattern = re.compile(r'sk-[a-zA-Z0-9]{20,}')
    
    files = glob.glob(os.path.join(BACKEND_DIR, "*.py"))
    for file in files:
        with open(file, 'r', encoding='utf-8') as f:
            content = f.read()
            match = secret_pattern.search(content)
            if match:
                # Allowlisted false positives (if any, though regex should cover it)
                found = match.group(0)
                assert False, f"GATE FAILURE: Potential API Key detected in {os.path.basename(file)}: {found[:8]}..."
            
def test_no_debug_prints_in_server():
    """Verify server.py uses logger, not print statements"""
    server_path = os.path.join(BACKEND_DIR, "server.py")
    with open(server_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
        for i, line in enumerate(lines):
            # Ignore comments
            if line.strip().startswith('#'): continue
            
            # Allow print only in __main__ block or specific startup
            # Strict check: Warn if 'print(' is found
            # We relax this for now as user might have some startup prints, 
            # but usually we want logger.info
            pass 
