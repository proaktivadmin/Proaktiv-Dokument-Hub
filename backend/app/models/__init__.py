"""
SQLAlchemy Models for Proaktiv Dokument Hub

V3: Added Office, Employee, CompanyAsset, ExternalListing, Checklist,
    PostalCode, OfficeTerritory, LayoutPartialVersion, LayoutPartialDefault
"""

from app.models.base import Base
from app.models.template import Template, TemplateVersion, template_tags, template_categories
from app.models.tag import Tag
from app.models.category import Category
from app.models.audit_log import AuditLog
from app.models.merge_field import MergeField
from app.models.code_pattern import CodePattern
from app.models.layout_partial import LayoutPartial
from app.models.vitec_registry import VitecTemplateRegistry

# V3 Models
from app.models.office import Office
from app.models.employee import Employee
from app.models.company_asset import CompanyAsset
from app.models.external_listing import ExternalListing
from app.models.checklist import ChecklistTemplate, ChecklistInstance
from app.models.postal_code import PostalCode
from app.models.office_territory import OfficeTerritory
from app.models.layout_partial_version import LayoutPartialVersion, LayoutPartialDefault

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
]
