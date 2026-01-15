# Day 3: Backend Deployment & Self-Hosted CI/CD 🚀

## 🎯 Overview
Deployed a production-ready FastAPI backend on AWS EC2 t3.small instance with fully automated CI/CD pipeline using self-hosted GitHub Actions runners. This post details the complete DevOps journey from Dockerization to deployment automation, including AI-powered chatbot RAG and auto-blogger systems.

---

## 🐳 Docker Containerization

### Complete Backend Stack
- **FastAPI** v0.110.1 - High-performance Python web framework
- **Uvicorn** v0.25.0 - Lightning-fast ASGI server  
- **Python** 3.11-slim - Optimized runtime environment
- **MongoDB** (Motor 3.3.1) - NoSQL database for portfolio data
- **ChromaDB** >=0.5.5 - Vector database for AI-powered chatbot RAG
- **Cloudinary** - Media asset management
- **Google GenAI** - AI model integration
- **OpenAI** >=1.0.0 - GPT model access
- **APScheduler** >=3.10.4 - Auto-blogger scheduling
- **Resend** - Email notifications
- **BeautifulSoup4** 4.12.3 - Web scraping for blog research
- **Pandas** >=2.2.0 & **NumPy** 1.26.4 - Data processing

### Dockerfile Configuration
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install build dependencies
RUN apt-get update \
    && apt-get install -y build-essential curl \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Multi-stage build for optimized image size
