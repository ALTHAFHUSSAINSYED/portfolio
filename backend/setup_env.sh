#!/bin/bash

# Backend Environment Setup Script
# Run this on EC2 to configure all required environment variables

echo "========================================="
echo " Portfolio Backend Environment Setup"
echo "========================================="
echo ""

# Create .env file
ENV_FILE=".env"

echo "This script will help you set up all required environment variables."
echo "Creating $ENV_FILE..."
echo ""

# Function to prompt for a variable
prompt_var() {
    local var_name=$1
    local var_description=$2
    local is_required=$3
    local current_value=$(printenv $var_name)
    
    if [ -n "$current_value" ]; then
        echo "✓ $var_name is already set (using existing value)"
        echo "$var_name=$current_value" >> $ENV_FILE
    else
        if [ "$is_required" = "true" ]; then
            echo "❗ REQUIRED: $var_description"
        else
            echo "⚬  OPTIONAL: $var_description"
        fi
        read -p "Enter $var_name (or press Enter to skip): " value
        if [ -n "$value" ]; then
            echo "$var_name=$value" >> $ENV_FILE
            echo "✓ Set $var_name"
        elif [ "$is_required" = "true" ]; then
            echo "⚠ Warning: $var_name is required but not set!"
        fi
        echo ""
    fi
}

# Remove old .env if exists
rm -f $ENV_FILE

# Required variables
echo "=== REQUIRED VARIABLES ==="
echo ""
prompt_var "MONGO_URL" "MongoDB connection string (mongodb+srv://...)" "true"
prompt_var "GEMINI_API_KEY" "Google Gemini API key" "true"
prompt_var "SERPER_API_KEY" "Serper.dev API key for web search" "true"
prompt_var "CORS_ORIGINS" "Allowed CORS origins (comma-separated)" "true"

echo ""
echo "=== OPTIONAL VARIABLES ==="
echo ""
prompt_var "CHROMA_API_KEY" "ChromaDB API key (for vector search)" "false"
prompt_var "CHROMA_TENANT_ID" "ChromaDB tenant ID" "false"
prompt_var "CHROMA_DATABASE" "ChromaDB database name" "false"
prompt_var "CLOUDINARY_CLOUD_NAME" "Cloudinary cloud name (for image hosting)" "false"
prompt_var "CLOUDINARY_API_KEY" "Cloudinary API key" "false"
prompt_var "CLOUDINARY_API_SECRET" "Cloudinary API secret" "false"
prompt_var "SENDGRID_API_KEY" "SendGrid API key (for email notifications)" "false"
prompt_var "DB_NAME" "MongoDB database name (default: portfolioDB)" "false"

# Add default values if not set
if ! grep -q "^CORS_ORIGINS=" $ENV_FILE; then
    echo "CORS_ORIGINS=https://www.althafportfolio.site,https://althafportfolio.site" >> $ENV_FILE
    echo "✓ Set default CORS_ORIGINS"
fi

if ! grep -q "^DB_NAME=" $ENV_FILE; then
    echo "DB_NAME=portfolioDB" >> $ENV_FILE
    echo "✓ Set default DB_NAME"
fi

echo ""
echo "========================================="
echo " Environment file created: $ENV_FILE"
echo "========================================="
echo ""

# Show the file content (mask sensitive values)
echo "Current environment variables:"
cat $ENV_FILE | sed 's/\(.*=\)\(.\{10\}\).*/\1\2.../' 

echo ""
echo "========================================="
echo " Next Steps:"
echo "========================================="
echo ""
echo "1. Review the .env file and update any values if needed:"
echo "   nano $ENV_FILE"
echo ""
echo "2. Stop and remove the existing Docker container:"
echo "   docker stop portfolio-backend"
echo "   docker rm portfolio-backend"
echo ""
echo "3. Start the container with the new environment file:"
echo "   docker run -d \\"
echo "     --name portfolio-backend \\"
echo "     --restart unless-stopped \\"
echo "     --env-file $(pwd)/$ENV_FILE \\"
echo "     -p 8000:8000 \\"
echo "     portfolio-backend:latest"
echo ""
echo "4. Check if the container is running:"
echo "   docker ps"
echo ""
echo "5. View logs to verify everything is working:"
echo "   docker logs portfolio-backend --tail 50"
echo ""
echo "6. Run the deployment fix script to seed data:"
echo "   python3 backend/fix_deployment.py"
echo ""
