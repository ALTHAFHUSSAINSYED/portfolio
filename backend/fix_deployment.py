#!/usr/bin/env python3
"""
Deployment Fix Script - Run this on EC2 to fix common issues
"""

import os
import sys
import json
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio

# Sample projects data to seed MongoDB
SAMPLE_PROJECTS = [
    {
        "id": "1",
        "name": "Multi-Cloud CI/CD Pipeline",
        "summary": "End-to-end CI/CD implementation across AWS, GCP, and Azure",
        "details": """
        <p>Designed and implemented a comprehensive multi-cloud CI/CD pipeline that orchestrates 
        deployments across AWS, GCP, and Azure environments. This solution reduced deployment 
        time by 60% and improved reliability through automated testing and rollback mechanisms.</p>
        
        <h3>Key Features:</h3>
        <ul>
            <li>Unified pipeline for multi-cloud deployments</li>
            <li>Automated testing with 95% code coverage</li>
            <li>Blue-green deployment strategy</li>
            <li>Integrated security scanning</li>
        </ul>
        """,
        "technologies": ["Jenkins", "AWS CodePipeline", "GCP Cloud Build", "Docker", "Kubernetes", "Terraform"],
        "key_outcomes": "60% reduction in deployment time, 40% decrease in production incidents",
        "image_url": "https://images.unsplash.com/photo-1551033406-611cf9a28f67?w=800"
    },
    {
        "id": "2",
        "name": "Kubernetes Auto-Scaling Solution",
        "summary": "Implemented intelligent auto-scaling for Kubernetes clusters",
        "details": """
        <p>Developed and deployed a custom auto-scaling solution for Kubernetes clusters that 
        intelligently scales based on application metrics, reducing infrastructure costs by 35% 
        while maintaining 99.9% uptime.</p>
        
        <h3>Technical Implementation:</h3>
        <ul>
            <li>Custom Kubernetes Operator in Go</li>
            <li>Prometheus-based metrics collection</li>
            <li>Predictive scaling using historical data</li>
            <li>Cost optimization algorithms</li>
        </ul>
        """,
        "technologies": ["Kubernetes", "Go", "Prometheus", "Grafana", "AWS EKS", "Helm"],
        "key_outcomes": "35% cost reduction, 99.9% uptime maintained",
        "image_url": "https://images.unsplash.com/photo-1667372393119-3d4c48d07fc9?w=800"
    },
    {
        "id": "3",
        "name": "Infrastructure as Code Framework",
        "summary": "Built comprehensive IaC framework for multi-cloud provisioning",
        "details": """
        <p>Created a reusable Infrastructure as Code framework that standardizes infrastructure 
        provisioning across multiple cloud providers. The framework includes pre-built modules 
        for common patterns and automated compliance checking.</p>
        
        <h3>Components:</h3>
        <ul>
            <li>Terraform modules library</li>
            <li>Automated compliance scanning</li>
            <li>Cost estimation integration</li>
            <li>GitOps workflow</li>
        </ul>
        """,
        "technologies": ["Terraform", "Ansible", "Python", "GitLab CI", "AWS", "Azure", "GCP"],
        "key_outcomes": "70% faster infrastructure deployment, 100% infrastructure tracked in code",
        "image_url": "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=800"
    },
    {
        "id": "4",
        "name": "Serverless Monitoring Platform",
        "summary": "Built a serverless observability platform for distributed systems",
        "details": """
        <p>Designed and implemented a fully serverless monitoring and observability platform 
        that provides real-time insights into distributed systems. The platform processes 
        millions of events per day with sub-second latency.</p>
        
        <h3>Architecture:</h3>
        <ul>
            <li>Event-driven architecture</li>
            <li>Real-time data processing with Lambda</li>
            <li>CloudWatch and DataDog integration</li>
            <li>Custom alerting engine</li>
        </ul>
        """,
        "technologies": ["AWS Lambda", "DynamoDB", "Kinesis", "CloudWatch", "Python", "React"],
        "key_outcomes": "99.99% availability, sub-second latency for event processing",
        "image_url": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=800"
    },
    {
        "id": "5",
        "name": "Zero-Trust Security Architecture",
        "summary": "Implemented zero-trust security model across cloud infrastructure",
        "details": """
        <p>Led the implementation of a zero-trust security architecture across multi-cloud 
        infrastructure, significantly improving security posture and reducing the attack surface. 
        The solution includes identity-based access control, network segmentation, and continuous 
        monitoring.</p>
        
        <h3>Security Layers:</h3>
        <ul>
            <li>Identity and Access Management (IAM)</li>
            <li>Network micro-segmentation</li>
            <li>Continuous authentication and authorization</li>
            <li>Automated threat detection and response</li>
        </ul>
        """,
        "technologies": ["AWS IAM", "HashiCorp Vault", "Istio", "Cilium", "Falco", "SIEM"],
        "key_outcomes": "50% reduction in security incidents, passed SOC 2 Type II audit",
        "image_url": "https://images.unsplash.com/photo-1563986768609-322da13575f3?w=800"
    }
]

