# Security Measures for Portfolio Web App

This document outlines the security measures implemented in the Portfolio Web Application.

## 1. Input Sanitization

We use the `bleach` library to sanitize user inputs, protecting against XSS (Cross-Site Scripting) attacks:

- All form inputs are sanitized before processing
- HTML content is filtered to allow only safe tags and attributes
- Rich text content uses a more permissive but still secure sanitization

## 2. HTTPS Enforcement

The application enforces HTTPS connections in production environments:

- HTTP requests are automatically redirected to HTTPS
- The redirect is disabled in development environments
- HSTS headers are set to ensure browsers always use HTTPS

## 3. Security Headers

The following security headers are added to all responses:

- **X-Content-Type-Options**: Prevents MIME type sniffing
- **X-Frame-Options**: Controls iframe embedding to prevent clickjacking
- **X-XSS-Protection**: Enables browser XSS protection
- **Strict-Transport-Security**: Enforces HTTPS connections
- **Referrer-Policy**: Controls information in the Referer header
- **Content-Security-Policy**: Controls resource loading
- **Permissions-Policy**: Controls browser feature permissions

## 4. API Rate Limiting & Fallbacks

The application implements rate limiting and fallback mechanisms:

- Search API has rate limiting to prevent abuse
- Automatic fallback from Serper.dev API to DuckDuckGo when limits are reached
- Caching of search results to reduce API calls

## 5. Environment Variables

Sensitive information is stored in environment variables:

- API keys (Sendgrid, Cloudinary, Google Gemini, etc.)
- Database connection strings
- Email configuration

## 6. Error Handling

Proper error handling prevents information leakage:

- Generic error messages for users
- Detailed logs for developers
- Failed operations gracefully degrade

## 7. CORS Configuration

Cross-Origin Resource Sharing is properly configured:

- Only allowed origins can access the API
- Proper headers for secure cross-origin requests

## Usage Guidelines

1. Always keep dependencies up to date
2. Regularly review and update security policies
3. Validate all user inputs
4. Use HTTPS in production
5. Monitor logs for suspicious activity

## Implemented Files

- `security_utils.py`: Contains security utility functions and middleware
- Security middleware added to `server.py`
- Input sanitization added to all endpoints that accept user input