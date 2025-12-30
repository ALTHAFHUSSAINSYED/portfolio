import boto3
import json
import logging

logging.basicConfig(level=logging.INFO)
s3 = boto3.client('s3')
bucket = 'althaf-blogs-storage'
blog_id = 'DevOps_(Review_Pending)_1767069000'

def clean_content(text):
    if not text: return ""
    
    # 1. Structure check
    stripped = text.rstrip()
    if stripped.endswith("```"): return text
    last_line = stripped.split('\n')[-1].strip()
    if last_line.startswith("#") or last_line.startswith("- ") or last_line.startswith("* "):
        return text

    # 2. Find terminator
    terminators = ['.', '!', '?', '"', ')', ']', '}']
    last_idx = -1
    for char in terminators:
        idx = text.rfind(char)
        if idx > last_idx:
            last_idx = idx
            
    if last_idx != -1:
        # Check if we are deleting structure
        text_to_delete = text[last_idx+1:]
        if "\n#" in text_to_delete or "```" in text_to_delete:
            return text
            
        return text[:last_idx+1]
    
    return text

try:
    print(f"🔧 Fetching Blog: {blog_id}")
    resp = s3.get_object(Bucket=bucket, Key=f'blogs/posts/{blog_id}.json')
    blog = json.loads(resp['Body'].read())
    
    content = blog.get('content', '')
    print(f"🧐 CURRENT ENDING (Last 50 chars): '{content[-50:]}'")
    
    # 1. Force Trim
    fixed_content = clean_content(content)
    print(f"✂️  Trimming: {len(content)} -> {len(fixed_content)}")
    print(f"    New Ending: '{fixed_content[-50:]}'")
    
    if len(content) == len(fixed_content):
         print("⚠️ WARNING: No trimming happened. Does it already end with punctuation?")
    
    blog['content'] = fixed_content
    
    # 2. FORCE Summary Generation
    print("📝 Forcing Summary Regeneration...")
    intro = fixed_content.replace("#", "").replace("*", "").strip()
    summary = intro[:250]
    last_space = summary.rfind(" ")
    if last_space != -1:
        summary = summary[:last_space] + "..."
    blog['summary'] = summary
    print(f"   New Summary: {summary}")
    
    # 3. Save
    s3.put_object(
        Bucket=bucket,
        Key=f'blogs/posts/{blog_id}.json',
        Body=json.dumps(blog, indent=2).encode(),
        ContentType='application/json'
    )
    
    # 4. Update Index
    print("📚 Updating Index...")
    resp = s3.get_object(Bucket=bucket, Key='blogs/index.json')
    index = json.loads(resp['Body'].read())
    
    found = False
    for b in index['blogs']:
        if b['id'] == blog_id:
            b['summary'] = summary
            print("✅ Index entry updated.")
            found = True
            break
            
    if found:
        s3.put_object(
            Bucket=bucket,
            Key='blogs/index.json',
            Body=json.dumps(index, indent=2).encode(),
            ContentType='application/json'
        )
    print("🚀 Done.")

except Exception as e:
    print(f"❌ Error: {e}")