# Production-ready with health checks
```

**Container Details:**
- **Name:** `portfolio-backend`
- **Port Mapping:** Internal 8000 → External 80  
- **Restart Policy:** `always` (auto-recovery on failures)
- **Created:** January 7, 2026, 08:07 UTC
- **Status:** Running continuously (12+ days uptime)

---

## ☁️ AWS EC2 Infrastructure

### Instance Specifications
- **Instance Type:** **t3.small** (2 vCPUs, 2GB RAM)
- **Processor:** Intel(R) Xeon(R) CPU @ 2.50GHz
- **Region:** ap-south-1 (Mumbai)
- **Availability Zone:** ap-south-1a
- **Public IP:** 13.233.54.210
- **OS:** Amazon Linux 2023
- **Uptime:** 12+ days continuous operation

### Resource Utilization
- **Storage:** 35GB EBS volume (gp3)
  - Used: 11GB (31%)
  - Available: 24GB
  - Efficient utilization with room for growth
- **Memory:** 1.9GB RAM
  - Used: 1.1GB (58%)
  - Available: 800MB
  - Swap: 2GB (106MB used)
  - Optimized for production workload

### Security Configuration
- **Security Groups:** Configured for HTTP/HTTPS traffic
- **Firewall Rules (iptables):** 
  - Port 80 (HTTP) - Public access for API
  - Port 8000 - Backend service (Docker mapped)
  - Port 22 (SSH) - Restricted access via PEM key
  - Established connections tracked and allowed
- **Authentication:** SSH key-based only (PORTFOLIO.pem)
- **No password authentication** - Enhanced security posture

---

## 🤖 AI-Powered Backend Features

### 1. Intelligent Chatbot with RAG
**Endpoint:** `/api/ask-all-u-bot`

**Architecture:**
- **Vector Database:** ChromaDB with dual-mode support
  - Legacy mode: 3 separate collections
  - Unified mode: Single `portfolio_master` collection
- **Data Sources:** Portfolio sections (education, experience, projects, skills, achievements, languages, professional interests)
- **Embedding Model:** Google GenAI embeddings
- **Retrieval:** Semantic search with context-aware responses
- **Population Script:** `populate_vector_db.py` (32KB, 22KB chatbot provider)

**Workflow:**
- Manual repopulation via GitHub Actions workflow
- Automated ChromaDB sync from MongoDB
- Intent detection and context extraction
- RAG-based response generation

### 2. Auto-Blogger System
**Endpoint:** `/api/generate-blog`

**6-Component Architecture:**
1. **Researcher** - Topic research and trend analysis
2. **Writer** - Content generation with AI models
3. **Critic** - Quality assurance and feedback
4. **Publisher** - MongoDB and Cloudinary publishing
5. **Cleanup** - Resource management
6. **Notifier** - Email notifications via Resend

**Technology Categories:**
- AI and ML
- Cloud Computing
- Cybersecurity
- DevOps
- Low-Code/No-Code
- Software Development

**Scheduler:** APScheduler with AsyncIO for daily blog generation  
**State Management:** Persistent state file at `/app/backend/logs/auto_blogger/scheduler_state.json`

---

## 🔄 Self-Hosted CI/CD Pipeline

### GitHub Actions Workflows

#### 1. Backend Deployment Workflow
**Trigger:** Push to main branch  
**Runner:** Self-hosted on EC2 instance

**Deployment Process:**
1. **Code Push Detection** - Automatic trigger
2. **Container Cleanup** - Removes old containers and images
3. **Fresh Build** - Builds new Docker image from latest code
4. **Port Management** - Kills processes blocking port 8000
5. **Container Launch** - Starts container with restart policy
6. **Health Checks** - Multi-attempt validation (5 retries, 5s interval)
7. **Logging** - Captures deployment logs for debugging

**Health Check System:**
```bash
# Multi-attempt health verification
- Maximum attempts: 5
- Retry interval: 5 seconds
- Validates backend responsiveness
- Logs container status on failure
- Automatic rollback on health check failure
```

#### 2. ChromaDB Repopulation Workflow
**Trigger:** Manual (workflow_dispatch)  
**Purpose:** Sync vector database with latest portfolio data

**Process:**
1. Navigate to backend folder
2. Execute `populate_vector_db.py`
3. Clean up temporary files
4. Validate successful repopulation

### Workflow Features
- ✅ Automated deployment on code push
- ✅ Zero-downtime deployment strategy
- ✅ Comprehensive health checks with retry logic
- ✅ Automatic rollback on failure
- ✅ Detailed logging for debugging
- ✅ Environment variable management
- ✅ Self-hosted runner (no GitHub Actions compute costs)

---

## 🛠️ API Endpoints

### Core Endpoints
- **`GET /`** - Root endpoint
- **`GET /sitemap.xml`** - SEO sitemap
- **`GET /version`** - API version info
- **`GET /api/projects/{project_id}`** - Project details
- **`POST /api/contact`** - Contact form submission
- **`POST /api/generate-blog`** - Trigger auto-blogger
- **`POST /api/ask-all-u-bot`** - Chatbot RAG queries

**API Prefix:** `/api` for all application routes  
**Purpose:** Bypass Amplify SPA routing for backend calls

---

## 📊 Logging & Monitoring

### Current Setup
- **Docker Logs:** `docker logs portfolio-backend` (persistent across restarts)
- **Application Logs:** FastAPI logging within container
- **Deployment Logs:** GitHub Actions workflow runs
- **Health Check Logs:** Automated validation on each deployment
- **Auto-Blogger Logs:** Persistent state tracking in `/app/backend/logs/`

### Log Retention
- Container logs persist across restarts
- GitHub Actions logs retained per workflow run
- Application-level logging via FastAPI
- Auto-blogger state file prevents duplicate blog generation

---

## 💰 Cost Optimization

### Current Configuration
- **EC2 Instance:** t3.small (~$15/month)
  - 2 vCPUs, 2GB RAM
  - Sufficient for AI workloads (chatbot + auto-blogger)
- **EBS Storage:** 35GB gp3 (~$2.80/month)
- **Data Transfer:** Minimal costs for API traffic
- **Estimated Monthly Cost:** ~$18-20

### Optimization Strategies
- Efficient Docker multi-stage builds
- Minimal storage footprint (31% utilization)
- Optimized memory usage (58% utilization)
- Self-hosted runner eliminates GitHub Actions compute costs
- Single instance handles multiple AI workloads
- APScheduler for efficient task scheduling
- Persistent state prevents redundant processing

### Why t3.small?
- **AI Model Requirements:** ChromaDB embeddings + OpenAI/Google GenAI
- **Concurrent Workloads:** Chatbot RAG + Auto-blogger + API serving
- **Memory Headroom:** 2GB RAM handles vector operations efficiently
- **Cost-Performance Balance:** Optimal for production AI workloads

---

## 🔐 Security Best Practices

### Implemented Measures
- ✅ SSH key-based authentication (no password access)
- ✅ Security groups restrict inbound traffic
- ✅ Firewall rules (iptables) for specific ports only
- ✅ Environment variables for sensitive data (API keys, DB credentials)
- ✅ Docker container isolation
- ✅ Regular security updates via automated deployments
- ✅ MongoDB connection with authentication
- ✅ Cloudinary secure media storage
- ✅ No exposed secrets in codebase

---

## 🚀 Deployment Workflow

### Manual Deployment (Initial Setup)
```bash
# SSH into EC2
ssh -i "PORTFOLIO.pem" ec2-user@13.233.54.210

