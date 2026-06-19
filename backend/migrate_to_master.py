"""
ChromaDB Migration Script: Legacy Collections → portfolio_master
===================================================================
Migrates data from 3 separate collections to unified portfolio_master collection.

Features:
- ✅ Reuses existing embeddings (no Gemini API cost)
- ✅ Adds category metadata tags (profile/project/blog)
- ✅ Preserves all original metadata
- ✅ Validates data integrity
- ✅ Provides rollback instructions

Collections:
- portfolio → portfolio_master (category='profile')
- Projects_data → portfolio_master (category='project')
- Blogs_data → portfolio_master (category='blog')

Usage:
    python backend/migrate_to_master.py [--dry-run] [--force]

Options:
    --dry-run    Show migration plan without executing
    --force      Delete existing portfolio_master and recreate

Author: AI Coding Agent (GitHub Copilot)
Date: January 2, 2026
"""

import chromadb
import os
import sys
import logging
from dotenv import load_dotenv
from typing import Dict, List, Optional
from datetime import datetime
import google.generativeai as genai
from chromadb import Documents, EmbeddingFunction, Embeddings

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env.local'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('migration.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# --- CONFIGURATION ---
GOOGLE_API_KEY = os.getenv('GEMINI_API_KEY')
CHROMA_API_KEY = os.getenv('CHROMA_API_KEY')
CHROMA_TENANT_ID = os.getenv('CHROMA_TENANT_ID')
CHROMA_DB_NAME = os.getenv('CHROMA_DB_NAME', 'Development')

if not GOOGLE_API_KEY:
    logger.error("GEMINI_API_KEY is missing")
    sys.exit(1)

if not CHROMA_API_KEY:
    logger.error("CHROMA_API_KEY is missing")
    sys.exit(1)

# Configure Gemini
genai.configure(api_key=GOOGLE_API_KEY)

# --- GEMINI EMBEDDING CLASS ---
class GeminiEmbeddingFunction(EmbeddingFunction):
    """Gemini text-embedding-004 (768 dimensions)"""
    def __init__(self):
        pass

    def __call__(self, input: Documents) -> Embeddings:
        model = 'models/text-embedding-004'
        try:
            return [
                genai.embed_content(
                    model=model,
                    content=text,
                    task_type="retrieval_document"
                )['embedding']
                for text in input
            ]
        except Exception as e:
            logger.error(f"Embedding failed: {e}")
            return [[0.0] * 768 for _ in input]


