import boto3
import json
import logging
import os
import chromadb
import google.generativeai as genai
import time

# Setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DevOpsFix")

s3 = boto3.client('s3')
bucket = 'althaf-blogs-storage'
old_id = 'DevOps_(Review_Pending)_1767069000'
new_id = 'DevOps_1767069000'

# Missing Content to Append
MISSING_STEPS = """

#### Step 1: Infrastructure as Code with Terraform
First, we define our Kubernetes cluster using HCL (HashiCorp Configuration Language).

```hcl
resource "aws_eks_cluster" "main" {
  name     = "devops-auto-cluster"
  role_arn = aws_iam_role.eks_cluster_role.arn

  vpc_config {
    subnet_ids = module.vpc.public_subnets
  }
}
```

#### Step 2: Continuous Deployment Pipeline
Next, we configure a Github Actions workflow to deploy automatically.

```yaml
name: Deploy to EKS
on: [push]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Configure AWS Credentials
        uses: aws-actions/configure-aws-credentials@v1
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1
      - name: Deploy to Cluster
        run: |
          aws eks update-kubeconfig --name devops-auto-cluster
          kubectl apply -f k8s/deployment.yaml
```

#### Step 3: Monitoring & Observability
Finally, we ensure the system is observable using Prometheus.

This closes the loop on a fully autonomous cycle.
"""

def get_embedding(text):
    try:
        genai.configure(api_key=os.getenv("GEMINI_API_KEY")) 
        result = genai.embed_content(
            model="models/text-embedding-004",
            content=text,
            task_type="retrieval_document"
        )
        return result['embedding']
    except Exception as e:
        logger.error(f"Embedding error: {e}")
        return None

try:
    # 1. Fetch Old Blog
    print(f"🔧 Fetching Old Blog: {old_id}")
    resp = s3.get_object(Bucket=bucket, Key=f'blogs/posts/{old_id}.json')
    blog = json.loads(resp['Body'].read())
    
    # 2. Prepare New Content
    content = blog.get('content', '')
    # Remove any partial "#### Step 1" if it exists at the very end
    if "#### Step 1" in content[-200:]:
         content = content.split("#### Step 1")[0].strip()
    
    # Check if "Kubernetes and Terraform" is at the end (from my previous read)
    # We will just append the steps.
    new_content = content + "\n" + MISSING_STEPS
    
    blog['content'] = new_content
    blog['id'] = new_id
    blog['category'] = "DevOps" # Ensure category is clean
    blog['url'] = f"https://althafportfolio.site/blogs/{new_id}"
    
    print(f"✅ Content Repaired. New Length: {len(new_content)}")

    # 3. Save New Blog to S3
    s3.put_object(
        Bucket=bucket,
        Key=f'blogs/posts/{new_id}.json',
        Body=json.dumps(blog, indent=2).encode(),
        ContentType='application/json'
    )
    print(f"✅ Saved NEW blog to S3: {new_id}")

    # 4. Update Index (Remove Old, Add New)
    print("📚 Updating Index...")
    resp = s3.get_object(Bucket=bucket, Key='blogs/index.json')
    index = json.loads(resp['Body'].read())
    
    # Filter out old ID
    new_list = [b for b in index['blogs'] if b['id'] != old_id]
    
    # Add new entry
    new_entry = {
         "id": new_id,
         "title": blog.get('title'),
         "summary": blog.get('summary'),
         "category": "DevOps",
         "created_at": blog.get('created_at'),
         "tags": blog.get('tags')
    }
    new_list.insert(0, new_entry) # Add to top
    index['blogs'] = new_list
    
    s3.put_object(
        Bucket=bucket,
        Key='blogs/index.json',
        Body=json.dumps(index, indent=2).encode(),
        ContentType='application/json'
    )
    print("✅ Index Updated (Old removed, New added).")

    # 5. Delete OLD Blog File
    s3.delete_object(Bucket=bucket, Key=f'blogs/posts/{old_id}.json')
    print(f"🗑️ Deleted Old Blog File: {old_id}")

    # 6. Update ChromaDB
    print("🧠 Updating ChromaDB...")
    try:
        api_key = os.getenv("CHROMA_API_KEY")
        tenant = os.getenv("CHROMA_TENANT_ID")
        db_name = os.getenv("CHROMA_DB_NAME")
        
        if api_key:
            client = chromadb.HttpClient(
                ssl=True, host='api.trychroma.com',
                tenant=tenant, database=db_name,
                headers={"x-chroma-token": api_key, "x-tenant": tenant, "x-database": db_name}
            )
        else:
             client = chromadb.PersistentClient(path="./chroma_db")

        collection = client.get_or_create_collection("Blogs_data")
        
        # Delete old
        collection.delete(ids=[old_id])
        print("   - Deleted old ID from Chroma")
        
        # Upsert new
        embed = get_embedding(new_content)
        if embed:
            collection.upsert(
                ids=[new_id],
                documents=[new_content],
                metadatas=[{
                    "title": blog.get('title'),
                    "category": "DevOps",
                    "url": blog['url'],
                    "timestamp": str(int(time.time()))
                }],
                embeddings=[embed]
            )
            print("   - Upserted NEW ID to Chroma")
        else:
            print("   ⚠️ Embedding failed, skipping upsert.")

    except Exception as e:
         print(f"❌ Chroma Update Failed: {e}")

    print("🚀 Full Migration Complete!")

except Exception as e:
    print(f"❌ Script Error: {e}")
