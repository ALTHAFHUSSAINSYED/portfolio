#!/usr/bin/env python3
"""
ChromaDB Category Filtering Test Suite (Task 14)
Tests portfolio_master collection metadata filtering capabilities

This script validates:
1. Category filtering: {category: 'profile'}, {category: 'project'}, {category: 'blog'}
2. $or metadata queries: {$or: [{category: 'project'}, {category: 'profile'}]}
3. $in operator: {category: {$in: ['blog', 'project']}}
4. Subcategory filtering for blogs: {category: 'blog', subcategory: 'DevOps'}
5. Data integrity: Verify all items have correct category tags

Usage:
    python backend/test_category_filtering.py
    
Environment Variables:
    CHROMA_API_KEY: ChromaDB Cloud API key
    CHROMA_TENANT_ID: ChromaDB tenant ID
    CHROMA_DATABASE: Database name (default: Development)
    GEMINI_API_KEY: Google Gemini API key for embeddings
"""

import os
import chromadb
import google.generativeai as genai
from chromadb import EmbeddingFunction, Documents, Embeddings
from dotenv import load_dotenv
from typing import Dict, List

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env.local'))

# ANSI color codes
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"

# Configure Gemini
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

# Embedding function
class GeminiEmbeddingFunction(EmbeddingFunction):
    def __init__(self):
        pass

    def __call__(self, input: Documents) -> Embeddings:
        try:
            return [
                genai.embed_content(
                    model='models/text-embedding-004',
                    content=text,
                    task_type="retrieval_query"
                )['embedding']
                for text in input
            ]
        except Exception as e:
            print(f"{RED}Embedding failed: {e}{RESET}")
            return [[0.0] * 768 for _ in input]

