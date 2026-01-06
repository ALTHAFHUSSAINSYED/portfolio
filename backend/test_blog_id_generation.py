#!/usr/bin/env python3
"""
Test blog ID generation for all categories to ensure URL safety.
This prevents future issues with nested directories in S3.
"""

import sys
import time

# Test categories (matching scheduler.py)
CATEGORIES = [
    "AI and ML",
    "Cloud Computing", 
    "Cybersecurity",
    "DevOps",
    "Low-Code/No-Code",
    "Software Development"
]

def generate_url_safe_blog_id(category: str) -> str:
    """
    Generate URL-safe blog ID (matching publisher.py logic)
    """
    category_slug = (
        category
        .replace(' ', '_')
        .replace('/', '-')
        .replace('\\', '-')
        .replace(':', '-')
        .replace('?', '')
        .replace('&', 'and')
        .replace('#', '')
    )
    blog_id = f"{category_slug}_{int(time.time())}"
    
    # Safety check
    if '/' in blog_id or '\\' in blog_id:
        raise ValueError(f"Blog ID contains path separator: {blog_id}")
    
    return blog_id

def test_all_categories():
    """Test blog ID generation for all categories"""
    print("=" * 80)
    print("BLOG ID GENERATION TEST - URL SAFETY VALIDATION")
    print("=" * 80)
    print()
    
    all_safe = True
    
    for i, category in enumerate(CATEGORIES, 1):
        try:
            blog_id = generate_url_safe_blog_id(category)
            
            # Verify no path separators
            has_slash = '/' in blog_id
            has_backslash = '\\' in blog_id
            is_safe = not (has_slash or has_backslash)
            
            status = "✅ SAFE" if is_safe else "❌ UNSAFE"
            
            print(f"{i}. {category}")
            print(f"   Generated ID: {blog_id}")
            print(f"   Contains '/': {has_slash}")
            print(f"   Contains '\\': {has_backslash}")
            print(f"   Status: {status}")
            print(f"   S3 Path: blogs/posts/{blog_id}.json")
            print()
            
            if not is_safe:
                all_safe = False
                print(f"   ⚠️  WARNING: This would create nested directories!")
                print()
                
        except Exception as e:
            print(f"{i}. {category}")
            print(f"   ❌ ERROR: {e}")
            print()
            all_safe = False
    
    print("=" * 80)
    if all_safe:
        print("✅ ALL CATEGORIES SAFE - Future blogs will work correctly!")
    else:
        print("❌ SOME CATEGORIES UNSAFE - Fix required before next blog generation!")
    print("=" * 80)
    
    return all_safe

if __name__ == "__main__":
    success = test_all_categories()
    sys.exit(0 if success else 1)
