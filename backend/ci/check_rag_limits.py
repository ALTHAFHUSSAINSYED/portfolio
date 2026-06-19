
import sys
import re
from pathlib import Path

def check_rag_limits():
    """
    CI Guard to ensure Search Visibility (Candidate Limit) > Packet Safety (Injection Limit).
    Also detects regression in Date Anchoring logic.
    """
    server_path = Path(__file__).parent.parent / 'server.py'
    
    if not server_path.exists():
        print(f"❌ Critical: {server_path} not found.")
        sys.exit(1)
        
    with open(server_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    print(f"🔍 Analyzing {server_path} for RAG Guardrails...")
    
    # 1. Capture Limits (Regex)
    # Looking for: CANDIDATE_LIMIT = 5  and  INJECTION_LIMIT = 2
    # We look for the "blogs" specific block if possible, or general definitions
    
    cand_match = re.search(r'CANDIDATE_LIMIT\s*=\s*(\d+)', content)
    inj_match = re.search(r'INJECTION_LIMIT\s*=\s*(\d+)', content)
    
    if not cand_match:
        print("❌ FAIL: Could not find 'CANDIDATE_LIMIT' definition.")
        sys.exit(1)
        
    if not inj_match:
        print("❌ FAIL: Could not find 'INJECTION_LIMIT' definition.")
        sys.exit(1)
        
    c_limit = int(cand_match.group(1))
    i_limit = int(inj_match.group(1))
    
    print(f"  • CANDIDATE_LIMIT found: {c_limit}")
    print(f"  • INJECTION_LIMIT found: {i_limit}")
    
    if c_limit <= i_limit:
        print(f"❌ FAIL: Visibility Regression! CANDIDATE_LIMIT ({c_limit}) must be greater than INJECTION_LIMIT ({i_limit}).")
        print("   -> Fix: Increase Retrieval Candidates to ensure date/relevance sorting works before clamping.")
        sys.exit(1)
    else:
        print("  ✅ Limit Split Guard Passed.")

    # 2. Check for Date Anchoring Logic
    if "filter_blogs_by_date" not in content:
        print("❌ FAIL: 'filter_blogs_by_date' function missing. Date Anchoring logic was removed!")
        sys.exit(1)
    
    if "normalize_blog_query" not in content:
        print("❌ FAIL: 'normalize_blog_query' function missing.")
        sys.exit(1)
        
    print("  ✅ Logic Integrity Guard Passed.")
    print("\n🎉 RAG Compliance Check Passed.")
    sys.exit(0)

if __name__ == "__main__":
    check_rag_limits()