class CategoryFilterTester:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.client = None
        self.collection = None
        
    def connect(self):
        """Connect to ChromaDB"""
        try:
            chroma_api_key = os.getenv('CHROMA_API_KEY')
            chroma_tenant = os.getenv('CHROMA_TENANT_ID')
            chroma_database = os.getenv('CHROMA_DATABASE', 'Development')
            
            if not all([chroma_api_key, chroma_tenant]):
                raise ValueError("Missing CHROMA_API_KEY or CHROMA_TENANT_ID")
            
            print(f"{BLUE}Connecting to ChromaDB Cloud...{RESET}")
            print(f"  Database: {chroma_database}")
            print(f"  Tenant: {chroma_tenant}")
            
            self.client = chromadb.CloudClient(
                api_key=chroma_api_key,
                tenant=chroma_tenant,
                database=chroma_database
            )
            
            print(f"{GREEN}✅ Connected successfully{RESET}\n")
            return True
            
        except Exception as e:
            print(f"{RED}❌ Connection failed: {e}{RESET}")
            return False
    
    def get_collection(self):
        """Get portfolio_master collection"""
        try:
            print(f"{BLUE}Getting portfolio_master collection...{RESET}")
            self.collection = self.client.get_collection(
                name='portfolio_master',
                embedding_function=GeminiEmbeddingFunction()
            )
            
            count = self.collection.count()
            print(f"{GREEN}✅ Found portfolio_master with {count} documents{RESET}\n")
            return True
            
        except Exception as e:
            print(f"{RED}❌ Failed to get collection: {e}{RESET}")
            print(f"{YELLOW}Hint: Run migrate_to_master.py first to create the collection{RESET}\n")
            return False
    
    def test_category_filter(self, category: str, expected_min: int = 1):
        """Test single category filter"""
        test_name = f"Category Filter: {{category: '{category}'}}"
        print(f"{BLUE}Test: {test_name}{RESET}")
        
        try:
            results = self.collection.query(
                query_texts=[f"Tell me about {category}"],
                n_results=20,
                where={"category": category}
            )
            
            ids = results.get('ids', [[]])[0]
            metadatas = results.get('metadatas', [[]])[0]
            
            print(f"  Found {len(ids)} documents")
            
            # Verify all results have correct category
            invalid = [m for m in metadatas if m.get('category') != category]
            
            if len(ids) < expected_min:
                print(f"{RED}❌ FAILED - Expected at least {expected_min} documents, got {len(ids)}{RESET}")
                self.failed += 1
                return False
            
            if invalid:
                print(f"{RED}❌ FAILED - Found {len(invalid)} documents with wrong category{RESET}")
                self.failed += 1
                return False
            
            print(f"{GREEN}✅ PASSED - All {len(ids)} documents have category='{category}'{RESET}\n")
            self.passed += 1
            return True
            
        except Exception as e:
            print(f"{RED}❌ FAILED - {e}{RESET}\n")
            self.failed += 1
            return False
    
    def test_or_filter(self):
        """Test $or metadata query"""
        test_name = "$or Filter: {$or: [{category: 'project'}, {category: 'profile'}]}"
        print(f"{BLUE}Test: {test_name}{RESET}")
        
        try:
            results = self.collection.query(
                query_texts=["Show me projects and profile"],
                n_results=20,
                where={"$or": [{"category": "project"}, {"category": "profile"}]}
            )
            
            ids = results.get('ids', [[]])[0]
            metadatas = results.get('metadatas', [[]])[0]
            
            print(f"  Found {len(ids)} documents")
            
            # Verify all results are either project or profile
            invalid = [m for m in metadatas if m.get('category') not in ['project', 'profile']]
            
            # Count each category
            project_count = sum(1 for m in metadatas if m.get('category') == 'project')
            profile_count = sum(1 for m in metadatas if m.get('category') == 'profile')
            
            print(f"  - Projects: {project_count}")
            print(f"  - Profile: {profile_count}")
            
            if invalid:
                print(f"{RED}❌ FAILED - Found {len(invalid)} documents with invalid categories{RESET}")
                self.failed += 1
                return False
            
            if len(ids) < 1:
                print(f"{RED}❌ FAILED - No documents returned{RESET}")
                self.failed += 1
                return False
            
            print(f"{GREEN}✅ PASSED - All documents match $or filter{RESET}\n")
            self.passed += 1
            return True
            
        except Exception as e:
            print(f"{RED}❌ FAILED - {e}{RESET}\n")
            self.failed += 1
            return False
    
    def test_in_filter(self):
        """Test $in operator"""
        test_name = "$in Filter: {category: {$in: ['blog', 'project']}}"
        print(f"{BLUE}Test: {test_name}{RESET}")
        
        try:
            results = self.collection.query(
                query_texts=["Show me blogs and projects"],
                n_results=20,
                where={"category": {"$in": ["blog", "project"]}}
            )
            
            ids = results.get('ids', [[]])[0]
            metadatas = results.get('metadatas', [[]])[0]
            
            print(f"  Found {len(ids)} documents")
            
            # Verify all results are either blog or project
            invalid = [m for m in metadatas if m.get('category') not in ['blog', 'project']]
            
            # Count each category
            blog_count = sum(1 for m in metadatas if m.get('category') == 'blog')
            project_count = sum(1 for m in metadatas if m.get('category') == 'project')
            
            print(f"  - Blogs: {blog_count}")
            print(f"  - Projects: {project_count}")
            
            if invalid:
                print(f"{RED}❌ FAILED - Found {len(invalid)} documents with invalid categories{RESET}")
                self.failed += 1
                return False
            
            if len(ids) < 1:
                print(f"{RED}❌ FAILED - No documents returned{RESET}")
                self.failed += 1
                return False
            
            print(f"{GREEN}✅ PASSED - All documents match $in filter{RESET}\n")
            self.passed += 1
            return True
            
        except Exception as e:
            print(f"{RED}❌ FAILED - {e}{RESET}\n")
            self.failed += 1
            return False
    
    def test_subcategory_filter(self):
        """Test subcategory filtering for blogs"""
        test_name = "Subcategory Filter: {category: 'blog', subcategory: 'DevOps'}"
        print(f"{BLUE}Test: {test_name}{RESET}")
        
        try:
            # First, get all blogs to see available subcategories
            all_blogs = self.collection.query(
                query_texts=["DevOps blogs"],
                n_results=50,
                where={"category": "blog"}
            )
            
            all_subcategories = set()
            for meta in all_blogs.get('metadatas', [[]])[0]:
                if 'subcategory' in meta:
                    all_subcategories.add(meta['subcategory'])
            
            print(f"  Available subcategories: {all_subcategories}")
            
            if not all_subcategories:
                print(f"{YELLOW}⚠️  SKIPPED - No subcategories found{RESET}\n")
                return True
            
            # Test filtering by a specific subcategory
            test_subcategory = list(all_subcategories)[0]
            results = self.collection.query(
                query_texts=[f"{test_subcategory} blogs"],
                n_results=10,
                where={"category": "blog", "subcategory": test_subcategory}
            )
            
            ids = results.get('ids', [[]])[0]
            metadatas = results.get('metadatas', [[]])[0]
            
            print(f"  Found {len(ids)} documents with subcategory='{test_subcategory}'")
            
            # Verify all results have correct category and subcategory
            invalid = [m for m in metadatas 
                      if m.get('category') != 'blog' or m.get('subcategory') != test_subcategory]
            
            if invalid:
                print(f"{RED}❌ FAILED - Found {len(invalid)} documents with wrong category/subcategory{RESET}")
                self.failed += 1
                return False
            
            print(f"{GREEN}✅ PASSED - All documents match subcategory filter{RESET}\n")
            self.passed += 1
            return True
            
        except Exception as e:
            print(f"{RED}❌ FAILED - {e}{RESET}\n")
            self.failed += 1
            return False
    
    def test_data_integrity(self):
        """Verify all documents have required category tags"""
        test_name = "Data Integrity: All documents have 'category' field"
        print(f"{BLUE}Test: {test_name}{RESET}")
        
        try:
            # Get all documents without filter
            all_data = self.collection.get()
            
            total_count = len(all_data['ids'])
            print(f"  Total documents: {total_count}")
            
            # Check category distribution
            category_counts = {}
            missing_category = 0
            
            for meta in all_data['metadatas']:
                cat = meta.get('category')
                if cat:
                    category_counts[cat] = category_counts.get(cat, 0) + 1
                else:
                    missing_category += 1
            
            print(f"  Category distribution:")
            for cat, count in category_counts.items():
                print(f"    - {cat}: {count}")
            
            if missing_category > 0:
                print(f"{RED}❌ FAILED - {missing_category} documents missing 'category' field{RESET}")
                self.failed += 1
                return False
            
            # Verify expected categories exist
            expected_categories = {'profile', 'project', 'blog'}
            found_categories = set(category_counts.keys())
            
            if not expected_categories.issubset(found_categories):
                missing = expected_categories - found_categories
                print(f"{RED}❌ FAILED - Missing expected categories: {missing}{RESET}")
                self.failed += 1
                return False
            
            print(f"{GREEN}✅ PASSED - All documents have valid category tags{RESET}\n")
            self.passed += 1
            return True
            
        except Exception as e:
            print(f"{RED}❌ FAILED - {e}{RESET}\n")
            self.failed += 1
            return False
    
    def run_all_tests(self):
        """Run all category filtering tests"""
        print(f"\n{BLUE}{'='*80}{RESET}")
        print(f"{BLUE}CHROMADB CATEGORY FILTERING TEST SUITE{RESET}")
        print(f"{BLUE}{'='*80}{RESET}\n")
        
        # Connect to ChromaDB
        if not self.connect():
            return False
        
        # Get portfolio_master collection
        if not self.get_collection():
            return False
        
        # Run tests
        self.test_data_integrity()
        self.test_category_filter('profile', expected_min=5)
        self.test_category_filter('project', expected_min=1)
        self.test_category_filter('blog', expected_min=1)
        self.test_or_filter()
        self.test_in_filter()
        self.test_subcategory_filter()
        
        # Print summary
        self.print_summary()
        
        return self.failed == 0
    
    def print_summary(self):
        """Print test summary"""
        total = self.passed + self.failed
        pass_rate = (self.passed / total * 100) if total > 0 else 0
        
        print(f"\n{BLUE}{'='*80}{RESET}")
        print(f"{BLUE}TEST SUMMARY{RESET}")
        print(f"{BLUE}{'='*80}{RESET}")
        print(f"Total Tests: {total}")
        print(f"{GREEN}Passed: {self.passed}{RESET}")
        print(f"{RED}Failed: {self.failed}{RESET}")
        print(f"Pass Rate: {pass_rate:.1f}%")
        
        if self.failed == 0:
            print(f"\n{GREEN}{'='*80}{RESET}")
            print(f"{GREEN}🎉 ALL TESTS PASSED! Category filtering is working correctly.{RESET}")
            print(f"{GREEN}{'='*80}{RESET}")
        else:
            print(f"\n{RED}{'='*80}{RESET}")
            print(f"{RED}⚠️  SOME TESTS FAILED. Review the output above for details.{RESET}")
            print(f"{RED}{'='*80}{RESET}")

if __name__ == "__main__":
    tester = CategoryFilterTester()
    
    try:
        success = tester.run_all_tests()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Tests interrupted by user{RESET}")
        exit(1)
    except Exception as e:
        print(f"\n{RED}Fatal error: {e}{RESET}")
        import traceback
        traceback.print_exc()
        exit(1)
