#!/usr/bin/env python3
"""
Clean blogs.json file by removing specific categories
"""

import json
import os

# Categories to remove
EXCLUDED_CATEGORIES = [
    'Frontend Development',
    'IoT Development',
    'Blockchain',
    'Databases',
    'Edge Computing',
    'Quantum Computing'
]

# File paths
FRONTEND_BLOGS_PATH = 'frontend/public/data/blogs.json'
BACKEND_TEST_PATH = 'backend/test_blogs_output.json'

def clean_json_file(filepath):
    """Remove blogs with excluded categories from JSON file"""
    if not os.path.exists(filepath):
        print(f"⚠️  File not found: {filepath}")
        return
    
    print(f"\n📂 Processing: {filepath}")
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Handle different JSON structures
        if 'blogs' in data and isinstance(data['blogs'], list):
            original_count = len(data['blogs'])
            data['blogs'] = [
                blog for blog in data['blogs']
                if blog.get('category') not in EXCLUDED_CATEGORIES
            ]
            removed = original_count - len(data['blogs'])
        elif isinstance(data, list):
            original_count = len(data)
            data = [
                blog for blog in data
                if blog.get('category') not in EXCLUDED_CATEGORIES
            ]
            removed = original_count - len(data)
        else:
            print(f"⚠️  Unknown JSON structure in {filepath}")
            return
        
        print(f"   ✅ Removed {removed} blogs")
        print(f"   📊 Remaining: {len(data.get('blogs', data))} blogs")
        
        # Write back to file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"   💾 Saved cleaned file")
        
    except Exception as e:
        print(f"   ❌ Error processing {filepath}: {e}")

def main():
    print("="*60)
    print("🧹 CLEANING LOCAL JSON FILES")
    print("="*60)
    print("\nRemoving blogs from these categories:")
    for cat in EXCLUDED_CATEGORIES:
        print(f"  ❌ {cat}")
    
    # Clean frontend file
    clean_json_file(FRONTEND_BLOGS_PATH)
    
    # Clean backend test file
    clean_json_file(BACKEND_TEST_PATH)
    
    print("\n" + "="*60)
    print("✅ Cleanup complete!")
    print("="*60)

if __name__ == "__main__":
    main()
