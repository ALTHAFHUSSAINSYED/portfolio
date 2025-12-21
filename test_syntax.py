import sys

file_path = "backend/server.py"

print(f"🔍 Checking {file_path} for invisible errors...")

try:
    with open(file_path, 'rb') as f:
        raw_content = f.read()

    # 1. Check for Non-Breaking Spaces (The "Invisible Killer")
    if b'\xc2\xa0' in raw_content or b'\xa0' in raw_content:
        print("❌ FAIL: Found 'Non-Breaking Spaces' (NBSP).")
        print("   -> These look like spaces but cause IndentationErrors.")
        print("   -> You MUST clean the file.")
    else:
        print("✅ PASS: No invisible NBSP characters found.")

    # 2. Check for Mixed Tabs and Spaces
    if b'\t' in raw_content and b' ' in raw_content:
         print("⚠️ WARNING: File contains both Tabs and Spaces. This can cause errors.")

    # 3. Try to Compile (The Ultimate Test)
    with open(file_path, 'r', encoding='utf-8') as f:
        source = f.read()

    compile(source, file_path, 'exec')
    print("✅ PASS: Python Syntax is VALID. The file is safe to run!")

except IndentationError as e:
    print(f"❌ FAIL: Indentation Error at line {e.lineno}:")
    print(f"   {e.msg}")
except SyntaxError as e:
    print(f"❌ FAIL: Syntax Error at line {e.lineno}:")
    print(f"   {e.msg}")
except FileNotFoundError:
    print(f"❌ FAIL: Could not find {file_path}")
except Exception as e:
    print(f"❌ FAIL: Unexpected error: {e}")