"""
Task 20 Verification Script
Validates that auto-blogger is correctly configured for portfolio_master migration
"""

import os
import sys
import chromadb
from dotenv import load_dotenv

# Load environment
load_dotenv()

def verify_chromadb_connection():
    """Verify ChromaDB connection and portfolio_master collection exists"""
    print("=" * 60)
    print("TASK 20 VERIFICATION: Auto-Blogger Migration Validation")
    print("=" * 60)
    
    try:
        # Connect to ChromaDB
        chroma_api_key = os.getenv("CHROMA_API_KEY")
        chroma_tenant = os.getenv("CHROMA_TENANT_ID")
        chroma_db = os.getenv("CHROMA_DATABASE", "Development")
        
        if not chroma_api_key:
            print("❌ CHROMA_API_KEY not found in environment")
            return False
            
        client = chromadb.HttpClient(
            host="api.trychroma.com",
            ssl=True,
            headers={
                "x-chroma-token": chroma_api_key,
                "x-tenant": chroma_tenant,
                "x-database": chroma_db
            }
        )
        
        print(f"✅ ChromaDB connection established")
        print(f"   Tenant: {chroma_tenant}")
        print(f"   Database: {chroma_db}")
        
        # Check portfolio_master collection
        try:
            collection = client.get_collection("portfolio_master")
            total_count = collection.count()
            print(f"\n✅ portfolio_master collection found")
            print(f"   Total items: {total_count}")
            
            # Count by category
            try:
                # Get all items with metadata
                all_items = collection.get(include=['metadatas'])
                
                category_counts = {}
                for metadata in all_items['metadatas']:
                    cat = metadata.get('category', 'unknown')
                    category_counts[cat] = category_counts.get(cat, 0) + 1
                
                print(f"\n📊 Category Distribution:")
                for cat, count in sorted(category_counts.items()):
                    print(f"   - {cat}: {count} items")
                    
            except Exception as e:
                print(f"   ⚠️ Could not fetch category distribution: {e}")
            
        except Exception as e:
            print(f"❌ portfolio_master collection not found: {e}")
            return False
            
        # Check if old collections still exist
        print(f"\n🔍 Checking for legacy collections...")
        legacy_collections = ["Blogs_data", "Projects_data", "portfolio"]
        found_legacy = []
        
        for legacy_col in legacy_collections:
            try:
                client.get_collection(legacy_col)
                found_legacy.append(legacy_col)
                print(f"   ⚠️ {legacy_col} still exists (should be deleted after 7-day validation)")
            except:
                print(f"   ✅ {legacy_col} not found (already deleted or never existed)")
        
        if found_legacy:
            print(f"\n⚠️ Legacy collections found: {', '.join(found_legacy)}")
            print(f"   These should be deleted after 7-day validation (Task 22)")
        
        return True
        
    except Exception as e:
        print(f"❌ ChromaDB connection failed: {e}")
        return False

def verify_publisher_config():
    """Verify publisher.py is configured correctly"""
    print(f"\n{'=' * 60}")
    print("PUBLISHER CONFIGURATION CHECK")
    print("=" * 60)
    
    try:
        with open('backend/auto_blogger/publisher.py', 'r') as f:
            content = f.read()
            
        # Check for portfolio_master usage
        if 'portfolio_master' in content:
            print("✅ Publisher uses portfolio_master collection")
        else:
            print("❌ Publisher does not reference portfolio_master")
            return False
            
        # Check metadata structure
        if '"category": "blog"' in content or "'category': 'blog'" in content:
            print("✅ Publisher sets category='blog' in metadata")
        else:
            print("⚠️ Publisher may not be setting category='blog' correctly")
            
        if 'subcategory' in content:
            print("✅ Publisher preserves original category as subcategory")
        else:
            print("⚠️ Publisher may not be preserving original category")
            
        # Check for dual-write (should NOT exist anymore)
        if 'Blogs_data' in content and 'collections_to_write' in content:
            print("⚠️ Publisher may still have dual-write code (check manually)")
        else:
            print("✅ Publisher appears to be master-only (no dual-write)")
            
        return True
        
    except Exception as e:
        print(f"❌ Could not verify publisher: {e}")
        return False

def verify_cleanup_config():
    """Verify cleanup.py is configured correctly"""
    print(f"\n{'=' * 60}")
    print("CLEANUP CONFIGURATION CHECK")
    print("=" * 60)
    
    try:
        with open('backend/auto_blogger/cleanup.py', 'r') as f:
            content = f.read()
            
        # Check for portfolio_master usage
        if 'portfolio_master' in content:
            print("✅ Cleanup uses portfolio_master collection")
        else:
            print("❌ Cleanup still uses old collection (needs update)")
            return False
            
        # Check for category filter
        if "category" in content and "blog" in content:
            print("✅ Cleanup has category filter for safety")
        else:
            print("⚠️ Cleanup may not have category='blog' filter")
            
        return True
        
    except Exception as e:
        print(f"❌ Could not verify cleanup: {e}")
        return False

def main():
    results = {
        'chromadb': verify_chromadb_connection(),
        'publisher': verify_publisher_config(),
        'cleanup': verify_cleanup_config()
    }
    
    print(f"\n{'=' * 60}")
    print("TASK 20 VERIFICATION SUMMARY")
    print("=" * 60)
    
    all_passed = all(results.values())
    
    for component, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{component.upper():20s}: {status}")
    
    if all_passed:
        print(f"\n🎉 All checks passed! Auto-blogger is ready for Task 20.")
        print(f"\n📅 Next Steps:")
        print(f"   1. Monitor tomorrow's blog generation (Jan 3, 7:00 AM IST)")
        print(f"   2. Verify blog appears in portfolio_master with category='blog'")
        print(f"   3. Check email notification for success")
        print(f"   4. Run cleanup test to ensure old blogs are deleted correctly")
        return 0
    else:
        print(f"\n❌ Some checks failed. Please fix the issues above before proceeding.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
