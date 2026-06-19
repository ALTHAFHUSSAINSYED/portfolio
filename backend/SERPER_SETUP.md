# Setting Up Serper.dev for Web Search

Serper.dev provides a reliable Google Search API that allows your portfolio agent to perform web searches with better results than the fallback method.

## Steps to Set Up Serper.dev

1. **Create a Serper.dev Account**:
   - Go to [Serper.dev](https://serper.dev) and sign up for an account
   - They offer a free tier with limited searches per month, or paid plans for more usage

2. **Get Your API Key**:
   - After creating an account, navigate to the dashboard
   - Find and copy your API key

3. **Add the API Key to Your Environment**:
   - Open your `.env` file in the backend directory
   - Add the following line:
     ```
     SERPER_API_KEY=your_api_key_here
     ```
   - Replace `your_api_key_here` with the actual API key you copied

4. **Test the Configuration**:
   - Run the test script to verify Serper.dev is working correctly:
     ```
     python test_serper.py
     ```

## Usage in Code

The agent service is already configured to use Serper.dev if the API key is available. It will:

1. Use Serper.dev as the primary search method
2. Fall back to other methods if Serper.dev fails or is not configured

## Serper.dev API Response Format

When working with Serper.dev, the API returns results in the following format:

```json
{
  "searchParameters": {
    "q": "your search query",
    "gl": "us",
    "hl": "en",
    "num": 10,
    "type": "search"
  },
  "organic": [
    {
      "title": "Result title",
      "link": "https://example.com/page",
      "snippet": "A snippet of the content...",
      "position": 1,
      "attributes": {}
    },
    // More results...
  ],
  "relatedSearches": [
    {
      "query": "related search 1"
    },
    // More related searches...
  ],
  "peopleAlsoAsk": [
    {
      "question": "Common question",
      "answer": "Answer to the question",
      "title": "Source title",
      "link": "https://example.com/source"
    },
    // More questions...
  ]
}
```

The `WebSearchEngine._extract_serper_results` method handles parsing this format.

## Monitoring Usage

You can monitor your Serper.dev API usage on their dashboard to ensure you stay within your plan limits.