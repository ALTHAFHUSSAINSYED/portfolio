# Security Setup Guide

## Environment Variables Setup

1. Create a `.env` file in the `/backend` directory:
```bash
touch .env
```

2. Copy the template from `.env.example` and fill in your actual credentials:
```bash
# MongoDB Configuration
MONGO_URL="mongodb+srv://your-actual-mongodb-url"
DB_NAME="portfolioDB"

# Cloudinary Configuration
CLOUDINARY_CLOUD_NAME="your-actual-cloud-name"
CLOUDINARY_API_KEY="your-actual-api-key"
CLOUDINARY_API_SECRET="your-actual-secret"

# Email Configuration
SENDGRID_API_KEY="your-actual-sendgrid-key"
TO_EMAIL="your-actual-email@domain.com"

# AI Services Configuration
GEMINI_API_KEY="your-actual-gemini-key"
GOOGLE_API_KEY="your-actual-google-key"  # Can be same as GEMINI_API_KEY

# ChromaDB Configuration
CHROMA_API_KEY="your-actual-chroma-key"
CHROMA_TENANT_ID="your-actual-tenant-id"
CHROMA_DATABASE="your-actual-database"
CHROMA_URL="your-actual-chroma-url"

# Search Configuration
SERPER_API_KEY="your-actual-serper-key"
```

## Important Security Notes

1. **NEVER commit the `.env` file to git**
   - The `.env` file is listed in `.gitignore`
   - Always use `.env.example` for sharing the structure

2. **Local Development**
   - Keep your `.env` file local
   - Different environments (dev/staging/prod) should have different credentials

3. **Production Deployment**
   - Use environment variables in production
   - Never copy `.env` file directly to production
   - Use secure secrets management in your hosting platform

4. **Credential Rotation**
   - Regularly rotate API keys
   - Update `.env` file after rotation
   - Keep backup of old credentials during rotation

5. **Access Control**
   - Limit access to credentials to essential team members
   - Use different API keys for development and production
   - Monitor API usage for unusual patterns

## Getting Your Credentials

1. **MongoDB**
   - Get from MongoDB Atlas Dashboard
   - Create specific database user with limited permissions

2. **Cloudinary**
   - Available in your Cloudinary Dashboard
   - Create separate API keys for each environment

3. **SendGrid**
   - Generate from SendGrid Dashboard
   - Use restricted API keys with minimum required permissions

4. **Gemini/Google**
   - Get from Google AI Studio
   - Create separate projects for dev/prod

5. **ChromaDB**
   - Available in ChromaDB Cloud Dashboard
   - Create separate tenants for different environments

6. **Serper**
   - Generate from Serper.dev Dashboard
   - Monitor usage to stay within limits

## Security Best Practices

1. **Environment Separation**
   ```bash
   # Development
   .env.development

   # Production
   .env.production
   ```

2. **Regular Audits**
   - Review API key usage regularly
   - Check for unauthorized access
   - Monitor rate limits and quotas

3. **Backup Strategy**
   - Keep secure backup of credentials
   - Document credential recovery process
   - Store recovery codes safely

4. **Access Logging**
   - Log all API key usage
   - Set up alerts for unusual patterns
   - Regular security reviews