# EC2 Deployment & Testing Guide

## Step 1: Connect to EC2
```bash
ssh -i "PORTFOLIO.pem" ec2-user@13.233.54.210
```

## Step 2: Navigate to Project Directory
```bash
cd /path/to/portfolio/backend
# (Replace with actual path on EC2)
```

## Step 3: Pull Latest Changes
```bash
git pull origin main
```

## Step 4: Restart Backend Service
```bash
# If using systemd
sudo systemctl restart portfolio-backend

# OR if using PM2
pm2 restart portfolio-backend

# OR if running manually
# Kill existing process and restart
pkill -f "python.*server.py"
python server.py &
```

## Step 5: Run Test Script
```bash
python test_chatbot_fixes.py
```

## Expected Output

You should see:
- ✅ Test 1: LOW Profanity (Frustrated) - PASSED
- ✅ Test 2: Frustration Signal - PASSED
- ✅ Test 3: HIGH Profanity (Hostile) - PASSED
- ✅ Test 4: Filler/Acknowledgement - PASSED
- ✅ Test 5: Specific Question (No Biography) - PASSED
- ✅ Test 6a-6f: Multi-State Conversation Flow - PASSED
- ✅ Test 7: Normal Query (No False Positives) - PASSED

**Pass Rate: 100%**

## If Tests Fail

1. **Check server logs**:
   ```bash
   tail -f logs/chatbot.log
   ```

2. **Verify server is running**:
   ```bash
   curl http://localhost:8000/
   ```

3. **Share test output** with me for debugging

## After All Tests Pass

Proceed to Phase 8 (System Prompt Optimization) - final polish!