async def check_mongodb_connection():
    """Check if MongoDB is accessible"""
    print("Checking MongoDB connection...")
    mongo_url = os.environ.get('MONGO_URL')
    
    if not mongo_url:
        print("❌ MONGO_URL environment variable is not set!")
        print("\nTo fix this, run:")
        print('export MONGO_URL="your_mongodb_connection_string"')
        return False
    
    try:
        client = AsyncIOMotorClient(mongo_url, serverSelectionTimeoutMS=5000)
        # Try to get server info to verify connection
        await client.server_info()
        print("✅ MongoDB connection successful!")
        return True
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        return False

async def seed_projects():
    """Seed MongoDB with sample projects"""
    print("\nSeeding MongoDB with sample projects...")
    mongo_url = os.environ.get('MONGO_URL')
    db_name = os.environ.get('DB_NAME', 'portfolioDB')
    
    if not mongo_url:
        print("❌ Cannot seed: MONGO_URL not set")
        return False
    
    try:
        client = AsyncIOMotorClient(mongo_url)
        db = client[db_name]
        
        # Clear existing projects
        await db.projects.delete_many({})
        print(f"Cleared existing projects from {db_name}.projects")
        
        # Insert sample projects
        result = await db.projects.insert_many(SAMPLE_PROJECTS)
        print(f"✅ Successfully inserted {len(result.inserted_ids)} projects!")
        
        # Verify insertion
        count = await db.projects.count_documents({})
        print(f"Total projects in database: {count}")
        
        return True
    except Exception as e:
        print(f"❌ Failed to seed projects: {e}")
        return False

def check_environment_variables():
    """Check if all required environment variables are set"""
    print("\nChecking environment variables...")
    
    required_vars = {
        'MONGO_URL': 'MongoDB connection string',
        'GEMINI_API_KEY': 'Google Gemini API key',
        'SERPER_API_KEY': 'Serper search API key',
        'CORS_ORIGINS': 'Allowed CORS origins',
    }
    
    optional_vars = {
        'CHROMA_API_KEY': 'ChromaDB API key',
        'CHROMA_TENANT_ID': 'ChromaDB tenant ID',
        'CHROMA_DATABASE': 'ChromaDB database name',
        'CLOUDINARY_CLOUD_NAME': 'Cloudinary cloud name',
        'CLOUDINARY_API_KEY': 'Cloudinary API key',
        'CLOUDINARY_API_SECRET': 'Cloudinary API secret',
    }
    
    print("\n📋 Required Variables:")
    missing_required = []
    for var, description in required_vars.items():
        value = os.environ.get(var)
        if value:
            # Mask sensitive values
            masked = value[:10] + "..." if len(value) > 10 else "***"
            print(f"  ✅ {var}: {masked} ({description})")
        else:
            print(f"  ❌ {var}: NOT SET ({description})")
            missing_required.append(var)
    
    print("\n📋 Optional Variables:")
    for var, description in optional_vars.items():
        value = os.environ.get(var)
        if value:
            masked = value[:10] + "..." if len(value) > 10 else "***"
            print(f"  ✅ {var}: {masked} ({description})")
        else:
            print(f"  ⚠️  {var}: NOT SET ({description})")
    
    if missing_required:
        print(f"\n❌ Missing {len(missing_required)} required environment variables!")
        print("\nTo fix, add these to your .env file or set them in your environment:")
        for var in missing_required:
            print(f'export {var}="your_value_here"')
        return False
    else:
        print("\n✅ All required environment variables are set!")
        return True

async def main():
    """Main function to run all checks and fixes"""
    print("=" * 60)
    print(" Portfolio Deployment Fix Script")
    print("=" * 60)
    
    # Check environment variables
    env_ok = check_environment_variables()
    
    if not env_ok:
        print("\n⚠️  Some environment variables are missing.")
        print("Please set them before continuing.")
        sys.exit(1)
    
    # Check MongoDB connection
    mongo_ok = await check_mongodb_connection()
    
    if not mongo_ok:
        print("\n⚠️  MongoDB connection failed. Please check your MONGO_URL.")
        sys.exit(1)
    
    # Ask user if they want to seed projects
    print("\n" + "=" * 60)
    response = input("Do you want to seed MongoDB with sample projects? (yes/no): ").strip().lower()
    
    if response in ['yes', 'y']:
        seed_ok = await seed_projects()
        if seed_ok:
            print("\n✅ All fixes applied successfully!")
        else:
            print("\n⚠️  Failed to seed projects. Check the error messages above.")
    else:
        print("\n Skipping project seeding.")
    
    print("\n" + "=" * 60)
    print("✅ Deployment check complete!")
    print("=" * 60)
    
    # Print next steps
    print("\n📝 Next Steps:")
    print("1. Restart your Docker container if you made environment changes:")
    print("   docker restart portfolio-backend")
    print("\n2. Test the API endpoints:")
    print("   curl https://api.althafportfolio.site/api/projects")
    print("\n3. Check Docker logs for any errors:")
    print("   docker logs portfolio-backend --tail 100")

if __name__ == "__main__":
    asyncio.run(main())
