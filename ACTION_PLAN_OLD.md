# 🎯 Action Plan - Fix All Issues

## What I've Done

I've analyzed all the issues you reported and created automated fixes. Here's what's ready:

### ✅ Issues Fixed in Code

1. **Blogs UI** - Already working! Shows 3 blogs with "See More" button ✓
2. **MongoDB Setup** - Created automated seed script with 5 sample projects ✓
3. **Environment Variables** - Updated GitHub Actions to auto-deploy with secrets ✓
4. **Deployment Scripts** - Created helper scripts for setup and diagnostics ✓

### 📦 Files Created

1. **`backend/fix_deployment.py`** - Python script to:
   - Check all environment variables
   - Test MongoDB connection
   - Seed 5 sample projects into MongoDB
   - Provide diagnostic information

2. **`backend/setup_env.sh`** - Bash script to:
   - Interactively set up .env file
   - Prompt for all required variables
   - Generate complete configuration

3. **`DEPLOYMENT_FIXES.md`** - Comprehensive troubleshooting guide

4. **`.github/workflows/backend-deploy.yml`** - Updated to:
   - Automatically create .env file from GitHub Secrets
   - Deploy with proper environment variables
   - Include health checks after deployment
   - Auto-restart container

---

## 🚀 How to Fix Everything (2 Options)

### Option A: Automated Fix (Recommended)

This uses GitHub Actions to automatically deploy with all environment variables.

**Step 1: Add Secrets to GitHub**

Go to your GitHub repository → Settings → Secrets and variables → Actions → New repository secret

Add these secrets:

| Secret Name | Description | Example |
|------------|-------------|---------|
| `MONGO_URL` | MongoDB connection string | `mongodb+srv://user:pass@cluster.mongodb.net/` |
| `GEMINI_API_KEY` | Google Gemini API key | `AIzaSy...` |
| `SERPER_API_KEY` | Serper.dev API key | `abc123...` |
| `CORS_ORIGINS` | Allowed domains | `https://www.althafportfolio.site,https://althafportfolio.site` |
| `CHROMA_API_KEY` | ChromaDB API key (optional) | Your key |
| `CHROMA_TENANT_ID` | ChromaDB tenant (optional) | Your tenant |
| `CHROMA_DATABASE` | ChromaDB database (optional) | Your database |
| `CLOUDINARY_CLOUD_NAME` | Cloudinary name (optional) | Your cloud name |
| `CLOUDINARY_API_KEY` | Cloudinary key (optional) | Your API key |
| `CLOUDINARY_API_SECRET` | Cloudinary secret (optional) | Your secret |

**Step 2: Push the Updated Workflow**

```bash
git add .github/workflows/backend-deploy.yml
git add backend/fix_deployment.py
git add backend/setup_env.sh
git commit -m "feat: Add automated environment setup and MongoDB seeding"
git push origin main
```

**Step 3: Monitor the Deployment**

- Go to your repository → Actions tab
- Watch the "Deploy Backend to EC2" workflow run
- It will automatically:
  - Create .env file from secrets
  - Rebuild and restart Docker container
  - Run health checks

**Step 4: Seed Projects Data**

After successful deployment, SSH to EC2 and run:

```bash
cd /home/ec2-user/portfolio/backend
python3 fix_deployment.py
# Follow prompts to seed MongoDB with projects
```

---

### Option B: Manual Fix

If you prefer manual control or want to troubleshoot:

**Step 1: SSH to EC2**

```bash
ssh -i your-key.pem ec2-user@54.160.165.127
```

If SSH times out, check EC2 security group allows port 22 from your IP.

**Step 2: Navigate to Backend Directory**

```bash
cd /home/ec2-user/portfolio/backend
```

**Step 3: Run Setup Script**

```bash
chmod +x setup_env.sh
./setup_env.sh
```

Follow the prompts to enter all environment variables.

**Step 4: Restart Docker Container**

```bash
cd /home/ec2-user/portfolio
sudo docker stop portfolio-backend
sudo docker rm portfolio-backend
sudo docker build -t portfolio-backend -f backend/Dockerfile .
sudo docker run -d \
  --name portfolio-backend \
  --restart unless-stopped \
  --env-file /home/ec2-user/portfolio/backend/.env \
  -p 8000:8000 \
  portfolio-backend:latest
```

**Step 5: Run Fix Script**

```bash
python3 /home/ec2-user/portfolio/backend/fix_deployment.py
```

This will check everything and seed the database.

**Step 6: Verify**

```bash
# Check container is running
docker ps

# Check logs
docker logs portfolio-backend --tail 50

# Test API
curl http://localhost:8000/api/projects
```

---

## 🎥 Videos Issue

The videos exist in `/public/videos/` but may not be loading. Here are your options:

### Quick Fix (Hide Videos)

Edit [frontend/src/components/HeroSection.js](frontend/src/components/HeroSection.js):

Comment out the video sections (lines ~166-177 and ~215-226):

