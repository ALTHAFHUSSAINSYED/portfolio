# Google Gemini API Integration

This portfolio project uses Google Gemini API as the AI service for chatbot functionality and blog generation. Gemini provides powerful language model capabilities for generating content and answering questions.

## Getting Started with Gemini

### 1. Create a Google AI Studio Account

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign up or log in with your Google account
3. New users receive free credits to use with the Gemini API

### 2. Generate an API Key

1. In Google AI Studio, navigate to the "Get API key" section
2. Create a new API key for your project
3. Copy the API key for use in your application

### 3. Configure Your Environment

1. Add your Gemini API key to the `.env` file:
   ```
   GEMINI_API_KEY="your_gemini_api_key"
   ```


### 4. Testing Your Setup

Run the included test script to verify your Gemini API integration:

```
python test_gemini.py
```

## Features Enabled by Gemini

- **Blog Generation**: AI-powered blog content creation
- **Web Search Enhancements**: Better contextual understanding of search results
- **Fallback Mechanism**: Graceful fallback to template-based generation if API limits are reached

## Advantages of Gemini API

- Free tier for new users with generous allowances
- Web searching capabilities built into the API
- Strong performance on technical and general knowledge topics
- Regular model improvements from Google AI

## Troubleshooting

If you encounter any issues with the Gemini API integration:

1. Verify your API key is correctly set in the `.env` file
2. Check that you have internet access and can reach Google's APIs
3. Review the application logs for specific error messages
4. The application will use template-based generation if Gemini API is unavailable

For more information, see the [Google Generative AI documentation](https://ai.google.dev/).