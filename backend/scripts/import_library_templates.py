#!/usr/bin/env python3
"""
Legacy Library Import Script

Imports templates from the legacy library folder into the new system.
- Creates categories from folder names
- Sanitizes HTML content via SanitizerService
- Uploads files to Azure Blob Storage
- Creates Template records with category associations

Usage:
    docker exec dokument-hub-backend python /app/scripts/import_library_templates.py

Options:
    --source: Source folder path (default: /app/library)
    --dry-run: Preview changes without making them
    --skip-azure: Skip Azure upload (store content in DB only)
"""

import asyncio
import argparse
import io
import os
import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, Dict, Set
import logging

# Add parent directory to path for imports
sys.path.insert(0, '/app')

from app.database import async_session_factory
from app.services.template_service import TemplateService
from app.services.category_service import CategoryService
from app.services.azure_storage_service import get_azure_storage_service
from app.services.sanitizer_service import get_sanitizer_service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Default paths
DEFAULT_SOURCE_PATH = Path("/app/library")
LEGACY_SOURCE_PATH = Path("/app/_legacy_v1/library")

# File extensions to process
SUPPORTED_EXTENSIONS = {'.html', '.htm'}

# Folders to skip (system/config folders)
SKIP_FOLDERS = {'System', 'Bundles', 'assets', '__pycache__'}

# Category icon mapping based on folder names
CATEGORY_ICONS = {
    'Akseptbrev': '📝',
    'AML': '🔒',
    'Bortefester': '🏠',
    'Bunntekst': '📄',
    'Følgebrev': '📨',
    'Forkjøpsrett': '⚖️',
    'Forretningsfører': '🏢',
    'Informasjonsbrev': 'ℹ️',
    'Innhenting av info': '📋',
    'Kjøper': '🛒',
    'Kontrakt': '📃',
    'Salgsmelding': '📢',
    'Selger': '💰',
    'SMS': '📱',
    'Topptekst': '📑',
    'Uncategorized': '📁',
}