```javascript
{/* Temporarily hidden - videos not loading
<div className="z-20 order-2 lg:order-1 lg:col-span-1 flex justify-center lg:justify-start pt-4">
  <div className="relative group">
    <video 
      ref={leftVideoRef} 
      src="/videos/intro_left.mp4" 
      // ... rest of the code
    </video>
  </div>
</div>
*/}
```

### Proper Fix (Host Videos Externally)

1. Check video file sizes:
   ```bash
   ls -lh frontend/public/videos/
   ```

2. If large (>10MB each), upload to:
   - Cloudinary (free tier: 25GB storage)
   - AWS S3 (pay as you go)
   - YouTube (embed as video)

3. Update video `src` URLs in HeroSection.js

### Alternative (Compress Videos)

```bash
# Install ffmpeg
sudo apt install ffmpeg  # Ubuntu/Debian
brew install ffmpeg      # macOS

# Compress videos
ffmpeg -i frontend/public/videos/intro_left.mp4 \
  -vcodec h264 -acodec aac -b:v 2M \
  frontend/public/videos/intro_left_compressed.mp4
```

---

## ✅ Verification Checklist

After running the fixes, verify everything works:

### Backend API
```bash
# Test root endpoint
curl https://api.althafportfolio.site/

# Test projects endpoint (should return 5 projects)
curl https://api.althafportfolio.site/api/projects | grep -o "title" | wc -l

# Test blogs endpoint
curl https://api.althafportfolio.site/api/blogs

# Test chatbot endpoint
curl -X POST https://api.althafportfolio.site/api/ask-all-u-bot \
  -H "Content-Type: application/json" \
  -d '{"message":"Who is Althaf?"}'
```

### Frontend
1. Open https://www.althafportfolio.site
2. Check Projects section - should show 5 projects
3. Check Blogs section - should show 3 blogs with "See More" button
4. Test Chatbot - should respond with full information
5. Check Videos - should display or be gracefully hidden

---

## 🆘 Troubleshooting

### Issue: GitHub Secrets Not Working

**Symptom:** Workflow runs but container doesn't have env vars

**Fix:**
1. Verify secrets are added in GitHub repo settings
2. Check workflow logs for "Create environment file" step
3. SSH to EC2 and verify .env file exists:
   ```bash
   cat /home/ec2-user/portfolio/backend/.env
   ```

### Issue: MongoDB Connection Failed

**Symptom:** API returns empty array, logs show connection error

**Fix:**
1. Verify MONGO_URL is correct (should start with `mongodb+srv://`)
2. Check MongoDB Atlas network access allows EC2 IP (or allow 0.0.0.0/0 for testing)
3. Test connection manually:
   ```bash
   docker exec -it portfolio-backend python3 -c "from motor.motor_asyncio import AsyncIOMotorClient; import asyncio; client = AsyncIOMotorClient('$MONGO_URL'); asyncio.run(client.server_info()); print('Connected!')"
   ```

### Issue: Docker Container Keeps Restarting

**Symptom:** `docker ps` shows container restarting

**Fix:**
1. Check logs: `docker logs portfolio-backend --tail 100`
2. Look for errors (missing modules, invalid env vars, etc.)
3. Try running container interactively to see errors:
   ```bash
   docker run -it --env-file backend/.env portfolio-backend:latest /bin/bash
   ```

### Issue: Self-Hosted Runner Not Working

**Symptom:** GitHub Actions shows "waiting for runner"

**Fix:**
1. Check runner status on EC2:
   ```bash
   cd /home/ec2-user/actions-runner
   ./run.sh status
   ```
2. Restart runner if needed:
   ```bash
   sudo ./svc.sh stop
   sudo ./svc.sh start
   ```

---

## 📊 Expected Results

After all fixes are applied:

| Component | Status | Expected Behavior |
|-----------|--------|-------------------|
| Projects API | ✅ | Returns 5 projects with full details |
| Chatbot | ✅ | Responds with AI-powered answers using Gemini + RAG |
| Blogs | ✅ | Shows 3 blogs initially, expands with "See More" |
| Videos | ⚠️ | Either display or gracefully hidden (pending fix) |

---

## 🎯 Next Steps

1. Choose Option A (automated) or Option B (manual) above
2. Follow the steps for your chosen option
3. Run the verification checklist
4. If any issues, check troubleshooting section
5. For videos, choose one of the three options (hide/host/compress)

---

## 💬 Need Help?

If you encounter any issues:

1. **Check Docker logs:**
   ```bash
   docker logs portfolio-backend --tail 100 --follow
   ```

2. **Run diagnostic script:**
   ```bash
   python3 backend/fix_deployment.py
   ```

3. **Test endpoints manually:**
   ```bash
   # From EC2
   curl http://localhost:8000/api/projects
   ```

4. **Provide error details:**
   - Container logs
   - Output of fix_deployment.py
   - GitHub Actions workflow logs

---

Ready to proceed! Choose your option and let me know if you need any clarification on the steps.
