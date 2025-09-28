# Environment Setup Guide

## Environment Variables

This project requires certain environment variables to be set for various functionalities to work properly. Environment files are not included in the repository for security reasons.

### Backend Environment Setup

1. Create the following files in the `backend` directory:
   - `.env` - Main environment configuration
   - `.env.gemini` - Gemini AI service configuration

2. Use the example files as templates:
   - Copy `.env.example` to `.env` and update with your values
   - Copy `.env.gemini.example` to `.env.gemini` and update with your API keys

### Required Environment Variables

#### Main Environment (.env)

```
# MongoDB Configuration
MONGO_URL="your_mongodb_connection_string"
DB_NAME="portfolio"

# Cloudinary Configuration (for image uploads)
CLOUDINARY_CLOUD_NAME="your_cloud_name"
CLOUDINARY_API_KEY="your_api_key"
CLOUDINARY_API_SECRET="your_api_secret"

# Email Configuration (SendGrid)
SENDGRID_API_KEY="your_sendgrid_api_key"
TO_EMAIL="your_email@example.com"

# CORS Configuration
CORS_ORIGINS="http://localhost:3000,https://your-frontend-domain.com"
```

#### Gemini Configuration (.env.gemini)

```
# Gemini API Key
# Get your free API key from: https://makersuite.google.com/app/apikey
GEMINI_API_KEY="YOUR_GEMINI_API_KEY"

# OpenAI API Key (as fallback)
OPENAI_API_KEY="YOUR_OPENAI_API_KEY"
```

## Security Note

Never commit environment files with actual API keys to the repository. The `.gitignore` file is configured to exclude all `.env*` files to help prevent accidental exposure of sensitive information.