class LibraryImporter:
    """
    Handles importing templates from the legacy library.
    """
    
    def __init__(
        self,
        source_path: Path,
        dry_run: bool = False,
        skip_azure: bool = False
    ):
        self.source_path = source_path
        self.dry_run = dry_run
        self.skip_azure = skip_azure
        
        self.storage_service = get_azure_storage_service()
        self.sanitizer = get_sanitizer_service()
        
        # Track statistics
        self.stats = {
            'categories_created': 0,
            'categories_found': 0,
            'templates_imported': 0,
            'templates_skipped': 0,
            'templates_failed': 0,
            'azure_uploads': 0,
        }
        
        # Cache for categories (name -> Category object)
        self.category_cache: Dict[str, object] = {}
        
        # Track existing templates to avoid duplicates
        self.existing_files: Set[str] = set()
    
    async def run(self):
        """Main entry point for the import process."""
        logger.info(f"Starting library import from: {self.source_path}")
        logger.info(f"Dry run: {self.dry_run}, Skip Azure: {self.skip_azure}")
        
        if not self.source_path.exists():
            logger.error(f"Source path does not exist: {self.source_path}")
            return
        
        async with async_session_factory() as session:
            # Load existing templates to avoid duplicates
            await self._load_existing_templates(session)
            
            # Walk through the source directory
            await self._process_directory(session, self.source_path)
            
            # Commit all changes
            if not self.dry_run:
                await session.commit()
        
        # Print summary
        self._print_summary()
    
    async def _load_existing_templates(self, session):
        """Load existing template filenames to avoid duplicates."""
        from sqlalchemy import text
        result = await session.execute(text("SELECT file_name FROM templates"))
        self.existing_files = {row[0] for row in result.fetchall()}
        logger.info(f"Found {len(self.existing_files)} existing templates in database")
    
    async def _process_directory(
        self,
        session,
        directory: Path,
        parent_category_name: Optional[str] = None
    ):
        """
        Recursively process a directory.
        
        Args:
            session: Database session
            directory: Directory to process
            parent_category_name: Name of parent category (folder name)
        """
        for item in sorted(directory.iterdir()):
            if item.name.startswith('.') or item.name in SKIP_FOLDERS:
                continue
            
            if item.is_dir():
                # This is a category folder
                category_name = item.name
                
                # Get or create the category
                category = await self._get_or_create_category(session, category_name)
                
                # Process files in this category folder
                await self._process_directory(session, item, category_name)
                
            elif item.is_file() and item.suffix.lower() in SUPPORTED_EXTENSIONS:
                # This is a template file
                await self._import_template(
                    session,
                    file_path=item,
                    category_name=parent_category_name
                )
    
    async def _get_or_create_category(self, session, name: str):
        """
        Get existing category or create a new one.
        
        Args:
            session: Database session
            name: Category name
            
        Returns:
            Category object
        """
        # Check cache first
        if name in self.category_cache:
            return self.category_cache[name]
        
        # Try to find existing category
        category = await CategoryService.get_by_name(session, name)
        
        if category:
            logger.info(f"Found existing category: {name}")
            self.stats['categories_found'] += 1
        else:
            # Create new category
            if self.dry_run:
                logger.info(f"[DRY RUN] Would create category: {name}")
                self.stats['categories_created'] += 1
                # Return a mock category for dry run
                return type('MockCategory', (), {'id': None, 'name': name})()
            
            icon = CATEGORY_ICONS.get(name, '📁')
            try:
                category = await CategoryService.create(
                    session,
                    name=name,
                    icon=icon,
                    description=f"Imported from legacy library: {name}"
                )
                logger.info(f"Created category: {name} ({icon})")
                self.stats['categories_created'] += 1
            except ValueError as e:
                # Category might have been created by concurrent process
                category = await CategoryService.get_by_name(session, name)
                if category:
                    self.stats['categories_found'] += 1
                else:
                    logger.error(f"Failed to create category {name}: {e}")
                    return None
        
        # Cache for future use
        self.category_cache[name] = category
        return category
    
    async def _import_template(
        self,
        session,
        file_path: Path,
        category_name: Optional[str] = None
    ):
        """
        Import a single template file.
        
        Args:
            session: Database session
            file_path: Path to the template file
            category_name: Name of the category to associate
        """
        file_name = file_path.name
        
        # Check for duplicates
        if file_name in self.existing_files:
            logger.debug(f"Skipping (exists): {file_name}")
            self.stats['templates_skipped'] += 1
            return
        
        try:
            # Read file content
            content = file_path.read_text(encoding='utf-8')
            file_size = file_path.stat().st_size
            
        except UnicodeDecodeError:
            try:
                content = file_path.read_text(encoding='latin-1')
                file_size = file_path.stat().st_size
            except Exception as e:
                logger.error(f"Failed to read {file_name}: {e}")
                self.stats['templates_failed'] += 1
                return
        except Exception as e:
            logger.error(f"Failed to read {file_name}: {e}")
            self.stats['templates_failed'] += 1
            return
        
        # Sanitize the HTML content
        sanitized_content = self.sanitizer.sanitize(content)
        
        # Generate title from filename
        title = file_path.stem  # Remove extension
        
        # Generate description
        rel_path = file_path.relative_to(self.source_path)
        description = f"Imported from library/{rel_path}"
        
        if self.dry_run:
            category_str = f" -> [{category_name}]" if category_name else ""
            logger.info(f"[DRY RUN] Would import: {file_name}{category_str}")
            self.stats['templates_imported'] += 1
            return
        
        # Upload to Azure Storage
        blob_url = None
        if not self.skip_azure and self.storage_service.is_configured:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            blob_name = f"legacy/{timestamp}_{file_name}"
            
            blob_url = await self.storage_service.upload_file(
                file_data=io.BytesIO(sanitized_content.encode('utf-8')),
                blob_name=blob_name,
                content_type='text/html'
            )
            
            if blob_url:
                self.stats['azure_uploads'] += 1
        
        # Fallback URL if Azure upload failed or skipped
        if not blob_url:
            blob_url = f"file://library/{rel_path}"
        
        # Get category ID for association
        category_ids = None
        if category_name:
            category = self.category_cache.get(category_name)
            if category and category.id:
                category_ids = [category.id]
        
        # Create the template record
        try:
            template = await TemplateService.create(
                session,
                title=title,
                description=description,
                file_name=file_name,
                file_type=file_path.suffix.lstrip('.').lower(),
                file_size_bytes=file_size,
                azure_blob_url=blob_url,
                created_by="import@system",
                status="published",
                category_ids=category_ids,
                content=sanitized_content
            )
            
            category_str = f" -> [{category_name}]" if category_name else ""
            logger.info(f"Imported: {file_name}{category_str}")
            self.stats['templates_imported'] += 1
            
            # Add to existing files set to prevent re-import in same run
            self.existing_files.add(file_name)
            
        except Exception as e:
            logger.error(f"Failed to create template {file_name}: {e}")
            self.stats['templates_failed'] += 1
    
    def _print_summary(self):
        """Print import summary statistics."""
        logger.info("=" * 50)
        logger.info("IMPORT SUMMARY")
        logger.info("=" * 50)
        logger.info(f"Categories created:   {self.stats['categories_created']}")
        logger.info(f"Categories found:     {self.stats['categories_found']}")
        logger.info(f"Templates imported:   {self.stats['templates_imported']}")
        logger.info(f"Templates skipped:    {self.stats['templates_skipped']}")
        logger.info(f"Templates failed:     {self.stats['templates_failed']}")
        logger.info(f"Azure uploads:        {self.stats['azure_uploads']}")
        logger.info("=" * 50)


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Import templates from legacy library"
    )
    parser.add_argument(
        '--source',
        type=str,
        default=str(DEFAULT_SOURCE_PATH),
        help=f"Source folder path (default: {DEFAULT_SOURCE_PATH})"
    )
    parser.add_argument(
        '--legacy',
        action='store_true',
        help=f"Use legacy source path: {LEGACY_SOURCE_PATH}"
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help="Preview changes without making them"
    )
    parser.add_argument(
        '--skip-azure',
        action='store_true',
        help="Skip Azure upload (store content in DB only)"
    )
    
    args = parser.parse_args()
    
    # Determine source path
    if args.legacy:
        source_path = LEGACY_SOURCE_PATH
    else:
        source_path = Path(args.source)
    
    # Run the import
    importer = LibraryImporter(
        source_path=source_path,
        dry_run=args.dry_run,
        skip_azure=args.skip_azure
    )
    
    await importer.run()


if __name__ == "__main__":
    asyncio.run(main())
