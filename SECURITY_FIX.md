# Security Fix Instructions

## Critical Issue: Exposed API Keys and Credentials

The CodeQL scan failed because your repository contains exposed API keys, secrets, and credentials. This is a serious security vulnerability that must be addressed immediately.

## Immediate Actions Required:

### 1. Revoke and Regenerate All Exposed API Keys

- **Gemini API Key**: Go to [Google AI Studio](https://makersuite.google.com/app/apikey) and regenerate your API key
- **Cloudinary**: Log into your Cloudinary dashboard and revoke/regenerate your API key and secret
- **Serper API Key**: Go to [Serper.dev](https://serper.dev) and regenerate your API key

### 2. Remove Sensitive Data from Git History

Install the BFG Repo-Cleaner:
```powershell
# Download the BFG jar file
Invoke-WebRequest -Uri "https://repo1.maven.org/maven2/com/madgag/bfg/1.14.0/bfg-1.14.0.jar" -OutFile "bfg.jar"
```

Create a text file containing patterns to remove:
```powershell
# Create a file with patterns to remove
@"
GEMINI_API_KEY=".*"
CLOUDINARY_API_KEY=.*
CLOUDINARY_API_SECRET=.*
SERPER_API_KEY=".*"
"@ | Out-File -FilePath "patterns.txt" -Encoding utf8
```

Run BFG to clean the repository:
```powershell
# Make a backup first
Copy-Item -Path "C:\portfolio\portfolio" -Destination "C:\portfolio\portfolio_backup" -Recurse

# Clone a fresh copy of your repo
cd C:\portfolio
git clone --mirror https://github.com/ALTHAFHUSSAINSYED/portfolio portfolio-mirror

# Run BFG on the mirror
java -jar bfg.jar --replace-text patterns.txt portfolio-mirror

# Clean the repository
cd portfolio-mirror
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# Push the cleaned repo
git push
```

### 3. Update Your Local Repository

After cleaning the repository history, update your local copy:

```powershell
cd C:\portfolio
rm -r -force portfolio
git clone https://github.com/ALTHAFHUSSAINSYED/portfolio
cd portfolio

# Create a new .env file with placeholders (don't include actual values)
@"
# MongoDB
MONGO_URL=mongodb+srv://username:password@cluster.mongodb.net/database
DB_NAME=portfolio

# Cloudinary
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key_placeholder
CLOUDINARY_API_SECRET=your_api_secret_placeholder

# AI Services
GEMINI_API_KEY=your_gemini_api_key_placeholder
SERPER_API_KEY=your_serper_api_key_placeholder
"@ | Out-File -FilePath "backend\.env.example" -Encoding utf8

# Add the actual values to your local .env file (this file should remain in .gitignore)
@"
# MongoDB
MONGO_URL=mongodb+srv://username:password@cluster.mongodb.net/database
DB_NAME=portfolio

# Cloudinary
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_new_api_key
CLOUDINARY_API_SECRET=your_new_api_secret

# AI Services
GEMINI_API_KEY=your_new_gemini_api_key
SERPER_API_KEY=your_new_serper_api_key
"@ | Out-File -FilePath "backend\.env" -Encoding utf8
```

### 4. Update Environment Variables in Deployment Services

- Log into your Render dashboard
- Go to your service settings
- Update all environment variables with the new credentials
- Redeploy your application

### 5. Add Security Checks to Your Workflow

- Consider using git pre-commit hooks to prevent committing sensitive data
- Set up GitHub secret scanning alerts
- Keep `.env` and similar files in your `.gitignore`

## Verification Steps

After completing these steps:

1. Confirm no credentials appear in your GitHub repository
2. Verify the application works with the new credentials
3. Wait for the next CodeQL scan to pass

## Additional Security Best Practices

- Use environment variables for all sensitive data
- Implement proper secret management
- Never hardcode credentials in your code
- Review code before committing to avoid leaking secrets