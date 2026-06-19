"""
Task 20 Monitoring Script
Monitors auto-blogger executions and verifies portfolio_master integration
Run this after each blog generation to validate Task 20 completion
"""

import os
import chromadb
from datetime import datetime, timedelta
from dotenv import load_dotenv
import pytz

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env.local'))

IST = pytz.timezone('Asia/Kolkata')

def check_latest_blog():
    """Check the latest blog in portfolio_master"""
    print("=" * 70)
    print(f"TASK 20 MONITORING: Latest Blog Check ({datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S IST')})")
    print("=" * 70)
    
    try:
        # Connect to ChromaDB
        chroma_api_key = os.getenv("CHROMA_API_KEY")
        chroma_tenant = os.getenv("CHROMA_TENANT_ID")
        chroma_db = os.getenv("CHROMA_DATABASE", "Development")
        
        client = chromadb.HttpClient(
            host="api.trychroma.com",
            ssl=True,
            headers={
                "x-chroma-token": chroma_api_key,
                "x-tenant": chroma_tenant,
                "x-database": chroma_db
            }
        )
        
        collection = client.get_collection("portfolio_master")
        
        # Get all blog items (category='blog')
        all_items = collection.get(include=['metadatas'])
        
        blog_items = []
        for idx, metadata in enumerate(all_items['metadatas']):
            if metadata.get('category') == 'blog':
                blog_items.append({
                    'id': all_items['ids'][idx],
                    'metadata': metadata
                })
        
        if not blog_items:
            print("❌ No blogs found in portfolio_master with category='blog'")
            return False
        
        # Sort by timestamp (newest first)
        blog_items.sort(key=lambda x: int(x['metadata'].get('timestamp', 0)), reverse=True)
        
        print(f"\n📊 Total blogs in portfolio_master: {len(blog_items)}")
        print(f"\n🆕 Latest 5 Blogs:")
        print("-" * 70)
        
        for idx, blog in enumerate(blog_items[:5], 1):
            metadata = blog['metadata']
            timestamp = int(metadata.get('timestamp', 0))
            published_date = datetime.fromtimestamp(timestamp, IST)
            
            # Check if published today
            today = datetime.now(IST).date()
            is_today = published_date.date() == today
            
            status_icon = "🆕" if is_today else "📄"
            
            print(f"\n{status_icon} Blog #{idx}")
            print(f"   ID: {blog['id']}")
            print(f"   Title: {metadata.get('title', 'N/A')}")
            print(f"   Category: {metadata.get('category', 'N/A')}")
            print(f"   Subcategory: {metadata.get('subcategory', 'N/A')}")
            print(f"   Published: {published_date.strftime('%Y-%m-%d %H:%M:%S IST')}")
            print(f"   URL: {metadata.get('url', 'N/A')}")
            
            # Validation checks
            validation_passed = True
            validation_issues = []
            
            if metadata.get('category') != 'blog':
                validation_issues.append(f"❌ Category should be 'blog', got '{metadata.get('category')}'")
                validation_passed = False
            
            if not metadata.get('subcategory'):
                validation_issues.append("⚠️ Subcategory missing (DevOps/Cloud_Computing/Cybersecurity/AI_and_ML)")
            
            if not metadata.get('url'):
                validation_issues.append("❌ URL missing")
                validation_passed = False
            
            if validation_issues:
                print(f"\n   Validation Issues:")
                for issue in validation_issues:
                    print(f"   {issue}")
            else:
                print(f"   ✅ All metadata validation passed")
        
        # Check for today's blog
        print(f"\n{'=' * 70}")
        print(f"TODAY'S BLOG CHECK ({today})")
        print("=" * 70)
        
        today_blogs = [b for b in blog_items if datetime.fromtimestamp(int(b['metadata'].get('timestamp', 0)), IST).date() == today]
        
        if today_blogs:
            print(f"✅ Found {len(today_blogs)} blog(s) published today")
            for blog in today_blogs:
                print(f"   - {blog['metadata'].get('title', 'N/A')}")
        else:
            print(f"⚠️ No blogs published today yet")
            print(f"   Expected time: 7:00 AM IST daily")
            print(f"   Current time: {datetime.now(IST).strftime('%H:%M:%S IST')}")
            
            # Check if it's before 7 AM
            current_hour = datetime.now(IST).hour
            if current_hour < 7:
                print(f"   ℹ️ Too early - blog generation runs at 7:00 AM")
            elif current_hour < 8:
                print(f"   ⚠️ Blog generation may be in progress or failed")
            else:
                print(f"   ❌ Blog generation may have failed - check logs")
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking latest blog: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_s3_sync():
    """Verify S3 and ChromaDB are in sync"""
    print(f"\n{'=' * 70}")
    print("S3 ↔ ChromaDB SYNC CHECK")
    print("=" * 70)
    
    try:
        import boto3
        import json
        
        s3 = boto3.client('s3')
        bucket = os.getenv('S3_BLOG_BUCKET', 'althaf-blogs-storage')
        
        # Get index.json from S3
        try:
            response = s3.get_object(Bucket=bucket, Key='blogs/index.json')
            s3_index = json.loads(response['Body'].read().decode('utf-8'))
            s3_blog_ids = {blog['id'] for blog in s3_index}
            
            print(f"✅ S3 blogs: {len(s3_blog_ids)}")
            
        except Exception as e:
            print(f"⚠️ Could not fetch S3 index: {e}")
            return False
        
        # Get blogs from ChromaDB
        chroma_api_key = os.getenv("CHROMA_API_KEY")
        chroma_tenant = os.getenv("CHROMA_TENANT_ID")
        chroma_db = os.getenv("CHROMA_DATABASE", "Development")
        
        client = chromadb.HttpClient(
            host="api.trychroma.com",
            ssl=True,
            headers={
                "x-chroma-token": chroma_api_key,
                "x-tenant": chroma_tenant,
                "x-database": chroma_db
            }
        )
        
        collection = client.get_collection("portfolio_master")
        all_items = collection.get(include=['metadatas'])
        
        chromadb_blog_ids = {
            all_items['ids'][idx] 
            for idx, metadata in enumerate(all_items['metadatas']) 
            if metadata.get('category') == 'blog'
        }
        
        print(f"✅ ChromaDB blogs: {len(chromadb_blog_ids)}")
        
        # Compare
        missing_in_chromadb = s3_blog_ids - chromadb_blog_ids
        missing_in_s3 = chromadb_blog_ids - s3_blog_ids
        
        if not missing_in_chromadb and not missing_in_s3:
            print(f"✅ S3 and ChromaDB are perfectly in sync!")
        else:
            if missing_in_chromadb:
                print(f"\n⚠️ {len(missing_in_chromadb)} blogs in S3 but not in ChromaDB:")
                for blog_id in list(missing_in_chromadb)[:5]:
                    print(f"   - {blog_id}")
                if len(missing_in_chromadb) > 5:
                    print(f"   ... and {len(missing_in_chromadb) - 5} more")
            
            if missing_in_s3:
                print(f"\n⚠️ {len(missing_in_s3)} blogs in ChromaDB but not in S3:")
                for blog_id in list(missing_in_s3)[:5]:
                    print(f"   - {blog_id}")
                if len(missing_in_s3) > 5:
                    print(f"   ... and {len(missing_in_s3) - 5} more")
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking S3 sync: {e}")
        return False

def main():
    print("\n")
    check_latest_blog()
    check_s3_sync()
    
    print(f"\n{'=' * 70}")
    print("MONITORING COMPLETE")
    print("=" * 70)
    print(f"\n📋 Task 20 Checklist:")
    print(f"   □ Blog generated today with category='blog'")
    print(f"   □ Subcategory matches expected rotation (DevOps/Cloud/Cyber/AI)")
    print(f"   □ S3 and ChromaDB are in sync")
    print(f"   □ Email notification received (check inbox)")
    print(f"   □ Blog accessible via frontend URL")
    print(f"\n💡 Run this script daily during Task 20 validation (48 hours)")

if __name__ == "__main__":
    main()
