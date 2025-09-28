# Serper.dev API Integration Guide

## Overview

This document outlines how the Serper.dev Google Search API is integrated into the portfolio project, with a focus on credit-saving strategies. Since the free tier of Serper.dev provides only 2,500 credits, implementing optimization techniques is crucial for sustainable usage.

## Serper.dev API Basics

- **API Endpoint**: https://google.serper.dev/search
- **Free Tier**: 2,500 credits
- **Credit Usage**: Each search query consumes 1 credit
- **API Key**: Stored in `.env` file as `SERPER_API_KEY`

## Credit-Saving Features

### 1. Search Result Caching

The system implements an intelligent caching mechanism to store search results and reduce redundant API calls.

**Implementation Details:**
- Cache storage: JSON files in the `cache/` directory
- Default cache expiry: 24 hours (configurable)
- Cache key: MD5 hash of query string + parameters
- Cache hit tracking: Statistics on hits/misses for reporting

**Benefits:**
- Eliminates redundant API calls for identical searches
- Significantly reduces credit consumption
- Improves response times for repeated queries

### 2. Rate Limiting

Rate limiting prevents accidental API abuse and ensures the application stays within intended usage limits.

**Implementation Details:**
- Default limit: 100 requests per hour (configurable)
- Rolling window implementation
- Tracks request timestamps to enforce limits

**Benefits:**
- Prevents unexpected credit depletion
- Provides visibility into API usage patterns
- Helps maintain sustainable credit consumption

### 3. Query Optimization

Smart query processing improves search result quality while minimizing the need for additional searches.

**Implementation Details:**
- Removes filler words for more precise results
- Adds strategic qualifiers for certain query types
- Preserves original query for short searches

**Benefits:**
- Improves search result relevance
- Reduces need for follow-up searches
- More efficient use of available credits

## Usage Monitoring

### Dashboard

A dashboard utility (`serper_dashboard.py`) provides real-time visibility into API usage:

```
python serper_dashboard.py
```

The dashboard displays:
- Current rate limit status
- Cache statistics
- Estimated credits saved
- Cache storage information
- Tips for further credit optimization

### Admin Utilities

Administrative functions (`serper_admin.py`) help manage the cache and system:

```
# View cache entries
python serper_admin.py cache list

# Clear expired cache entries
python serper_admin.py cache clear --expired-only

# Clear all cache
python serper_admin.py cache clear

# Run diagnostics
python serper_admin.py diagnostics
```

## Best Practices for Credit Conservation

1. **Be Specific in Queries**: Use precise search terms to get relevant results in a single query

2. **Schedule Blog Generation**: Implement weekly rather than daily blog generation to reduce query volume

3. **Regular Maintenance**: Clear expired cache entries weekly, not the entire cache

4. **Monitor Usage**: Check the dashboard regularly to track credit consumption

5. **Batch Operations**: Group related searches together to maximize cache efficiency

## Integration Examples

### Basic Search Example

```python
from search_utils import search_cache, rate_limiter, query_optimizer
import requests
import os
from dotenv import load_dotenv

load_dotenv()

def search_web(query, params=None):
    # Check cache first
    cached_results = search_cache.get(query, params)
    if cached_results:
        print("Using cached results")
        return cached_results
    
    # Check rate limit
    if not rate_limiter.check_limit():
        print("Rate limit reached, try again later")
        return None
    
    # Optimize query
    optimized_query = query_optimizer.optimize_query(query)
    
    # Make API request
    api_key = os.getenv("SERPER_API_KEY")
    headers = {
        'X-API-KEY': api_key,
        'Content-Type': 'application/json'
    }
    
    data = {
        'q': optimized_query
    }
    if params:
        data.update(params)
    
    response = requests.post(
        'https://google.serper.dev/search',
        headers=headers,
        json=data
    )
    
    # Record the request
    rate_limiter.add_request()
    
    if response.status_code == 200:
        results = response.json()
        # Cache the results
        search_cache.set(query, results, params)
        return results
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None
```

## Conclusion

The implemented credit-saving features ensure efficient use of the limited Serper.dev API credits. By leveraging caching, rate limiting, and query optimization, the system significantly reduces API calls while maintaining functionality.

Regular monitoring through the dashboard and proper maintenance with the admin utilities will help maximize the value of the free tier allocation.