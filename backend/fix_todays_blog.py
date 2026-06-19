"""
Quick Fix Script: Patch Today's Blog (Jan 1, 2026)
Removes leaked SEO instructions from published blog
"""
import boto3
import json
import re
import sys

def strip_seo_leakage(content: str) -> str:
    """Remove leaked SEO instructions from content"""
    # Remove SEO Implementation sections
    content = re.sub(
        r'####?\s*SEO Implementation.*?(?=\n##|\Z)',
        '',
        content,
        flags=re.DOTALL | re.IGNORECASE
    )
    
    # Remove meta description instructions
    content = re.sub(
        r'(?:1\.|•)\s*Meta Descriptions:.*?(?=\n(?:2\.|##)|\Z)',
        '',
        content,
        flags=re.DOTALL | re.IGNORECASE
    )
    
    # Clean up extra whitespace
    content = re.sub(r'\n{3,}', '\n\n', content)
    
    return content.strip()

def main():
    s3 = boto3.client('s3')
    bucket = 'althaf-blogs-storage'
    blog_id = 'DevOps_1767241800'
    key = f'blogs/posts/{blog_id}.json'
    
    print(f"🔧 Fixing blog: {blog_id}")
    
    try:
        # Download
        response = s3.get_object(Bucket=bucket, Key=key)
        blog = json.loads(response['Body'].read())
        
        original_content = blog['content']
        
        # Strip SEO instructions
        blog['content'] = strip_seo_leakage(original_content)
        
        # Check if anything changed
        if blog['content'] == original_content:
            print("⚠️ No SEO leakage found")
            return
        
        chars_removed = len(original_content) - len(blog['content'])
        print(f"✅ Removed {chars_removed} characters of leaked instructions")
        
        # Upload fixed version
        s3.put_object(
            Bucket=bucket,
            Key=key,
            Body=json.dumps(blog, indent=2).encode('utf-8'),
            ContentType='application/json'
        )
        
        print(f"✅ Successfully patched {blog_id}")
        print(f"📍 Updated: s3://{bucket}/{key}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
