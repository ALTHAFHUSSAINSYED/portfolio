"""
Serper API Admin Utility

This script provides administrative functions for managing the Serper API usage,
including cache management, statistics, and configuration.
"""

import os
import argparse
import json
from datetime import datetime, timedelta
from search_utils import search_cache, rate_limiter, logger

def clear_cache():
    """Clear all cached search results"""
    cache_dir = search_cache.cache_dir
    cache_files = [f for f in os.listdir(cache_dir) if f.endswith('.json')]
    
    count = 0
    for file in cache_files:
        file_path = os.path.join(cache_dir, file)
        try:
            os.remove(file_path)
            count += 1
        except Exception as e:
            logger.error(f"Error removing cache file {file}: {e}")
    
    return count

def clear_expired_cache():
    """Clear only expired cache entries"""
    return search_cache.clear_expired()

def export_cache_metadata():
    """Export metadata about cached queries"""
    cache_dir = search_cache.cache_dir
    cache_files = [f for f in os.listdir(cache_dir) if f.endswith('.json')]
    
    metadata = []
    for file in cache_files:
        file_path = os.path.join(cache_dir, file)
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                
            cache_time = datetime.fromisoformat(data['timestamp'])
            age = (datetime.now() - cache_time).total_seconds() / 3600  # age in hours
            
            metadata.append({
                'query': data.get('query', 'Unknown'),
                'timestamp': data['timestamp'],
                'age_hours': round(age, 1),
                'expired': age > search_cache.max_age.total_seconds() / 3600,
                'file': file
            })
        except Exception as e:
            logger.error(f"Error reading cache file {file}: {e}")
    
    # Sort by timestamp (newest first)
    metadata.sort(key=lambda x: x['timestamp'], reverse=True)
    return metadata

def run_diagnostics():
    """Run diagnostics on the search system"""
    results = {
        'cache': {
            'directory': search_cache.cache_dir,
            'exists': os.path.exists(search_cache.cache_dir),
            'writeable': os.access(search_cache.cache_dir, os.W_OK) if os.path.exists(search_cache.cache_dir) else False,
            'max_age_hours': search_cache.max_age.total_seconds() / 3600
        },
        'rate_limiter': {
            'max_requests': rate_limiter.max_requests,
            'time_window_seconds': rate_limiter.time_window,
            'current_usage': len(rate_limiter.request_timestamps),
            'remaining': rate_limiter.get_remaining()
        }
    }
    
    # Check cache files
    if results['cache']['exists']:
        cache_files = [f for f in os.listdir(search_cache.cache_dir) if f.endswith('.json')]
        results['cache']['files'] = len(cache_files)
        
        # Check if we can read/write a test file
        try:
            test_file = os.path.join(search_cache.cache_dir, 'test_write.tmp')
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
            results['cache']['io_test'] = 'PASS'
        except Exception as e:
            results['cache']['io_test'] = f'FAIL: {str(e)}'
    
    return results

def main():
    """Main entry point for the admin utility"""
    parser = argparse.ArgumentParser(description='Serper API Admin Utility')
    
    # Command groups
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Cache commands
    cache_parser = subparsers.add_parser('cache', help='Cache management')
    cache_subparsers = cache_parser.add_subparsers(dest='cache_command')
    
    clear_parser = cache_subparsers.add_parser('clear', help='Clear cache')
    clear_parser.add_argument('--expired-only', action='store_true', help='Clear only expired cache entries')
    
    list_parser = cache_subparsers.add_parser('list', help='List cache entries')
    list_parser.add_argument('--json', action='store_true', help='Output in JSON format')
    
    # Diagnostics command
    subparsers.add_parser('diagnostics', help='Run system diagnostics')
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Handle cache commands
    if args.command == 'cache':
        if args.cache_command == 'clear':
            if args.expired_only:
                count = clear_expired_cache()
                print(f"Cleared {count} expired cache entries")
            else:
                count = clear_cache()
                print(f"Cleared {count} cache entries")
        elif args.cache_command == 'list':
            metadata = export_cache_metadata()
            if args.json:
                print(json.dumps(metadata, indent=2))
            else:
                print(f"Found {len(metadata)} cached queries:")
                print("=" * 80)
                for entry in metadata:
                    expired_mark = "EXPIRED" if entry['expired'] else "VALID"
                    print(f"{entry['query'][:50]:<50} | {entry['age_hours']:>5} hours | {expired_mark}")
                print("=" * 80)
    
    # Handle diagnostics command
    elif args.command == 'diagnostics':
        results = run_diagnostics()
        print("\nDiagnostic Results:")
        print("=" * 80)
        
        # Cache info
        print("\nCache Configuration:")
        print(f"  Directory: {results['cache']['directory']}")
        print(f"  Directory exists: {results['cache']['exists']}")
        print(f"  Directory writeable: {results['cache']['writeable']}")
        print(f"  Maximum cache age: {results['cache']['max_age_hours']} hours")
        if 'files' in results['cache']:
            print(f"  Cached files: {results['cache']['files']}")
        if 'io_test' in results['cache']:
            print(f"  I/O test: {results['cache']['io_test']}")
        
        # Rate limiter info
        print("\nRate Limiter Configuration:")
        print(f"  Max requests: {results['rate_limiter']['max_requests']}")
        print(f"  Time window: {results['rate_limiter']['time_window_seconds']} seconds")
        print(f"  Current usage: {results['rate_limiter']['current_usage']}")
        print(f"  Remaining requests: {results['rate_limiter']['remaining']}")
        
        print("\nDiagnostics complete!")

if __name__ == "__main__":
    main()