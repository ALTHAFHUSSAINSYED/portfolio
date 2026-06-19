#!/usr/bin/env python3
"""
Backend script to generate dynamic sitemap from S3 blogs and MongoDB projects.
Can be run as a cron job or triggered after blog generation.
"""

import os
import json
import boto3
from datetime import datetime
from typing import List, Dict
import xml.etree.ElementTree as ET

# Configuration
S3_BUCKET = os.getenv('S3_BLOG_BUCKET', 'althaf-blogs-storage')
SITE_URL = 'https://althafportfolio.site'
OUTPUT_FILE = '/tmp/sitemap.xml'

def fetch_blogs_from_s3() -> List[Dict]:
    """Fetch all blog posts from S3 bucket"""
    try:
        s3 = boto3.client('s3')
        
        # First, try to get index.json
        try:
            index_obj = s3.get_object(Bucket=S3_BUCKET, Key='index.json')
            index_data = json.loads(index_obj['Body'].read().decode('utf-8'))
            print(f"✅ Found {len(index_data)} blogs from index.json")
            return index_data
        except:
            # Fallback: List all JSON files in bucket
            print("⚠️  index.json not found, listing bucket objects...")
            response = s3.list_objects_v2(Bucket=S3_BUCKET)
            blogs = []
            
            for obj in response.get('Contents', []):
                key = obj['Key']
                if key.endswith('.json') and key != 'index.json':
                    blog_obj = s3.get_object(Bucket=S3_BUCKET, Key=key)
                    blog_data = json.loads(blog_obj['Body'].read().decode('utf-8'))
                    blogs.append(blog_data)
            
            print(f"✅ Found {len(blogs)} blogs from bucket listing")
            return blogs
    except Exception as e:
        print(f"❌ Error fetching blogs from S3: {e}")
        return []

def fetch_projects_from_mongodb() -> List[Dict]:
    """Fetch all projects from MongoDB"""
    try:
        from motor.motor_asyncio import AsyncIOMotorClient
        import asyncio
        
        mongo_url = os.getenv('MONGO_URL')
        db_name = os.getenv('DB_NAME', 'portfolioDB')
        
        async def get_projects():
            client = AsyncIOMotorClient(mongo_url)
            db = client[db_name]
            projects = await db.projects.find({}).to_list(length=None)
            return projects
        
        projects = asyncio.run(get_projects())
        print(f"✅ Found {len(projects)} projects from MongoDB")
        return projects
    except Exception as e:
        print(f"⚠️  Could not fetch projects from MongoDB: {e}")
        return []

def generate_sitemap(blogs: List[Dict], projects: List[Dict]) -> str:
    """Generate XML sitemap"""
    
    # Create root element
    urlset = ET.Element('urlset')
    urlset.set('xmlns', 'http://www.sitemaps.org/schemas/sitemap/0.9')
    urlset.set('xmlns:news', 'http://www.google.com/schemas/sitemap-news/0.9')
    urlset.set('xmlns:xhtml', 'http://www.w3.org/1999/xhtml')
    urlset.set('xmlns:mobile', 'http://www.google.com/schemas/sitemap-mobile/1.0')
    urlset.set('xmlns:image', 'http://www.google.com/schemas/sitemap-image/1.1')
    urlset.set('xmlns:video', 'http://www.google.com/schemas/sitemap-video/1.1')
    
    # Static pages
    static_pages = [
        {'url': '/', 'priority': '1.0', 'changefreq': 'weekly'},
        {'url': '/#about', 'priority': '0.8', 'changefreq': 'monthly'},
        {'url': '/#projects', 'priority': '0.8', 'changefreq': 'weekly'},
        {'url': '/#blogs', 'priority': '0.9', 'changefreq': 'daily'},
        {'url': '/#contact', 'priority': '0.7', 'changefreq': 'monthly'},
    ]
    
    for page in static_pages:
        url_elem = ET.SubElement(urlset, 'url')
        ET.SubElement(url_elem, 'loc').text = f"{SITE_URL}{page['url']}"
        ET.SubElement(url_elem, 'changefreq').text = page['changefreq']
        ET.SubElement(url_elem, 'priority').text = page['priority']
    
    # Blog pages
    for blog in blogs:
        if blog.get('published', True) and blog.get('id'):
            url_elem = ET.SubElement(urlset, 'url')
            ET.SubElement(url_elem, 'loc').text = f"{SITE_URL}/blogs/{blog['id']}"
            
            # Add lastmod if created_at exists
            if 'created_at' in blog:
                try:
                    date_str = blog['created_at'].split('T')[0]
                    ET.SubElement(url_elem, 'lastmod').text = date_str
                except:
                    pass
            
            ET.SubElement(url_elem, 'changefreq').text = 'weekly'
            ET.SubElement(url_elem, 'priority').text = '0.9'
    
    # Project pages
    for project in projects:
        project_id = str(project.get('_id', project.get('id', '')))
        if project_id:
            url_elem = ET.SubElement(urlset, 'url')
            ET.SubElement(url_elem, 'loc').text = f"{SITE_URL}/projects/{project_id}"
            ET.SubElement(url_elem, 'changefreq').text = 'monthly'
            ET.SubElement(url_elem, 'priority').text = '0.8'
            ET.SubElement(url_elem, 'lastmod').text = datetime.now().strftime('%Y-%m-%d')
    
    # Generate XML string
    tree = ET.ElementTree(urlset)
    ET.indent(tree, space="  ")
    
    return ET.tostring(urlset, encoding='unicode', xml_declaration=True)

def upload_to_s3(xml_content: str):
    """Upload sitemap to S3 bucket"""
    try:
        s3 = boto3.client('s3')
        s3.put_object(
            Bucket=S3_BUCKET,
            Key='sitemap.xml',
            Body=xml_content.encode('utf-8'),
            ContentType='application/xml',
            CacheControl='max-age=3600'
        )
        print(f"✅ Sitemap uploaded to S3: s3://{S3_BUCKET}/sitemap.xml")
        return True
    except Exception as e:
        print(f"❌ Error uploading sitemap to S3: {e}")
        return False

def main():
    """Main execution"""
    print("🚀 Generating dynamic sitemap...")
    print(f"   📦 S3 Bucket: {S3_BUCKET}")
    print(f"   🌐 Site URL: {SITE_URL}")
    print()
    
    # Fetch data
    blogs = fetch_blogs_from_s3()
    projects = fetch_projects_from_mongodb()
    
    # Generate sitemap
    xml_content = generate_sitemap(blogs, projects)
    
    # Save locally
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(xml_content)
    
    print(f"\n✅ Dynamic sitemap generated successfully!")
    print(f"   📊 Total URLs: {5 + len(blogs) + len(projects)}")
    print(f"   - 5 static pages")
    print(f"   - {len(blogs)} blog posts")
    print(f"   - {len(projects)} projects")
    print(f"   📍 Local: {OUTPUT_FILE}")
    
    # Upload to S3 (optional - can be disabled if using frontend build)
    upload_to_s3(xml_content)
    
    print(f"\n🌐 Submit to Google Search Console:")
    print(f"   https://search.google.com/search-console")

if __name__ == '__main__':
    main()
