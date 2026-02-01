"""
SQLAlchemy Models for Proaktiv Dokument Hub

V3: Added Office, Employee, CompanyAsset, ExternalListing, Checklist,
    PostalCode, OfficeTerritory, LayoutPartialVersion, LayoutPartialDefault
"""

from app.models.audit_log import AuditLog
from app.models.base import Base
from app.models.category import Category
from app.models.checklist import ChecklistInstance, ChecklistTemplate
from app.models.code_pattern import CodePattern
from app.models.company_asset import CompanyAsset
from app.models.employee import Employee
from app.models.external_listing import ExternalListing
from app.models.firecrawl_scrape import FirecrawlScrape
from app.models.layout_partial import LayoutPartial
from app.models.layout_partial_version import LayoutPartialDefault, LayoutPartialVersion
from app.models.merge_field import MergeField
from app.models.notification import Notification

# V3 Models
from app.models.office import Office
from app.models.office_territory import OfficeTerritory
from app.models.postal_code import PostalCode
from app.models.signature_override import SignatureOverride
from app.models.sync_session import SyncSession
from app.models.tag import Tag
from app.models.template import Template, TemplateVersion, template_categories, template_tags
from app.models.vitec_registry import VitecTemplateRegistry

__all__ = [
    # Base
    "Base",
    # Templates
    "Template",
    "TemplateVersion",
    "template_tags",
    "template_categories",
    # Tags & Categories
    "Tag",
    "Category",
    # Audit
    "AuditLog",
    "Notification",
    # V2 Features
    "MergeField",
    "CodePattern",
    "LayoutPartial",
    "VitecTemplateRegistry",
    # V3 Office & Employee Hub
    "Office",
    "Employee",
    "CompanyAsset",
    "ExternalListing",
    "ChecklistTemplate",
    "ChecklistInstance",
    # V3 Territory
    "PostalCode",
    "OfficeTerritory",
    # V3 Layout Partial Versioning
    "LayoutPartialVersion",
    "LayoutPartialDefault",
    # Web scraping / crawling
    "FirecrawlScrape",
    # V3.9.4 Signature Overrides
    "SignatureOverride",
    # Sync review sessions
    "SyncSession",
]
