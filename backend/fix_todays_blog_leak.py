#!/usr/bin/env python3
"""
Fix SEO metadata leak in today's Low-Code/No-Code blog
"""
import os
import boto3
import json

def main():
    print("=" * 80)
    print("FIXING SEO METADATA LEAK IN LOW-CODE/NO-CODE BLOG")
    print("=" * 80)
    
    # Connect to S3
    s3 = boto3.client('s3')
    bucket = 'althaf-blogs-storage'
    blog_id = 'Low-Code-No-Code_1767673800'
    key = f'blogs/posts/{blog_id}.json'
    
    print(f"\n1. Downloading blog from S3: {key}")
    try:
        response = s3.get_object(Bucket=bucket, Key=key)
        blog_data = json.loads(response['Body'].read())
        print(f"   ✅ Downloaded: {blog_data['title'][:70]}...")
    except Exception as e:
        print(f"   ❌ Failed to download: {e}")
        return 1
    
    # Check if the leak exists
    content = blog_data.get('content', '')
    if 'SEO Improvements:' not in content:
        print("\n   ⚠️  SEO leak section not found in content. Might already be fixed.")
        return 0
    
    # Remove the SEO Improvements section
    print("\n2. Removing SEO metadata leak...")
    
    # Find and remove the entire SEO Improvements section
    leak_start = content.find('SEO Improvements:')
    if leak_start != -1:
        # Find the end of the section (look for next major heading or end of content)
        leak_section = content[leak_start:]
        
        # The leak section typically ends before the next major section or at the end
        # Let's find the next double newline after "External Links:" which marks the end
        external_links_pos = leak_section.find('External Links:')
        if external_links_pos != -1:
            # Find the end of the External Links bullet point
            remaining = leak_section[external_links_pos:]
            # Find the next paragraph (double newline)
            end_pos = remaining.find('\n\n')
            if end_pos != -1:
                leak_end = leak_start + external_links_pos + end_pos
            else:
                # If no double newline found, assume it's at the end
                leak_end = len(content)
        else:
            # Fallback: remove until end of content
            leak_end = len(content)
        
        # Remove the leak section
        cleaned_content = content[:leak_start].rstrip() + content[leak_end:].lstrip()
        blog_data['content'] = cleaned_content
        
        print(f"   ✅ Removed {leak_end - leak_start} characters of SEO metadata")
        print(f"   Original length: {len(content)} chars")
        print(f"   Cleaned length: {len(cleaned_content)} chars")
    else:
        print("   ⚠️  'SEO Improvements:' section not found")
        return 0
    
    # Upload cleaned blog back to S3
    print("\n3. Uploading cleaned blog to S3...")
    try:
        s3.put_object(
            Bucket=bucket,
            Key=key,
            Body=json.dumps(blog_data, indent=2),
            ContentType='application/json'
        )
        print(f"   ✅ Uploaded: {key}")
    except Exception as e:
        print(f"   ❌ Failed to upload: {e}")
        return 1
    
    print("\n" + "=" * 80)
    print("✅ SEO METADATA LEAK FIXED SUCCESSFULLY")
    print("=" * 80)
    print("\nNext steps:")
    print("1. Restart the backend container to clear caches")
    print("2. Verify the blog at: /blogs/Low-Code-No-Code_1767673800")
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main())