class ChromaDBMigrator:
    """Handles migration from legacy collections to portfolio_master"""
    
    def __init__(self, dry_run: bool = False, force: bool = False):
        """
        Initialize migrator
        
        Args:
            dry_run: Show plan without executing
            force: Delete existing portfolio_master
        """
        self.dry_run = dry_run
        self.force = force
        self.client = None
        self.embed_function = GeminiEmbeddingFunction()
        
        # Migration statistics
        self.stats = {
            'profile': {'success': 0, 'failed': 0},
            'project': {'success': 0, 'failed': 0},
            'blog': {'success': 0, 'failed': 0}
        }
        
    def connect(self):
        """Connect to ChromaDB Cloud"""
        try:
            logger.info("Connecting to ChromaDB Cloud...")
            self.client = chromadb.CloudClient(
                api_key=CHROMA_API_KEY,
                tenant=CHROMA_TENANT_ID,
                database=CHROMA_DB_NAME
            )
            logger.info("✅ Connected to ChromaDB Cloud")
            return True
        except Exception as e:
            logger.error(f"❌ Connection failed: {e}")
            return False
    
    def check_legacy_collections(self) -> Dict[str, int]:
        """
        Check existence and count of legacy collections
        
        Returns:
            Dictionary with collection names and item counts
        """
        logger.info("\n📊 Checking legacy collections...")
        
        collection_counts = {}
        legacy_collections = ['portfolio', 'Projects_data', 'Blogs_data']
        
        for col_name in legacy_collections:
            try:
                collection = self.client.get_collection(
                    name=col_name,
                    embedding_function=self.embed_function
                )
                count = collection.count()
                collection_counts[col_name] = count
                logger.info(f"  ✅ {col_name}: {count} items")
            except Exception as e:
                logger.warning(f"  ⚠️ {col_name}: Not found ({e})")
                collection_counts[col_name] = 0
        
        return collection_counts
    
    def check_master_collection(self) -> Optional[int]:
        """
        Check if portfolio_master already exists
        
        Returns:
            Item count if exists, None otherwise
        """
        logger.info("\n🔍 Checking for existing portfolio_master...")
        
        try:
            collection = self.client.get_collection(
                name='portfolio_master',
                embedding_function=self.embed_function
            )
            count = collection.count()
            logger.info(f"  ⚠️ portfolio_master exists with {count} items")
            return count
        except Exception:
            logger.info("  ✅ portfolio_master does not exist (ready for migration)")
            return None
    
    def create_master_collection(self):
        """Create empty portfolio_master collection"""
        if self.dry_run:
            logger.info("[DRY-RUN] Would create portfolio_master collection")
            return
        
        try:
            logger.info("\n🔧 Creating portfolio_master collection...")
            collection = self.client.create_collection(
                name='portfolio_master',
                embedding_function=self.embed_function,
                metadata={"description": "Unified collection for portfolio, projects, and blogs"}
            )
            logger.info("✅ portfolio_master created successfully")
            return collection
        except Exception as e:
            logger.error(f"❌ Failed to create portfolio_master: {e}")
            raise
    
    def delete_master_collection(self):
        """Delete existing portfolio_master (for --force mode)"""
        if self.dry_run:
            logger.info("[DRY-RUN] Would delete existing portfolio_master")
            return
        
        try:
            logger.info("🗑️ Deleting existing portfolio_master...")
            self.client.delete_collection('portfolio_master')
            logger.info("✅ portfolio_master deleted")
        except Exception as e:
            logger.warning(f"⚠️ Could not delete portfolio_master: {e}")
    
    def migrate_collection(self, source_name: str, category: str, subcategory_field: Optional[str] = None):
        """
        Migrate data from source collection to portfolio_master
        
        Args:
            source_name: Source collection name (portfolio, Projects_data, Blogs_data)
            category: Category tag to add (profile, project, blog)
            subcategory_field: Field to use as subcategory (e.g., 'category' for blogs)
        """
        logger.info(f"\n📦 Migrating {source_name} → portfolio_master (category='{category}')...")
        
        try:
            # Get source collection
            source_col = self.client.get_collection(
                name=source_name,
                embedding_function=self.embed_function
            )
            
            # Get master collection
            master_col = self.client.get_collection(
                name='portfolio_master',
                embedding_function=self.embed_function
            )
            
            # Fetch ALL data (including embeddings to reuse them)
            data = source_col.get(include=['embeddings', 'documents', 'metadatas'])
            
            if not data['ids']:
                logger.warning(f"  ⚠️ {source_name} is empty, skipping")
                return
            
            total_items = len(data['ids'])
            logger.info(f"  Found {total_items} items in {source_name}")
            
            if self.dry_run:
                logger.info(f"[DRY-RUN] Would migrate {total_items} items")
                logger.info(f"[DRY-RUN] Sample metadata: {data['metadatas'][0] if data['metadatas'] else 'N/A'}")
                return
            
            # Process in batches (ChromaDB recommends <1000 items per batch)
            batch_size = 500
            for i in range(0, total_items, batch_size):
                batch_end = min(i + batch_size, total_items)
                batch_ids = data['ids'][i:batch_end]
                batch_embeddings = data['embeddings'][i:batch_end]
                batch_documents = data['documents'][i:batch_end]
                batch_metadatas = data['metadatas'][i:batch_end]
                
                # Add category tags to metadata
                updated_metadatas = []
                for meta in batch_metadatas:
                    updated_meta = meta.copy()
                    updated_meta['category'] = category
                    
                    # Add subcategory for blogs (DevOps, Cloud, Cybersecurity, etc.)
                    if subcategory_field and subcategory_field in meta:
                        updated_meta['subcategory'] = meta[subcategory_field]
                    
                    updated_metadatas.append(updated_meta)
                
                # Upsert to master collection (reuses embeddings)
                try:
                    master_col.upsert(
                        ids=batch_ids,
                        embeddings=batch_embeddings,  # ✅ Reuse existing embeddings (no API cost)
                        documents=batch_documents,
                        metadatas=updated_metadatas
                    )
                    
                    batch_count = len(batch_ids)
                    self.stats[category]['success'] += batch_count
                    logger.info(f"  ✅ Batch {i//batch_size + 1}: Migrated {batch_count} items")
                    
                except Exception as e:
                    logger.error(f"  ❌ Batch {i//batch_size + 1} failed: {e}")
                    self.stats[category]['failed'] += len(batch_ids)
            
            logger.info(f"✅ {source_name} migration complete: {self.stats[category]['success']} items")
            
        except Exception as e:
            logger.error(f"❌ Migration failed for {source_name}: {e}")
            import traceback
            traceback.print_exc()
    
    def validate_migration(self, legacy_counts: Dict[str, int]):
        """
        Validate migration integrity
        
        Args:
            legacy_counts: Original counts from legacy collections
        """
        logger.info("\n🔍 Validating migration integrity...")
        
        try:
            master_col = self.client.get_collection(
                name='portfolio_master',
                embedding_function=self.embed_function
            )
            
            # Get total count
            master_count = master_col.count()
            expected_count = sum(legacy_counts.values())
            
            logger.info(f"  Total items in portfolio_master: {master_count}")
            logger.info(f"  Expected total (legacy sum): {expected_count}")
            
            # Check category distribution
            profile_count = len(master_col.get(where={"category": "profile"})['ids'])
            project_count = len(master_col.get(where={"category": "project"})['ids'])
            blog_count = len(master_col.get(where={"category": "blog"})['ids'])
            
            logger.info(f"\n  Category Distribution:")
            logger.info(f"    profile: {profile_count} (expected: {legacy_counts.get('portfolio', 0)})")
            logger.info(f"    project: {project_count} (expected: {legacy_counts.get('Projects_data', 0)})")
            logger.info(f"    blog: {blog_count} (expected: {legacy_counts.get('Blogs_data', 0)})")
            
            # Validation checks
            checks_passed = 0
            total_checks = 4
            
            # Check 1: Total count matches
            if master_count == expected_count:
                logger.info("  ✅ Check 1: Total count matches")
                checks_passed += 1
            else:
                logger.error(f"  ❌ Check 1: Count mismatch ({master_count} != {expected_count})")
            
            # Check 2: Profile count matches
            if profile_count == legacy_counts.get('portfolio', 0):
                logger.info("  ✅ Check 2: Profile count matches")
                checks_passed += 1
            else:
                logger.warning(f"  ⚠️ Check 2: Profile count mismatch")
            
            # Check 3: Project count matches
            if project_count == legacy_counts.get('Projects_data', 0):
                logger.info("  ✅ Check 3: Project count matches")
                checks_passed += 1
            else:
                logger.warning(f"  ⚠️ Check 3: Project count mismatch")
            
            # Check 4: Blog count matches
            if blog_count == legacy_counts.get('Blogs_data', 0):
                logger.info("  ✅ Check 4: Blog count matches")
                checks_passed += 1
            else:
                logger.warning(f"  ⚠️ Check 4: Blog count mismatch")
            
            # Summary
            logger.info(f"\n✅ Validation Summary: {checks_passed}/{total_checks} checks passed")
            
            if checks_passed == total_checks:
                logger.info("🎉 Migration validated successfully!")
                return True
            else:
                logger.warning("⚠️ Migration validation has warnings")
                return False
                
        except Exception as e:
            logger.error(f"❌ Validation failed: {e}")
            return False
    
    def print_summary(self, legacy_counts: Dict[str, int], duration: float):
        """Print migration summary"""
        logger.info("\n" + "="*70)
        logger.info("📊 MIGRATION SUMMARY")
        logger.info("="*70)
        
        logger.info(f"\nLegacy Collections:")
        for col_name, count in legacy_counts.items():
            logger.info(f"  {col_name}: {count} items")
        
        logger.info(f"\nMigration Statistics:")
        for category, stats in self.stats.items():
            total = stats['success'] + stats['failed']
            logger.info(f"  {category}: {stats['success']} success, {stats['failed']} failed (total: {total})")
        
        total_success = sum(s['success'] for s in self.stats.values())
        total_failed = sum(s['failed'] for s in self.stats.values())
        
        logger.info(f"\nOverall:")
        logger.info(f"  Total Success: {total_success}")
        logger.info(f"  Total Failed: {total_failed}")
        logger.info(f"  Duration: {duration:.2f} seconds")
        
        logger.info("\n" + "="*70)
    
    def run(self):
        """Execute migration"""
        start_time = datetime.now()
        
        logger.info("="*70)
        logger.info("🚀 ChromaDB Migration: Legacy → portfolio_master")
        logger.info("="*70)
        logger.info(f"Mode: {'DRY-RUN' if self.dry_run else 'LIVE'}")
        logger.info(f"Force: {'YES' if self.force else 'NO'}")
        logger.info(f"Started: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Step 1: Connect to ChromaDB
        if not self.connect():
            logger.error("Migration aborted: Could not connect to ChromaDB")
            return False
        
        # Step 2: Check legacy collections
        legacy_counts = self.check_legacy_collections()
        total_items = sum(legacy_counts.values())
        
        if total_items == 0:
            logger.error("Migration aborted: No data found in legacy collections")
            return False
        
        logger.info(f"\n📊 Total items to migrate: {total_items}")
        
        # Step 3: Check for existing master collection
        master_count = self.check_master_collection()
        
        if master_count is not None:
            if self.force:
                logger.warning("⚠️ --force mode: Deleting existing portfolio_master")
                self.delete_master_collection()
            else:
                logger.error("\n❌ Migration aborted: portfolio_master already exists")
                logger.error("Use --force to delete and recreate, or --dry-run to preview")
                return False
        
        # Step 4: Create master collection
        if not self.dry_run:
            self.create_master_collection()
        
        # Step 5: Migrate data
        logger.info("\n📦 Starting data migration...")
        
        # Migrate portfolio → profile
        if legacy_counts.get('portfolio', 0) > 0:
            self.migrate_collection('portfolio', 'profile')
        
        # Migrate Projects_data → project
        if legacy_counts.get('Projects_data', 0) > 0:
            self.migrate_collection('Projects_data', 'project')
        
        # Migrate Blogs_data → blog (with subcategory)
        if legacy_counts.get('Blogs_data', 0) > 0:
            self.migrate_collection('Blogs_data', 'blog', subcategory_field='category')
        
        # Step 6: Validate migration
        if not self.dry_run:
            validation_passed = self.validate_migration(legacy_counts)
        else:
            validation_passed = True
            logger.info("\n[DRY-RUN] Skipping validation")
        
        # Step 7: Print summary
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        self.print_summary(legacy_counts, duration)
        
        # Print next steps
        if not self.dry_run and validation_passed:
            logger.info("\n" + "="*70)
            logger.info("🎉 MIGRATION COMPLETE!")
            logger.info("="*70)
            logger.info("\nNext Steps:")
            logger.info("1. Test chatbot queries with portfolio_master")
            logger.info("2. Update server.py to use portfolio_master (Task 11)")
            logger.info("3. Monitor for 48 hours before deleting legacy collections")
            logger.info("\nRollback Instructions (if needed):")
            logger.info("  python backend/migrate_to_master.py --force")
            logger.info("  (This will recreate portfolio_master from legacy collections)")
        elif self.dry_run:
            logger.info("\n[DRY-RUN] No changes made. Run without --dry-run to execute migration.")
        
        return validation_passed


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Migrate ChromaDB collections to unified portfolio_master',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Preview migration (recommended first step)
  python backend/migrate_to_master.py --dry-run
  
  # Execute migration
  python backend/migrate_to_master.py
  
  # Force recreate (deletes existing portfolio_master)
  python backend/migrate_to_master.py --force
        """
    )
    
    parser.add_argument('--dry-run', action='store_true', help='Show migration plan without executing')
    parser.add_argument('--force', action='store_true', help='Delete existing portfolio_master and recreate')
    
    args = parser.parse_args()
    
    # Confirmation for live mode
    if not args.dry_run and not args.force:
        print("\n⚠️ WARNING: This will create portfolio_master collection and migrate all data.")
        print("Existing embeddings will be reused (no Gemini API cost).\n")
        response = input("Continue? (yes/no): ").strip().lower()
        if response != 'yes':
            print("Migration cancelled.")
            return
    
    # Run migration
    migrator = ChromaDBMigrator(dry_run=args.dry_run, force=args.force)
    success = migrator.run()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
