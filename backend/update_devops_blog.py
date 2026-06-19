#!/usr/bin/env python3
"""
Manually update DevOps blog with proper title and summary
"""
import boto3
import json

# S3 Configuration
bucket = 'althaf-blogs-storage'
blog_id = 'DevOps_1767007641'

# Initialize S3 client
s3 = boto3.client('s3')

# Read current blog
print(f"📖 Reading blog {blog_id}...")
resp = s3.get_object(Bucket=bucket, Key=f'blogs/posts/{blog_id}.json')
blog = json.loads(resp['Body'].read())

# Manually create descriptive title and summary
NEW_TITLE = "DevOps Fundamentals: A Comprehensive Guide to Modern Software Delivery"
NEW_SUMMARY = "Explore the core principles of DevOps, from continuous integration and deployment to infrastructure automation. Learn how DevOps practices transform software delivery through collaboration, automation, and monitoring, with practical examples using Jenkins, Docker, and Kubernetes."

print(f"\n✏️ Updating blog metadata:")
print(f"  Old title: {blog.get('title')}")
print(f"  New title: {NEW_TITLE}")
print(f"\n  New summary: {NEW_SUMMARY}")

# Update blog
blog['title'] = NEW_TITLE
blog['summary'] = NEW_SUMMARY

# Save updated blog to S3
print(f"\n💾 Saving updated blog to S3...")
s3.put_object(
    Bucket=bucket,
    Key=f'blogs/posts/{blog_id}.json',
    Body=json.dumps(blog, indent=2).encode(),
    ContentType='application/json'
)

# Update index.json
print(f"\n📝 Updating index.json...")
resp = s3.get_object(Bucket=bucket, Key='blogs/index.json')
index = json.loads(resp['Body'].read())

# Find and update the blog in index
for i, b in enumerate(index.get('blogs', [])):
    if b.get('id') == blog_id:
        index['blogs'][i]['title'] = NEW_TITLE
        index['blogs'][i]['summary'] = NEW_SUMMARY
        print(f"  ✅ Updated blog at index position {i}")
        break

# Save updated index
s3.put_object(
    Bucket=bucket,
    Key='blogs/index.json',
    Body=json.dumps(index, indent=2).encode(),
    ContentType='application/json'
)

print(f"\n✅ Blog updated successfully!")
print(f"\nChanges:")
print(f"  • Title: {NEW_TITLE}")
print(f"  • Summary: {NEW_SUMMARY[:100]}...")
print(f"\n🔗 View at: https://althafportfolio.site/blogs/{blog_id}")
