# 🚀 Deployment Issues - Fixes and Solutions

## Issues Identified

Based on your screenshot and testing, here are the issues found:

### ✅ 1. **Blogs UI** - ALREADY FIXED
The BlogsSection.js already has the functionality to show only 3 blogs initially with a "See More Blogs" button. This is working as expected.

### ⚠️ 2. **Videos Not Loading**
**Status:** Videos exist in `/public/videos/` folder but not displaying

**Possible Causes:**
- Video files might be too large for Amplify
- MIME type configuration issue
- Build output not including videos

**To Fix:**
1. Check video file sizes:
   ```bash
   ls -lh frontend/public/videos/
   ```

2. If videos are large (>10MB each), consider:
   - Compressing them with ffmpeg
   - Hosting them on Cloudinary or S3
   - Using video streaming service

3. Temporary fix - Replace videos with placeholder or remove them:
   - Option A: Comment out the video elements in [HeroSection.js](frontend/src/components/HeroSection.js#L166-L172)
   - Option B: Replace with static images

### ❌ 3. **Projects API Returns Empty Array**
**Status:** API responds but returns `[]`

**Root Cause:** MongoDB is either not connected or has no data

**To Fix on EC2:**

1. **SSH to EC2** (you may need to add your current IP to security group first):
   ```bash
   # Add your IP to security group
   # Then SSH:
   ssh -i <your-key.pem> ec2-user@<ec2-ip>
   ```

2. **Check Docker container environment variables:**
   ```bash
   docker exec portfolio-backend env | grep -E 'MONGO|CORS|GEMINI|SERPER|CHROMA'
   ```

3. **If MONGO_URL is missing, stop container and set environment variables:**
   ```bash
   # Create/update .env file on EC2
   sudo nano /home/ec2-user/portfolio-backend/.env
   ```

   Add these variables:
   ```bash
   MONGO_URL=your_mongodb_connection_string
   GEMINI_API_KEY=your_gemini_api_key
   SERPER_API_KEY=your_serper_api_key
   CORS_ORIGINS=https://www.althafportfolio.site,https://althafportfolio.site
   CHROMA_API_KEY=your_chroma_api_key
   CHROMA_TENANT_ID=your_chroma_tenant_id
   CHROMA_DATABASE=your_chroma_database
   CLOUDINARY_CLOUD_NAME=your_cloudinary_name
   CLOUDINARY_API_KEY=your_cloudinary_api_key
   CLOUDINARY_API_SECRET=your_cloudinary_api_secret
   ```

4. **Update docker-compose.yml or restart command to use .env file:**
   ```bash
   docker stop portfolio-backend
   docker rm portfolio-backend
   
   # Run with environment file
   docker run -d \
     --name portfolio-backend \
     --restart unless-stopped \
     --env-file /home/ec2-user/portfolio-backend/.env \
     -p 8000:8000 \
     portfolio-backend:latest
   ```

5. **Run the fix_deployment.py script:**
   ```bash
   # On EC2, in your backend directory
   python3 fix_deployment.py
   ```
   
   This script will:
   - ✅ Check all environment variables
   - ✅ Test MongoDB connection
   - ✅ Seed MongoDB with 5 sample projects
   - ✅ Provide diagnostic information

6. **Verify projects are loaded:**
   ```bash
   curl https://api.althafportfolio.site/api/projects
   ```

### ⚠️ 4. **Chatbot Limited Functionality**
**Status:** Works but returns "limited functionality" message

**Root Cause:** Missing API keys (GEMINI_API_KEY or SERPER_API_KEY) or ChromaDB credentials

**To Fix:**
- Follow the same steps as #3 above to set all environment variables
- The chatbot needs:
  - `GEMINI_API_KEY` - for AI responses
  - `SERPER_API_KEY` - for web search (optional but recommended)
  - `CHROMA_API_KEY`, `CHROMA_TENANT_ID`, `CHROMA_DATABASE` - for RAG (optional but recommended)

---

## 🔧 Quick Fix Script

I've created `backend/fix_deployment.py` which you can run on EC2 to:
1. Check all environment variables
2. Verify MongoDB connection
3. Seed sample projects data
4. Provide diagnostic information

**To use it:**
```bash
# On EC2
cd ~/portfolio-backend/backend
python3 fix_deployment.py
```

---

## 🎯 Priority Order

1. **CRITICAL** - Fix MongoDB connection (Projects not loading)
2. **HIGH** - Fix Chatbot API keys (Limited functionality)
3. **MEDIUM** - Fix Videos (Cosmetic issue)
4. **DONE** ✅ - Blogs UI (Already working correctly)

---

## 📋 Checklist

Use this checklist to track your progress:

- [ ] SSH to EC2 instance
- [ ] Check Docker container is running (`docker ps`)
- [ ] Check environment variables in container
- [ ] Create/update .env file on EC2
- [ ] Restart Docker container with .env file
- [ ] Run fix_deployment.py script
- [ ] Verify MongoDB connection
- [ ] Seed projects data
- [ ] Test `/api/projects` endpoint
- [ ] Test `/api/ask-all-u-bot` endpoint
- [ ] Check video file sizes
- [ ] Compress or host videos externally if needed
- [ ] Test full website functionality

---

## 🆘 If You Get Stuck

**SSH Connection Times Out:**
1. Check EC2 security group allows SSH (port 22) from your IP
2. Verify EC2 instance is running in AWS Console
3. Check if you have the correct .pem key file

**Docker Container Not Running:**
```bash
# Check container status
docker ps -a

# Check logs
docker logs portfolio-backend --tail 100

# Restart container
docker restart portfolio-backend
```

**MongoDB Connection Issues:**
1. Verify MONGO_URL is correct (should start with `mongodb+srv://` or `mongodb://`)
2. Check MongoDB Atlas allows connections from EC2 IP
3. Test connection with mongosh: `mongosh "your_mongo_url"`

**API Still Returns Empty:**
1. Check Docker logs: `docker logs portfolio-backend --tail 100`
2. Verify environment variables are loaded: `docker exec portfolio-backend env`
3. Test MongoDB from within container: `docker exec -it portfolio-backend python3 -c "import os; print(os.environ.get('MONGO_URL'))"`

---

## 📝 Alternative: GitHub Actions Deployment

If manual SSH is problematic, you can update your GitHub Actions workflow to automatically set environment variables and run the fix script:

Update `.github/workflows/backend-deploy.yml` to include:
```yaml
- name: Set environment variables
  run: |
    echo "MONGO_URL=${{ secrets.MONGO_URL }}" >> .env
    echo "GEMINI_API_KEY=${{ secrets.GEMINI_API_KEY }}" >> .env
    # ... add all other secrets
    docker cp .env portfolio-backend:/app/.env
    docker restart portfolio-backend
```

---

## 🎉 Expected Results

After following these fixes:

1. ✅ Projects section shows 5 sample projects
2. ✅ Chatbot responds with full functionality
3. ✅ Blogs show 3 initially with "See More" button (already working)
4. ✅ Videos either display or are gracefully hidden

---

Need help with any specific step? Let me know!