# Navigate to project
cd ~/portfolio

# Pull latest code
git pull origin main

# Build Docker image
docker build -t portfolio-backend -f backend/Dockerfile .

# Run container
docker run -d -p 80:8000 \
  --name portfolio-backend \
  --restart always \
  portfolio-backend
```

### Automated Deployment (Current)
```bash
# Developer workflow
git add .
git commit -m "Update backend features"
git push origin main

# GitHub Actions automatically:
# 1. Detects push to main
# 2. Runs on self-hosted EC2 runner
# 3. Stops and removes old container
# 4. Builds new Docker image
# 5. Starts new container with health checks
# 6. Validates deployment success
# 7. Logs results
```

---

## 📈 Key Achievements

✅ **Dockerized Backend** - Containerized FastAPI with 40+ dependencies  
✅ **AWS EC2 Deployment** - Production t3.small instance with 12+ days uptime  
✅ **Self-Hosted CI/CD** - Automated deployment pipeline on EC2  
✅ **AI Chatbot RAG** - ChromaDB vector database with semantic search  
✅ **Auto-Blogger System** - 6-component architecture with daily scheduling  
✅ **Health Monitoring** - Multi-retry health checks with automatic rollback  
✅ **Security Hardening** - SSH keys, security groups, firewall rules, env vars  
✅ **Cost Optimization** - Single instance for multiple AI workloads (~$18/month)  
✅ **Zero-Downtime Deployments** - Automated container replacement strategy  
✅ **Comprehensive Logging** - Multi-level logging for debugging and monitoring  
✅ **Database Integration** - MongoDB (portfolio data) + ChromaDB (vector embeddings)  
✅ **API Architecture** - RESTful endpoints with `/api` prefix for SPA routing  

---

## 🔮 Next Steps (Day 4)

- Deep dive into AI Chatbot RAG architecture
- Explain ChromaDB embedding and retrieval process
- Detail auto-blogger's 6-component pipeline
- Showcase model selection and fallback strategies
- Discuss prompt engineering for quality content
- Share performance metrics and optimization techniques

---

## 🛠️ Complete Tech Stack

**Backend Framework:** FastAPI 0.110.1  
**ASGI Server:** Uvicorn 0.25.0  
**Runtime:** Python 3.11-slim  
**Database:** MongoDB (Motor 3.3.1)  
**Vector Database:** ChromaDB >=0.5.5  
**AI Models:** Google GenAI, OpenAI >=1.0.0  
**Media Storage:** Cloudinary  
**Email:** Resend  
**Scheduling:** APScheduler >=3.10.4  
**Data Processing:** Pandas >=2.2.0, NumPy 1.26.4  
**Web Scraping:** BeautifulSoup4 4.12.3  
**Containerization:** Docker (Python 3.11-slim base)  
**Cloud Provider:** AWS EC2 t3.small (2 vCPUs, 2GB RAM)  
**CI/CD:** GitHub Actions (Self-hosted runner)  
**Operating System:** Amazon Linux 2023  
**Security:** SSH keys, Security Groups, Firewall rules, Environment variables  

---

## 💡 Lessons Learned

1. **Self-hosted runners** eliminate GitHub Actions compute costs while providing direct EC2 resource access
2. **Health checks with retry logic** are critical for validating deployments and catching issues early
3. **Docker restart policies** ensure automatic recovery from failures without manual intervention
4. **Resource monitoring** helps optimize costs and prevent over-provisioning
5. **Automated deployments** reduce human error and speed up iteration cycles
6. **t3.small is optimal** for AI workloads requiring vector operations and concurrent processing
7. **Persistent state management** prevents duplicate work in scheduled tasks
8. **Multi-component architecture** (auto-blogger) enables modular, maintainable AI systems
9. **Environment variable management** is crucial for secure API key handling
10. **Dual-mode ChromaDB** provides flexibility for legacy and unified collection strategies

---

**#DevOps #AWS #Docker #FastAPI #CICD #GitHubActions #CloudComputing #BackendDevelopment #Automation #EC2 #AI #MachineLearning #RAG #ChromaDB #MongoDB**

---

*This is Day 3 of my portfolio deployment series. Follow along as I document the complete DevOps journey from development to production!*

**Previous Posts:**
- Day 1: Frontend Architecture & AWS Amplify Deployment
- Day 2: Frontend CI/CD Pipeline & DNS Configuration

**Coming Next:**
- Day 4: AI Chatbot Architecture & RAG Implementation with ChromaDB
