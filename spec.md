Proaktiv Dokument Hub - Complete Implementation Specification
Version: 2.0 (Vitec Integration Corrected)
Last Updated: December 13, 2025
Company: Destino AS
Author: Senior Azure Solutions Architect

Table of Contents

Executive Summary
Application Flow
Data Model
API Endpoints
Vitec Next Integration Strategy
File Structure
Technology Stack
Azure Infrastructure
Security & Authentication
Document Preview Strategy
Deployment Strategy
Monitoring & Logging
Phase 1 vs Phase 2 Roadmap
Testing Strategy
Success Metrics


1. Executive Summary
Project Name: Proaktiv Dokument Hub
Purpose: Centralized Master Template Library for Vitec Next document templates
1.1 Problem Statement
Vitec Next's internal file handling is cluttered and difficult to manage. The Proaktiv Dokument Hub serves as a staging and quality control area for official company templates before they are used in production.
1.2 Solution Overview
A modern web application built with Next.js (frontend) and FastAPI (backend) that provides:

Clean, searchable template repository
Reliable document preview capabilities
Version control for templates
Rich metadata and tagging system
Integration with Vitec Next for template data hydration (Phase 2)

1.3 Technical Architecture
┌─────────────────────────────────────────────────────────────┐
│                    Microsoft Entra ID                        │
│                    (Azure Easy Auth)                         │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              Azure Container Apps Environment                │
│  ┌─────────────────────┐      ┌─────────────────────┐      │
│  │   Next.js Frontend  │◄────►│  FastAPI Backend    │      │
│  │  (React + Tailwind) │      │  (Python)           │      │
│  └─────────────────────┘      └──────────┬──────────┘      │
└────────────────────────────────────────────┼────────────────┘
                                             │
                         ┌───────────────────┼───────────────────┐
                         ▼                   ▼                   ▼
              ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐
              │ Azure Blob      │  │ PostgreSQL      │  │ Redis Cache  │
              │ Storage         │  │ Flexible Server │  │ (Optional)   │
              └─────────────────┘  └─────────────────┘  └──────────────┘
                                             │
                                             ▼
                                   ┌─────────────────┐
                                   │ Azure Key Vault │
                                   │ (Vitec Creds)   │
                                   └─────────────────┘
                                             │
                                             ▼
                                   ┌─────────────────┐
                                   │  Vitec Next API │
                                   │ (hub.megler.    │
                                   │  vitec.net)     │
                                   └─────────────────┘
2. Application Flow
2.1 Admin Workflow (Phase 1)
graph TD
    A[Login via Entra ID] --> B[Dashboard]
    B --> C{Action?}
    C -->|Upload| D[Upload Template]
    C -->|Browse| E[View Templates]
    C -->|Manage| F[Tags & Categories]
    
    D --> G[Select File]
    G --> H[Add Metadata]
    H --> I[Preview Document]
    I --> J{Status?}
    J -->|Draft| K[Save as Draft]
    J -->|Published| L[Publish Template]
    
    E --> M[Filter/Search]
    M --> N[Select Template]
    N --> O{Action?}
    O -->|Edit| P[Update Metadata]
    O -->|Replace| Q[Upload New Version]
    O -->|Download| R[Get File]
    O -->|View| S[Version History]
    
    P --> L
    Q --> T[Create Version Record]
    T --> L

Step-by-Step Flow:

Authentication (Handled by Azure Easy Auth)

User navigates to app URL
Redirected to Microsoft login
Entra ID validates credentials
User redirected back with auth token
Easy Auth injects user info into headers


Dashboard

Display template statistics
Recent uploads
Quick search bar
Category navigation


Upload New Template

Click "Upload Template" button
File picker (Word/PDF/Excel)
Client-side validation (file type, size < 50MB)
Fill metadata form:

Title (required)
Description (optional)
Tags (multi-select)
Categories (multi-select)
Status (Draft/Published)


Preview generation request
POST to /api/templates
Upload to Azure Blob Storage
Create database record
Show success message


Browse & Search

Grid/List view toggle
Filter sidebar:

Status (Draft/Published/Archived)
Tags (checkboxes)
Categories (checkboxes)
Date range


Search box (title/description)
Results update in real-time
Click template card to view details


Template Detail View

Document preview (full-screen capable)
Metadata panel:

Title, description
Tags, categories
Created/updated info
Version number


Action buttons:

Edit metadata
Replace file (new version)
Download
Delete (archive)
View version history




Version Management

Upload new file → creates new version
Old version archived but accessible
Version history table:

Version number
Upload date
User who uploaded
Change notes
Download link


Restore previous version option


Tag & Category Management

Admin-only section
Create/edit/delete tags
Create/edit/delete categories
Set category icons and colors
Reorder categories (drag & drop)



2.2 Employee Workflow (Phase 2 - Future)
graph TD
    A[Login via Entra ID] --> B[Browse Templates]
    B --> C[Search/Filter]
    C --> D[View Template]
    D --> E{Action?}
    E -->|Download| F[Get Template File]
    E -->|Generate| G[Merge with Vitec Data]
    
    G --> H[Select Vitec Case]
    H --> I[Preview Merged Document]
    I --> J[Download Generated File]

3. Data Model
3.1 Database Schema (PostgreSQL)
-- Templates table
CREATE TABLE templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(200) NOT NULL,
    description TEXT,
    file_name VARCHAR(255) NOT NULL,
    file_type VARCHAR(10) NOT NULL, -- 'docx', 'pdf', 'xlsx'
    file_size_bytes BIGINT NOT NULL,
    azure_blob_url TEXT NOT NULL,
    azure_blob_container VARCHAR(100) DEFAULT 'templates',
    status VARCHAR(20) DEFAULT 'draft', -- 'draft', 'published', 'archived'
    version INTEGER DEFAULT 1,
    created_by VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by VARCHAR(255) NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    published_at TIMESTAMP,
    preview_url TEXT,
    page_count INTEGER,
    language VARCHAR(10) DEFAULT 'nb-NO',
    vitec_merge_fields TEXT[], -- Array of merge field names
    metadata JSONB -- Flexible metadata storage
);

-- Template versions table
CREATE TABLE template_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    template_id UUID NOT NULL REFERENCES templates(id) ON DELETE CASCADE,
    version_number INTEGER NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    azure_blob_url TEXT NOT NULL,
    file_size_bytes BIGINT NOT NULL,
    created_by VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    change_notes TEXT,
    UNIQUE(template_id, version_number)
);

-- Tags table
CREATE TABLE tags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(50) UNIQUE NOT NULL,
    color VARCHAR(7) DEFAULT '#3B82F6', -- Hex color
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Categories table
CREATE TABLE categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(50) UNIQUE NOT NULL,
    icon VARCHAR(50), -- Lucide icon name
    description TEXT,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Template-Tag junction table
CREATE TABLE template_tags (
    template_id UUID REFERENCES templates(id) ON DELETE CASCADE,
    tag_id UUID REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY (template_id, tag_id)
);

-- Template-Category junction table
CREATE TABLE template_categories (
    template_id UUID REFERENCES templates(id) ON DELETE CASCADE,
    category_id UUID REFERENCES categories(id) ON DELETE CASCADE,
    PRIMARY KEY (template_id, category_id)
);

-- Vitec connection settings (Phase 2)
CREATE TABLE vitec_connections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    connection_name VARCHAR(100) NOT NULL,
    installation_id VARCHAR(50) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    last_tested_at TIMESTAMP,
    last_test_status VARCHAR(20), -- 'success', 'failed'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Audit log
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_type VARCHAR(50) NOT NULL, -- 'template', 'tag', 'category'
    entity_id UUID NOT NULL,
    action VARCHAR(50) NOT NULL, -- 'created', 'updated', 'deleted', 'published', 'downloaded'
    user_email VARCHAR(255) NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    details JSONB -- Additional context
);

-- Indexes for performance
CREATE INDEX idx_templates_status ON templates(status);
CREATE INDEX idx_templates_created_at ON templates(created_at DESC);
CREATE INDEX idx_templates_title ON templates USING gin(to_tsvector('norwegian', title));
CREATE INDEX idx_audit_logs_entity ON audit_logs(entity_type, entity_id);
CREATE INDEX idx_audit_logs_timestamp ON audit_logs(timestamp DESC);

3.2 JSON Schema Examples
Template Object
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Boligkjøpskontrakt Standard",
  "description": "Standard kontrakt for boligkjøp - oppdatert 2025",
  "file_name": "boligkjopskontrakt-standard-v2.docx",
  "file_type": "docx",
  "file_size_bytes": 45678,
  "azure_blob_url": "https://stdokumenthub.blob.core.windows.net/templates/550e8400-e29b-41d4-a716-446655440000.docx",
  "azure_blob_container": "templates",
  "status": "published",
  "version": 3,
  "created_by": "troyian@proaktiv.no",
  "created_at": "2025-01-10T10:00:00Z",
  "updated_by": "troyian@proaktiv.no",
  "updated_at": "2025-01-15T14:30:00Z",
  "published_at": "2025-01-15T14:30:00Z",
  "preview_url": "https://stdokumenthub.blob.core.windows.net/previews/550e8400-preview.pdf",
  "page_count": 12,
  "language": "nb-NO",
  "vitec_merge_fields": [
    "estate.streetAddress",
    "seller.fullName",
    "estate.salesPriceEstimate"
  ],
  "tags": [
    {
      "id": "tag-001",
      "name": "Kontrakt",
      "color": "#EF4444"
    },
    {
      "id": "tag-002",
      "name": "Bolig",
      "color": "#10B981"
    }
  ],
  "categories": [
    {
      "id": "cat-001",
      "name": "Salgskontrakter",
      "icon": "FileText"
    }
  ],
  "metadata": {
    "requires_signature": true,
    "approval_required": false
  }
}

4. API Endpoints
4.1 Authentication
All endpoints require authentication via Azure Easy Auth. User info extracted from headers:

X-MS-CLIENT-PRINCIPAL-NAME (email)
X-MS-CLIENT-PRINCIPAL-ID (user ID)

4.2 Template Management
GET /api/templates
List all templates with filtering and pagination.
Query Parameters:

status (optional): draft, published, archived
tags (optional): Comma-separated tag IDs
categories (optional): Comma-separated category IDs
search (optional): Text search in title/description
page (optional): Page number (default: 1)
per_page (optional): Items per page (default: 20, max: 100)
sort_by (optional): created_at, updated_at, title (default: updated_at)
sort_order (optional): asc, desc (default: desc)

Response (200 OK):
{
  "templates": [
    {
      "id": "uuid",
      "title": "string",
      "description": "string",
      "file_type": "docx",
      "file_size_bytes": 45678,
      "status": "published",
      "version": 3,
      "tags": [...],
      "categories": [...],
      "preview_url": "string",
      "created_at": "2025-01-15T10:30:00Z",
      "updated_at": "2025-01-15T14:30:00Z"
    }
  ],
  "pagination": {
    "total": 42,
    "page": 1,
    "per_page": 20,
    "total_pages": 3
  }
}
POST /api/templates
Upload a new template.
Request (multipart/form-data):

file (required): Binary file
title (required): string
description (optional): string
tags (optional): JSON array of tag IDs
categories (optional): JSON array of category IDs
status (optional): draft or published (default: draft)

Response (201 Created):
{
  "id": "uuid",
  "title": "string",
  "file_name": "string",
  "azure_blob_url": "string",
  "preview_url": "string",
  "status": "draft",
  "version": 1,
  "created_at": "2025-01-15T10:30:00Z"
}

Error Responses:

400 Bad Request: Invalid file type or size
413 Payload Too Large: File exceeds 50MB
500 Internal Server Error: Upload failed

GET /api/templates/{template_id}
Get single template details including full metadata.
Response (200 OK):
Response (200 OK):
json{
  "id": "uuid",
  "title": "string",
  "description": "string",
  "file_name": "string",
  "file_type": "docx",
  "file_size_bytes": 45678,
  "azure_blob_url": "string",
  "status": "published",
  "version": 3,
  "tags": [...],
  "categories": [...],
  "preview_url": "string",
  "page_count": 12,
  "vitec_merge_fields": [...],
  "created_by": "troyian@proaktiv.no",
  "created_at": "2025-01-10T10:00:00Z",
  "updated_by": "troyian@proaktiv.no",
  "updated_at": "2025-01-15T14:30:00Z",
  "published_at": "2025-01-15T14:30:00Z"
}
PUT /api/templates/{template_id}
Update template metadata (not the file itself).
Request Body:
json{
  "title": "string",
  "description": "string",
  "tags": ["uuid1", "uuid2"],
  "categories": ["uuid1"],
  "status": "published",
  "vitec_merge_fields": ["estate.streetAddress"]
}
Response (200 OK):
json{
  "id": "uuid",
  "title": "Updated Title",
  "updated_at": "2025-01-15T15:00:00Z"
}
POST /api/templates/{template_id}/versions
Upload a new version of a template (replaces file).
Request (multipart/form-data):

file (required): Binary file
change_notes (optional): Description of changes

Response (201 Created):
json{
  "template_id": "uuid",
  "version_number": 4,
  "file_name": "string",
  "azure_blob_url": "string",
  "created_at": "2025-01-15T15:30:00Z"
}
GET /api/templates/{template_id}/versions
Get version history for a template.
Response (200 OK):
json{
  "template_id": "uuid",
  "current_version": 4,
  "versions": [
    {
      "version_number": 4,
      "file_name": "template-v4.docx",
      "file_size_bytes": 48000,
      "created_by": "troyian@proaktiv.no",
      "created_at": "2025-01-15T15:30:00Z",
      "change_notes": "Updated formatting"
    },
    {
      "version_number": 3,
      "file_name": "template-v3.docx",
      "file_size_bytes": 45678,
      "created_by": "troyian@proaktiv.no",
      "created_at": "2025-01-10T10:00:00Z",
      "change_notes": "Fixed typos"
    }
  ]
}
POST /api/templates/{template_id}/restore-version/{version_number}
Restore a previous version as the current version.
Response (200 OK):
json{
  "template_id": "uuid",
  "restored_version": 3,
  "new_current_version": 5,
  "message": "Version 3 restored as version 5"
}
DELETE /api/templates/{template_id}
Soft delete (archive) a template.
Response (204 No Content)
GET /api/templates/{template_id}/download
Download the template file.
Response: Redirect (302) to Azure Blob Storage SAS URL with 1-hour expiration
Alternative: Stream file directly
pythonreturn StreamingResponse(
    file_stream,
    media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    headers={"Content-Disposition": f"attachment; filename={file_name}"}
)
GET /api/templates/{template_id}/preview
Get preview URL for in-browser viewing.
Response (200 OK):
json{
  "preview_url": "https://stdokumenthub.blob.core.windows.net/previews/uuid-preview.pdf",
  "expires_at": "2025-01-15T16:30:00Z"
}
4.3 Tags & Categories
GET /api/tags
List all tags.
Response (200 OK):
json{
  "tags": [
    {
      "id": "uuid",
      "name": "Kontrakt",
      "color": "#EF4444",
      "created_at": "2025-01-01T00:00:00Z"
    }
  ]
}
POST /api/tags
Create a new tag.
Request Body:
json{
  "name": "GDPR",
  "color": "#8B5CF6"
}
Response (201 Created):
json{
  "id": "uuid",
  "name": "GDPR",
  "color": "#8B5CF6",
  "created_at": "2025-01-15T10:00:00Z"
}
PUT /api/tags/{tag_id}
Update a tag.
Request Body:
json{
  "name": "GDPR Dokumenter",
  "color": "#8B5CF6"
}
Response (200 OK)
DELETE /api/tags/{tag_id}
Delete a tag (removes from all templates).
Response (204 No Content)
GET /api/categories
List all categories (sorted by sort_order).
Response (200 OK):
json{
  "categories": [
    {
      "id": "uuid",
      "name": "Salgskontrakter",
      "icon": "FileText",
      "description": "Kontrakter for salg av eiendom",
      "sort_order": 1,
      "created_at": "2025-01-01T00:00:00Z"
    }
  ]
}
POST /api/categories
Create a new category.
Request Body:
json{
  "name": "Marketing",
  "icon": "Megaphone",
  "description": "Marketing materials and flyers",
  "sort_order": 5
}
Response (201 Created)
PUT /api/categories/{category_id}
Update a category.
Response (200 OK)
DELETE /api/categories/{category_id}
Delete a category.
Response (204 No Content)
4.4 Analytics & Audit
GET /api/analytics/dashboard
Get dashboard statistics.
Response (200 OK):
json{
  "total_templates": 42,
  "published_templates": 35,
  "draft_templates": 7,
  "archived_templates": 0,
  "total_downloads_30d": 127,
  "most_downloaded": [
    {
      "template_id": "uuid",
      "title": "Boligkjøpskontrakt",
      "download_count": 45
    }
  ],
  "recent_uploads": [
    {
      "template_id": "uuid",
      "title": "New Contract",
      "created_at": "2025-01-15T10:00:00Z"
    }
  ]
}
GET /api/audit-logs
View audit trail.
Query Parameters:

entity_type (optional): template, tag, category
entity_id (optional): UUID
user_email (optional): Filter by user
action (optional): created, updated, deleted, published, downloaded
from_date (optional): ISO 8601 datetime
to_date (optional): ISO 8601 datetime
page (optional): Page number
per_page (optional): Items per page

Response (200 OK):
json{
  "logs": [
    {
      "id": "uuid",
      "entity_type": "template",
      "entity_id": "uuid",
      "action": "published",
      "user_email": "troyian@proaktiv.no",
      "timestamp": "2025-01-15T14:30:00Z",
      "details": {
        "previous_status": "draft",
        "new_status": "published"
      }
    }
  ],
  "pagination": {
    "total": 500,
    "page": 1,
    "per_page": 50
  }
}
4.5 Health & Status
GET /api/health
Health check endpoint.
Response (200 OK):
json{
  "status": "healthy",
  "timestamp": "2025-01-15T10:00:00Z",
  "services": {
    "database": "connected",
    "storage": "available",
    "vitec_api": "reachable",
    "redis": "connected"
  },
  "version": "1.0.0"
}
```

---

## 5. Vitec Next Integration Strategy

### 5.1 Your Actual Configuration

**Partner Details:**
- **Partner Login Name:** `destino`
- **Access Keys:** 2 access keys available (use Access Key 1)
- **Product:** "Destino AS - Product 1" (Version 1.5)
- **Installation ID (Test):** `MSPROATEST`
- **API Environments:**
  - QA/Test: `https://hub.qa.vitecnext.no/`
  - Production: `https://hub.megler.vitec.net/`

### 5.2 Authentication Flow

**Method:** Bearer Token Authentication
- **Header:** `Authorization: Bearer {access_key}`
- **Access Key Storage:** Azure Key Vault
- **Key Rotation:** Use Access Key 2 as backup, regenerate keys periodically
```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│  Next.js    │         │   FastAPI    │         │ Vitec Hub   │
│  Frontend   │         │   Backend    │         │     API     │
└──────┬──────┘         └──────┬───────┘         └──────┬──────┘
       │                       │                        │
       │ 1. Request Vitec data │                        │
       ├──────────────────────>│                        │
       │                       │                        │
       │                       │ 2. Get credentials     │
       │                       │    from Key Vault      │
       │                       │                        │
       │                       │ 3. Make authenticated  │
       │                       │    request             │
       │                       ├───────────────────────>│
       │                       │ Bearer: {access_key}   │
       │                       │                        │
       │                       │ 4. Return data         │
       │                       │<───────────────────────┤
       │                       │                        │
       │ 5. Forward to         │                        │
       │    frontend           │                        │
       │<──────────────────────┤                        │
5.3 Vitec API Client Implementation
python# backend/app/services/vitec_client.py
import httpx
from typing import Dict, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class VitecHubClient:
    """
    Client for Vitec Megler Hub API.
    
    Documentation: https://hub.megler.vitec.net/
    """
    
    def __init__(
        self,
        installation_id: str,
        access_key: str,
        environment: str = "production"
    ):
        """
        Initialize Vitec Hub client.
        
        Args:
            installation_id: Customer's installation ID (e.g., "MSPROATEST")
            access_key: Partner access key from Partner Portal
            environment: "production" or "qa"
        """
        self.installation_id = installation_id
        
        if environment == "production":
            self.base_url = "https://hub.megler.vitec.net"
        elif environment == "qa":
            self.base_url = "https://hub.qa.vitecnext.no"
        else:
            raise ValueError(f"Invalid environment: {environment}")
        
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {access_key}",
                "Accept": "application/json",
                "Content-Type": "application/json",
                "User-Agent": "ProaktivDokumentHub/1.0"
            },
            timeout=30.0
        )
        
        logger.info(
            f"Initialized Vitec client for installation {installation_id} "
            f"in {environment} environment"
        )
    
    async def test_connection(self) -> Dict:
        """
        Test API connectivity by fetching available methods.
        
        Endpoint: GET /Account/Methods
        
        Returns:
            Dict with status and available methods
        """
        try:
            response = await self.client.get("/Account/Methods")
            response.raise_for_status()
            
            return {
                "status": "success",
                "timestamp": datetime.utcnow().isoformat(),
                "methods": response.json()
            }
        except httpx.HTTPError as e:
            logger.error(f"Vitec connection test failed: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    # --- Departments ---
    
    async def get_departments(self) -> List[Dict]:
        """
        Fetch all departments/offices.
        
        Endpoint: GET /{installationId}/Departments
        
        Returns:
            List of department objects with name, address, contact info
        """
        response = await self.client.get(
            f"/{self.installation_id}/Departments"
        )
        response.raise_for_status()
        return response.json()
    
    # --- Estates (Properties/Cases) ---
    
    async def get_estates(
        self,
        department_id: Optional[int] = None,
        changed_after: Optional[str] = None,
        employee_email: Optional[str] = None
    ) -> List[Dict]:
        """
        Fetch estates (properties/cases).
        
        Endpoint: GET /{installationId}/Estates
        
        Args:
            department_id: Filter by department
            changed_after: ISO 8601 datetime (e.g., "2025-01-01T00:00:00Z")
            employee_email: Filter by employee
        
        Note: API returns max 10,000 estates per query.
              Use filters to stay within limit.
        
        Returns:
            List of estate objects
        """
        params = {}
        if department_id:
            params["departmentId"] = department_id
        if changed_after:
            params["changedAfter"] = changed_after
        if employee_email:
            params["employeeEmail"] = employee_email
        
        response = await self.client.get(
            f"/{self.installation_id}/Estates",
            params=params
        )
        response.raise_for_status()
        return response.json()
    
    async def get_estate_by_id(self, estate_id: str) -> Dict:
        """
        Fetch detailed information for a specific estate.
        
        Endpoint: GET /{installationId}/EstateId
        
        Args:
            estate_id: Estate GUID (visible in Vitec Next UI)
        
        Returns:
            Complete estate object with all fields
        """
        response = await self.client.get(
            f"/{self.installation_id}/EstateId",
            params={"estateId": estate_id}
        )
        response.raise_for_status()
        return response.json()
    
    async def get_estate_assignment_budget(self, estate_id: str) -> Dict:
        """
        Get assignment budget for an estate.
        
        Endpoint: GET /{installationId}/Estates/{estateId}/AssignmentBudget
        """
        response = await self.client.get(
            f"/{self.installation_id}/Estates/{estate_id}/AssignmentBudget"
        )
        response.raise_for_status()
        return response.json()
    
    # --- Contacts ---
    
    async def get_estate_contacts(self, estate_id: str) -> List[Dict]:
        """
        Fetch contacts for a specific estate.
        
        Endpoint: GET /{installationId}/Estates/{estateId}/Contacts
        
        Returns sellers, buyers, and other related contacts.
        
        Args:
            estate_id: Estate GUID
        
        Returns:
            List of contact objects with relation info
        """
        response = await self.client.get(
            f"/{self.installation_id}/Estates/{estate_id}/Contacts"
        )
        response.raise_for_status()
        return response.json()
    
    async def get_estate_contact_information(self, estate_id: str) -> Dict:
        """
        Fetch contact information for an estate.
        
        Endpoint: GET /{installationId}/Estates/{estateId}/ContactInformation
        
        Args:
            estate_id: Estate GUID
        
        Returns:
            Contact information object
        """
        response = await self.client.get(
            f"/{self.installation_id}/Estates/{estate_id}/ContactInformation"
        )
        response.raise_for_status()
        return response.json()
    
    async def get_contact(self, contact_id: str) -> Dict:
        """
        Fetch a specific contact by ID.
        
        Endpoint: GET /{installationId}/Contacts/{contactId}
        
        Args:
            contact_id: Contact GUID or ID
        
        Returns:
            Contact object with full details
        """
        response = await self.client.get(
            f"/{self.installation_id}/Contacts/{contact_id}"
        )
        response.raise_for_status()
        return response.json()
    
    async def find_contacts(self, search_term: str) -> List[Dict]:
        """
        Search for contacts by name, email, etc.
        
        Endpoint: GET /{installationId}/Contacts/Find
        
        Args:
            search_term: Search query
        
        Returns:
            List of matching contacts
        """
        response = await self.client.get(
            f"/{self.installation_id}/Contacts/Find",
            params={"searchTerm": search_term}
        )
        response.raise_for_status()
        return response.json()
    
    # --- Metadata Types ---
    
    async def get_metadata_types(self) -> Dict:
        """
        Get various metadata types used in Next.
        
        Available endpoints:
        - GET /{installationId}/Next/AreaTypes
        - GET /{installationId}/Next/ContactRoleTypes
        - GET /{installationId}/Next/AssignmentTypes
        - GET /{installationId}/Next/EstateTypes
        - GET /{installationId}/Next/OriginTypes
        - GET /{installationId}/Next/ConsentTypes
        
        Returns:
            Dict with all metadata types
        """
        types = {}
        
        endpoints = [
            "AreaTypes",
            "ContactRoleTypes",
            "AssignmentTypes",
            "EstateTypes",
            "OriginTypes",
            "ConsentTypes"
        ]
        
        for endpoint in endpoints:
            try:
                response = await self.client.get(
                    f"/{self.installation_id}/Next/{endpoint}"
                )
                response.raise_for_status()
                types[endpoint] = response.json()
            except httpx.HTTPError as e:
                logger.warning(f"Failed to fetch {endpoint}: {e}")
                types[endpoint] = None
        
        return types
    
    async def get_next_path(self) -> str:
        """
        Get the Next UI path/URL.
        
        Endpoint: GET /{installationId}/Next/GetPath
        
        Returns:
            URL to Vitec Next UI
        """
        response = await self.client.get(
            f"/{self.installation_id}/Next/GetPath"
        )
        response.raise_for_status()
        return response.json()
    
    # --- Documents ---
    
    async def get_estate_documents(
        self,
        estate_id: str,
        document_id: Optional[str] = None
    ) -> Dict:
        """
        Fetch documents related to an estate.
        
        Endpoint: GET /{installationId}/Estates/{estateId}/Documents/{documentId}
        
        Note: Requires document ID. Use get_estate_by_id() to get document IDs first.
        
        Args:
            estate_id: Estate GUID
            document_id: Specific document ID (if known)
        
        Returns:
            Document metadata or list of documents
        """
        if document_id:
            response = await self.client.get(
                f"/{self.installation_id}/Estates/{estate_id}/Documents/{document_id}"
            )
        else:
            # Might need to fetch estate first to get document IDs
            raise NotImplementedError(
                "Listing all documents requires fetching estate details first"
            )
        
        response.raise_for_status()
        return response.json()
    
    async def close(self):
        """Clean up HTTP client"""
        await self.client.aclose()
        logger.info("Vitec client closed")

5.4 FastAPI Integration Endpoints
python# backend/app/routers/vitec.py
from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
import logging

from app.services.vitec_client import VitecHubClient
from app.config import get_vitec_credentials
from app.middleware.vitec_rate_limit import rate_limit_vitec

router = APIRouter(prefix="/api/vitec", tags=["Vitec Integration"])
logger = logging.getLogger(__name__)

def get_vitec_client() -> VitecHubClient:
    """Dependency to create Vitec client with credentials from Key Vault"""
    creds = get_vitec_credentials()
    return VitecHubClient(
        installation_id=creds["installation_id"],
        access_key=creds["access_key"],
        environment=creds["environment"]
    )

@router.get("/test-connection")
@rate_limit_vitec(max_calls=5, period=60)
async def test_vitec_connection():
    """
    Test connectivity to Vitec Hub API.
    
    Returns available API methods and access rights.
    """
    client = get_vitec_client()
    
    try:
        result = await client.test_connection()
        return result
    finally:
        await client.close()

@router.get("/departments")
@rate_limit_vitec(max_calls=10, period=60)
async def get_departments():
    """
    Fetch all departments/offices from Vitec.
    
    Cached for 15 minutes to reduce API calls.
    """
    client = get_vitec_client()
    
    try:
        departments = await client.get_departments()
        return {
            "departments": departments,
            "count": len(departments)
        }
    except Exception as e:
        logger.error(f"Failed to fetch departments: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch departments")
    finally:
        await client.close()

@router.get("/estates")
@rate_limit_vitec(max_calls=20, period=60)
async def get_estates(
    department_id: Optional[int] = None,
    changed_after: Optional[str] = None,
    employee_email: Optional[str] = None
):
    """
    Fetch estates (properties/cases) with optional filters.
    
    Query params:
    - department_id: Filter by department
    - changed_after: ISO 8601 datetime (e.g., "2025-01-01T00:00:00Z")
    - employee_email: Filter by employee email
    
    Note: Returns max 10,000 estates. Use filters to stay within limit.
    """
    client = get_vitec_client()
    
    try:
        estates = await client.get_estates(
            department_id=department_id,
            changed_after=changed_after,
            employee_email=employee_email
        )
        return {
            "estates": estates,
            "count": len(estates)
        }
    except Exception as e:
        logger.error(f"Failed to fetch estates: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch estates")
    finally:
        await client.close()

@router.get("/estates/{estate_id}")
@rate_limit_vitec(max_calls=30, period=60)
async def get_estate(estate_id: str):
    """
    Get detailed estate information by ID.
    
    Args:
        estate_id: Estate GUID from Vitec Next
    """
    client = get_vitec_client()
    
    try:
        estate = await client.get_estate_by_id(estate_id)
        return estate
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise HTTPException(status_code=404, detail="Estate not found")
        raise HTTPException(status_code=500, detail="Failed to fetch estate")
    finally:
        await client.close()

@router.get("/estates/{estate_id}/contacts")
@rate_limit_vitec(max_calls=30, period=60)
async def get_estate_contacts(estate_id: str):
    """
    Get all contacts for an estate (sellers, buyers, etc.).
    
    Args:
        estate_id: Estate GUID
    """
    client = get_vitec_client()
    
    try:
        contacts = await client.get_estate_contacts(estate_id)
        return {
            "estate_id": estate_id,
            "contacts": contacts
        }
    except Exception as e:
        logger.error(f"Failed to fetch estate contacts: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch contacts")
    finally:
        await client.close()

@router.get("/merge-fields")
async def get_available_merge_fields():
    """
    Return available merge fields for template hydration.
    
    This is a static mapping based on Vitec's data structure.
    Used to populate merge field selector in UI.
    """
    return {
        "estate_fields": {
            "assignmentNum": "Assignment Number",
            "streetAddress": "Street Address",
            "city": "City",
            "zipCode": "Postal Code",
            "primaryArea": "Primary Area (sqm)",
            "salesPriceEstimate": "Estimated Sales Price",
            "status": "Status",
            "propertyType": "Property Type"
        },
        "contact_fields": {
            "firstName": "First Name",
            "lastName": "Last Name",
            "fullName": "Full Name",
            "email": "Email",
            "mobilePhone": "Mobile Phone",
            "postalAddress": "Postal Address",
            "postalCode": "Postal Code",
            "postalArea": "Postal Area"
        },
        "department_fields": {
            "name": "Department Name",
            "legalName": "Legal Name",
            "phone": "Phone",
            "email": "Email",
            "streetAddress": "Street Address",
            "city": "City",
            "postalCode": "Postal Code"
        }
    }
5.5 Environment Variables & Key Vault
python# backend/app/config.py
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from pydantic_settings import BaseSettings
from functools import lru_cache
import logging

logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    # Key Vault
    KEY_VAULT_URL: str = "https://kv-dokument-hub.vault.azure.net/"
    
    # Database
    DATABASE_URL: str
    
    # Azure Storage
    AZURE_STORAGE_CONNECTION_STRING: str
    AZURE_STORAGE_CONTAINER_NAME: str = "templates"
    
    # Redis (optional)
    REDIS_URL: str = ""
    
    # Application
    APP_NAME: str = "Proaktiv Dokument Hub"
    APP_VERSION: str = "1.0.0"
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    return Settings()

def get_vitec_credentials() -> dict:
    """
    Retrieve Vitec credentials from Azure Key Vault.
    Uses Managed Identity for authentication.
    
    Returns:
        Dict with installation_id, access_key, environment
    """
    settings = get_settings()
    
    try:
        credential = DefaultAzureCredential()
        secret_client = SecretClient(
            vault_url=settings.KEY_VAULT_URL,
            credential=credential
        )
        
        return {
            "installation_id": secret_client.get_secret("vitec-installation-id").value,
            "access_key": secret_client.get_secret("vitec-access-key").value,
            "environment": secret_client.get_secret("vitec-environment").value,
        }
    except Exception as e:
        logger.error(f"Failed to retrieve Vitec credentials from Key Vault: {e}")
        raise RuntimeError("Vitec credentials not available")

settings = get_settings()
5.6 Rate Limiting & Caching
python# backend/app/middleware/vitec_rate_limit.py
from functools import wraps
from fastapi import HTTPException
import redis
import logging
from app.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

# Initialize Redis client (optional)
if settings.REDIS_URL:
    redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)
else:
    redis_client = None
    logger.warning("Redis not configured - rate limiting disabled")

def rate_limit_vitec(max_calls: int = 10, period: int = 60):
    """
    Rate limit Vitec API calls: max_calls per period (seconds).
    
    Args:
        max_calls: Maximum number of calls allowed
        period: Time period in seconds
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if not redis_client:
                # Skip rate limiting if Redis not available
                return await func(*args, **kwargs)
            
            key = f"vitec_rate_limit:{func.__name__}"
            current_calls = redis_client.get(key)
            
            if current_calls and int(current_calls) >= max_calls:
                raise HTTPException(
                    status_code=429,
                    detail=f"Vitec API rate limit exceeded. Max {max_calls} calls per {period} seconds."
                )
            
            # Increment counter
            pipe = redis_client.pipeline()
            pipe.incr(key)
            pipe.expire(key, period)
            pipe.execute()
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator
5.7 Template Merge Service (Phase 2)
python# backend/app/services/document_merge.py
from docx import Document
from io import BytesIO
from typing import Dict
import logging

from app.services.vitec_client import VitecHubClient

logger = logging.getLogger(__name__)

async def merge_vitec_data_into_template(
    template_bytes: bytes,
    estate_id: str,
    vitec_client: VitecHubClient
) -> bytes:
    """
    Merge Vitec data into a Word template.
    
    Merge field format in template: {{estate.streetAddress}}
    
    Args:
        template_bytes: Template file content
        estate_id: Vitec estate ID
        vitec_client: Initialized Vitec client
    
    Returns:
        Merged document as bytes
    """
    # Fetch data from Vitec
    estate = await vitec_client.get_estate_by_id(estate_id)
    contacts = await vitec_client.get_estate_contacts(estate_id)
    departments = await vitec_client.get_departments()
    
    # Extract seller (first contact with seller role)
    seller = {}
    for contact_group in contacts:
        if contact_group.get("type") == 0:  # Seller type
            if contact_group.get("contacts") and len(contact_group["contacts"]) > 0:
                seller = contact_group["contacts"][0]
                break
    
    # Prepare merge data
    merge_data = {
        "estate": estate,
        "seller": seller,
        "department": departments[0] if departments else {}
    }
    
    # Load template
    doc = Document(BytesIO(template_bytes))
    
    # Flatten merge data for easy replacement
    flat_data = flatten_dict(merge_data)
    
    # Replace merge fields in all paragraphs
    for paragraph in doc.paragraphs:
        for key, value in flat_data.items():
            placeholder = f"{{{{{key}}}}}"
            if placeholder in paragraph.text:
                paragraph.text = paragraph.text.replace(placeholder, str(value))
    
    # Replace in tables
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for key, value in flat_data.items():
                    placeholder = f"{{{{{key}}}}}"
                    if


placeholder in cell.text:
cell.text = cell.text.replace(placeholder, str(value))
# Save to BytesIO
output = BytesIO()
doc.save(output)
output.seek(0)

logger.info(f"Successfully merged Vitec data for estate {estate_id}")
return output.read()
def flatten_dict(d: dict, parent_key: str = "", sep: str = ".") -> dict:
"""
Flatten nested dict for merge fields.
Example:
    {"estate": {"city": "Sandnes"}} -> {"estate.city": "Sandnes"}
"""
items = []
for k, v in d.items():
    new_key = f"{parent_key}{sep}{k}" if parent_key else k
    if isinstance(v, dict):
        items.extend(flatten_dict(v, new_key, sep=sep).items())
    elif v is not None:
        items.append((new_key, v))
return dict(items)

### 5.8 Phase 2: Generate Merged Document Endpoint
```python
# backend/app/routers/vitec.py (continued)

@router.post("/templates/{template_id}/generate")
@rate_limit_vitec(max_calls=10, period=60)
async def generate_merged_document(
    template_id: str,
    estate_id: str
):
    """
    Merge template with Vitec data and generate document.
    
    Args:
        template_id: Template UUID
        estate_id: Vitec estate GUID
    
    Returns:
        Download URL for generated document
    """
    from app.services.document_merge import merge_vitec_data_into_template
    from app.services.azure_storage import download_blob, upload_blob
    
    client = get_vitec_client()
    
    try:
        # 1. Download template from Azure Blob Storage
        template_bytes = await download_blob(template_id)
        
        # 2. Merge with Vitec data
        merged_bytes = await merge_vitec_data_into_template(
            template_bytes=template_bytes,
            estate_id=estate_id,
            vitec_client=client
        )
        
        # 3. Upload generated document
        generated_filename = f"{template_id}_generated_{estate_id}.docx"
        blob_url = await upload_blob(
            container="generated-documents",
            filename=generated_filename,
            data=merged_bytes
        )
        
        return {
            "status": "success",
            "download_url": blob_url,
            "filename": generated_filename
        }
        
    except Exception as e:
        logger.error(f"Failed to generate merged document: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate document")
    finally:
        await client.close()
```

---

## 6. File Structure
proaktiv-dokument-hub/
│
├── backend/                              # FastAPI Backend
│   ├── app/
│   │   ├── init.py
│   │   ├── main.py                       # FastAPI app entry point
│   │   ├── config.py                     # Configuration & Key Vault
│   │   ├── database.py                   # SQLAlchemy setup
│   │   │
│   │   ├── models/                       # SQLAlchemy models
│   │   │   ├── init.py
│   │   │   ├── template.py               # Template model
│   │   │   ├── template_version.py       # Version history
│   │   │   ├── tag.py                    # Tags
│   │   │   ├── category.py               # Categories
│   │   │   ├── audit_log.py              # Audit trail
│   │   │   └── vitec_connection.py       # Vitec settings (Phase 2)
│   │   │
│   │   ├── schemas/                      # Pydantic schemas
│   │   │   ├── init.py
│   │   │   ├── template.py               # Template request/response
│   │   │   ├── tag.py
│   │   │   ├── category.py
│   │   │   ├── vitec.py                  # Vitec data schemas
│   │   │   └── audit.py
│   │   │
│   │   ├── routers/                      # API route handlers
│   │   │   ├── init.py
│   │   │   ├── templates.py              # Template CRUD
│   │   │   ├── tags.py                   # Tag management
│   │   │   ├── categories.py             # Category management
│   │   │   ├── vitec.py                  # Vitec integration
│   │   │   ├── analytics.py              # Dashboard stats
│   │   │   └── health.py                 # Health check
│   │   │
│   │   ├── services/                     # Business logic
│   │   │   ├── init.py
│   │   │   ├── azure_storage.py          # Blob Storage operations
│   │   │   ├── vitec_client.py           # Vitec API client
│   │   │   ├── document_preview.py       # Preview generation
│   │   │   ├── document_merge.py         # Template merging
│   │   │   └── audit_service.py          # Audit logging
│   │   │
│   │   ├── middleware/                   # Custom middleware
│   │   │   ├── init.py
│   │   │   ├── auth.py                   # Extract Entra ID user
│   │   │   ├── logging.py                # Request/response logging
│   │   │   └── vitec_rate_limit.py       # API rate limiting
│   │   │
│   │   └── utils/                        # Utility functions
│   │       ├── init.py
│   │       ├── validators.py             # Input validation
│   │       └── exceptions.py             # Custom exceptions
│   │
│   ├── alembic/                          # Database migrations
│   │   ├── versions/
│   │   │   ├── 001_initial_schema.py
│   │   │   ├── 002_add_vitec_fields.py
│   │   │   └── ...
│   │   ├── env.py
│   │   └── alembic.ini
│   │
│   ├── tests/                            # Backend tests
│   │   ├── init.py
│   │   ├── conftest.py                   # Pytest fixtures
│   │   ├── test_templates.py
│   │   ├── test_vitec_integration.py
│   │   ├── test_auth.py
│   │   └── test_document_merge.py
│   │
│   ├── requirements.txt                  # Python dependencies
│   ├── requirements-dev.txt              # Dev dependencies
│   ├── Dockerfile                        # Container image
│   ├── .env.example                      # Example environment vars
│   └── README.md
│
├── frontend/                             # Next.js Frontend
│   ├── src/
│   │   ├── app/                          # Next.js 14 App Router
│   │   │   ├── layout.tsx                # Root layout
│   │   │   ├── page.tsx                  # Dashboard
│   │   │   ├── globals.css               # Global styles
│   │   │   │
│   │   │   ├── templates/
│   │   │   │   ├── page.tsx              # Template list
│   │   │   │   ├── [id]/
│   │   │   │   │   ├── page.tsx          # Template detail
│   │   │   │   │   └── edit/
│   │   │   │   │       └── page.tsx      # Edit metadata
│   │   │   │   └── new/
│   │   │   │       └── page.tsx          # Upload new template
│   │   │   │
│   │   │   ├── admin/
│   │   │   │   ├── layout.tsx            # Admin layout
│   │   │   │   ├── page.tsx              # Admin dashboard
│   │   │   │   ├── tags/
│   │   │   │   │   └── page.tsx          # Tag management
│   │   │   │   ├── categories/
│   │   │   │   │   └── page.tsx          # Category management
│   │   │   │   └── vitec/
│   │   │   │       └── page.tsx          # Vitec integration settings
│   │   │   │
│   │   │   └── api/                      # Next.js API routes (optional)
│   │   │       └── health/
│   │   │           └── route.ts
│   │   │
│   │   ├── components/                   # React components
│   │   │   ├── ui/                       # Shadcn UI components
│   │   │   │   ├── button.tsx
│   │   │   │   ├── card.tsx
│   │   │   │   ├── dialog.tsx
│   │   │   │   ├── dropdown-menu.tsx
│   │   │   │   ├── input.tsx
│   │   │   │   ├── select.tsx
│   │   │   │   ├── table.tsx
│   │   │   │   ├── tabs.tsx
│   │   │   │   ├── badge.tsx
│   │   │   │   ├── toast.tsx
│   │   │   │   ├── skeleton.tsx
│   │   │   │   └── ...
│   │   │   │
│   │   │   ├── layout/
│   │   │   │   ├── Header.tsx            # Top navigation
│   │   │   │   ├── Sidebar.tsx           # Side navigation
│   │   │   │   ├── Footer.tsx            # Footer
│   │   │   │   └── Breadcrumbs.tsx       # Breadcrumb trail
│   │   │   │
│   │   │   ├── templates/
│   │   │   │   ├── TemplateCard.tsx      # Grid item
│   │   │   │   ├── TemplateGrid.tsx      # Grid layout
│   │   │   │   ├── TemplateList.tsx      # List layout
│   │   │   │   ├── TemplateUpload.tsx    # Upload form
│   │   │   │   ├── TemplatePreview.tsx   # Document viewer
│   │   │   │   ├── TemplateFilters.tsx   # Filter sidebar
│   │   │   │   ├── TemplateSearch.tsx    # Search bar
│   │   │   │   ├── VersionHistory.tsx    # Version timeline
│   │   │   │   └── StatusBadge.tsx       # Status indicator
│   │   │   │
│   │   │   ├── tags/
│   │   │   │   ├── TagManager.tsx        # Tag CRUD
│   │   │   │   ├── TagSelector.tsx       # Multi-select tags
│   │   │   │   └── TagBadge.tsx          # Single tag display
│   │   │   │
│   │   │   ├── categories/
│   │   │   │   ├── CategoryManager.tsx
│   │   │   │   ├── CategorySelector.tsx
│   │   │   │   └── CategoryCard.tsx
│   │   │   │
│   │   │   └── vitec/
│   │   │       ├── VitecConnectionTest.tsx   # Test API
│   │   │       ├── MergeFieldSelector.tsx    # Field picker
│   │   │       ├── EstateSelector.tsx        # Select estate
│   │   │       └── GenerateDocumentDialog.tsx # Merge UI
│   │   │
│   │   ├── lib/                          # Utilities
│   │   │   ├── api.ts                    # API client wrapper
│   │   │   ├── utils.ts                  # General utilities
│   │   │   └── constants.ts              # App constants
│   │   │
│   │   ├── hooks/                        # Custom React hooks
│   │   │   ├── useTemplates.ts           # Template CRUD hooks
│   │   │   ├── useTags.ts                # Tag management
│   │   │   ├── useCategories.ts          # Category management
│   │   │   ├── useVitec.ts               # Vitec API hooks
│   │   │   └── useAuth.ts                # Auth context
│   │   │
│   │   ├── types/                        # TypeScript types
│   │   │   ├── template.ts
│   │   │   ├── tag.ts
│   │   │   ├── category.ts
│   │   │   ├── vitec.ts
│   │   │   └── api.ts
│   │   │
│   │   └── styles/
│   │       └── globals.css               # Tailwind imports
│   │
│   ├── public/
│   │   ├── favicon.ico
│   │   ├── icons/
│   │   └── images/
│   │       └── logo.svg
│   │
│   ├── next.config.js                    # Next.js config
│   ├── tailwind.config.ts                # Tailwind config
│   ├── tsconfig.json                     # TypeScript config
│   ├── package.json                      # Node dependencies
│   ├── package-lock.json
│   ├── components.json                   # Shadcn config
│   ├── Dockerfile                        # Container image
│   ├── .env.local.example                # Example env vars
│   └── README.md
│
├── infrastructure/                       # Infrastructure as Code
│   ├── bicep/                            # Azure Bicep templates
│   │   ├── main.bicep                    # Main deployment
│   │   ├── parameters.json               # Parameters
│   │   ├── modules/
│   │   │   ├── container-apps.bicep      # Container Apps
│   │   │   ├── database.bicep            # PostgreSQL
│   │   │   ├── storage.bicep             # Blob Storage
│   │   │   ├── key-vault.bicep           # Key Vault
│   │   │   ├── redis.bicep               # Redis Cache
│   │   │   └── monitoring.bicep          # App Insights
│   │   └── README.md
│   │
│   └── scripts/
│       ├── deploy.sh                     # Deployment script
│       └── setup-keyvault.sh             # Key Vault setup
│
├── .github/                              # GitHub Actions CI/CD
│   └── workflows/
│       ├── backend-ci.yml                # Backend CI
│       ├── frontend-ci.yml               # Frontend CI
│       ├── deploy-dev.yml                # Deploy to dev
│       ├── deploy-prod.yml               # Deploy to prod
│       └── database-migration.yml        # Run migrations
│
├── docs/
│   ├── API.md                            # API documentation
│   ├── DEPLOYMENT.md                     # Deployment guide
│   ├── VITEC_INTEGRATION.md              # Vitec setup guide
│   ├── DEVELOPMENT.md                    # Local dev setup
│   └── ARCHITECTURE.md                   # System architecture
│
├── docker-compose.yml                    # Local development
├── .gitignore
├── README.md
└── LICENSE

---

## 7. Technology Stack

### 7.1 Backend (FastAPI)

**Core Dependencies (requirements.txt):**
```txt
# FastAPI & Server
fastapi==0.109.0
uvicorn[standard]==0.27.0
python-multipart==0.0.6

# Database
sqlalchemy==2.0.25
alembic==1.13.1
psycopg2-binary==2.9.9
asyncpg==0.29.0

# Data Validation
pydantic==2.5.3
pydantic-settings==2.1.0

# Document Processing
python-docx==1.1.0
PyPDF2==3.0.1
Pillow==10.2.0
pypandoc==1.12

# Azure Services
azure-storage-blob==12.19.0
azure-identity==1.15.0
azure-keyvault-secrets==4.7.0

# HTTP Client
httpx==0.26.0

# Caching
redis==5.0.1

# Utilities
python-jose[cryptography]==3.3.0
python-dateutil==2.8.2

# Logging
loguru==0.7.2
```

**Development Dependencies (requirements-dev.txt):**
```txt
pytest==7.4.4
pytest-asyncio==0.23.3
pytest-cov==4.1.0
black==24.1.1
flake8==7.0.0
mypy==1.8.0
httpx-mock==0.14.0
```

### 7.2 Frontend (Next.js)

**Dependencies (package.json):**
```json
{
  "name": "proaktiv-dokument-hub-frontend",
  "version": "1.0.0",
  "dependencies": {
    "next": "14.1.0",
    "react": "18.2.0",
    "react-dom": "18.2.0",
    "typescript": "5.3.3",
    
    "@radix-ui/react-dialog": "^1.0.5",
    "@radix-ui/react-dropdown-menu": "^2.0.6",
    "@radix-ui/react-select": "^2.0.0",
    "@radix-ui/react-tabs": "^1.0.4",
    "@radix-ui/react-toast": "^1.1.5",
    "@radix-ui/react-slot": "^1.0.2",
    
    "tailwindcss": "3.4.1",
    "class-variance-authority": "^0.7.0",
    "clsx": "^2.1.0",
    "tailwind-merge": "^2.2.0",
    
    "lucide-react": "^0.312.0",
    "axios": "1.6.5",
    "react-dropzone": "14.2.3",
    "react-pdf": "7.7.0",
    "zustand": "4.4.7",
    "date-fns": "3.2.0",
    "react-hook-form": "7.49.3",
    "zod": "3.22.4",
    "@hookform/resolvers": "^3.3.4"
  },
  "devDependencies": {
    "@types/node": "20.11.5",
    "@types/react": "18.2.48",
    "@types/react-dom": "18.2.18",
    "eslint": "8.56.0",
    "eslint-config-next": "14.1.0",
    "autoprefixer": "10.4.17",
    "postcss": "8.4.33"
  }
}
```

---

## 8. Azure Infrastructure

### 8.1 Resource Group Structure
Resource Group: rg-proaktiv-dokument-hub-prod
Location: West Europe
Resources:
├── Container App Environment
│   └── cae-dokument-hub-prod
│       ├── Container App: ca-dokument-hub-frontend
│       └── Container App: ca-dokument-hub-backend
│
├── Database
│   └── PostgreSQL Flexible Server: psql-dokument-hub-prod
│       └── Database: dokument_hub
│
├── Storage
│   └── Storage Account: stdokumenthubprod
│       ├── Blob Container: templates
│       ├── Blob Container: previews
│       └── Blob Container: generated-documents
│
├── Security
│   └── Key Vault: kv-dokument-hub-prod
│       ├── Secret: vitec-installation-id
│       ├── Secret: vitec-access-key
│       ├── Secret: vitec-environment
│       └── Secret: database-password
│
├── Caching (Optional)
│   └── Azure Cache for Redis: redis-dokument-hub-prod
│
├── Monitoring
│   ├── Log Analytics Workspace: log-dokument-hub-prod
│   └── Application Insights: ai-dokument-hub-prod
│
└── Container Registry
└── ACR: acrdokumenthubprod

### 8.2 Container Apps Configuration

**Frontend Container App:**
```yaml
name: ca-dokument-hub-frontend
properties:
  managedEnvironmentId: /subscriptions/{sub-id}/resourceGroups/rg-proaktiv-dokument-hub-prod/providers/Microsoft.App/managedEnvironments/cae-dokument-hub-prod
  configuration:
    ingress:
      external: true
      targetPort: 3000
      transport: http
      customDomains:
        - name: dokumenthub.proaktiv.no
          bindingType: SniEnabled
    secrets:
      - name: entra-client-secret
        keyVaultUrl: https://kv-dokument-hub-prod.vault.azure.net/secrets/entra-client-secret
    registries:
      - server: acrdokumenthubprod.azurecr.io
        identity: system
  template:
    containers:
      - name: frontend
        image: acrdokumenthubprod.azurecr.io/dokument-hub-frontend:latest
        resources:
          cpu: 0.5
          memory: 1Gi
        env:
          - name: NEXT_PUBLIC_API_URL
            value: https://ca-dokument-hub-backend.internal.domain.com
    scale:
      minReplicas: 1
      maxReplicas: 5
      rules:
        - name: http-scaling
          http:
            metadata:
              concurrentRequests: "100"
```

**Backend Container App:**
```yaml
name: ca-dokument-hub-backend
properties:
  managedEnvironmentId: /subscriptions/{sub-id}/resourceGroups/rg-proaktiv-dokument-hub-prod/providers/Microsoft.App/managedEnvironments/cae-dokument-hub-prod
  configuration:
    ingress:
      external: false  # Internal only
      targetPort: 8000
      transport: http
    secrets:
      - name: database-password
        keyVaultUrl: https://kv-dokument-hub-prod.vault.azure.net/secrets/database-password
      - name: storage-connection-string
        keyVaultUrl: https://kv-dokument-hub-prod.vault.azure.net/secrets/storage-connection-string
  template:
    containers:
      - name: backend
        image: acrdokumenthubprod.azurecr.io/dokument-hub-backend:latest
        resources:
          cpu: 1.0
          memory: 2Gi
        env:
          - name: DATABASE_URL
            secretRef: database-password
          - name: AZURE_STORAGE_CONNECTION_STRING
            secretRef: storage-connection-string
          - name: KEY_VAULT_URL
            value: https://kv-dokument-hub-prod.vault.azure.net/
          - name: REDIS_URL
            value: redis://redis-dokument-hub-prod.redis.cache.windows.net:6380?ssl=True
    scale:
      minReplicas: 2
      maxReplicas: 10
```

### 8.3 Easy Auth Configuration

**Applied to Frontend Container App:**
```json
{
  "properties": {
    "platform": {
      "enabled": true
    },
    "globalValidation": {
      "requireAuthentication": true,
      "unauthenticatedClientAction": "RedirectToLoginPage",
      "redirectToProvider": "azureActiveDirectory"
    },
    "identityProviders": {
      "azureActiveDirectory": {
        "enabled": true,
        "registration": {
          "clientId": "<your-entra-app-client-id>",
          "clientSecretSettingName": "entra-client-secret",
          "openIdIssuer": "https://login.microsoftonline.com/<tenant-id>/v2.0"
        },
        "validation": {
          "allowedAudiences": [
            "api://<your-entra-app-client-id>"
          ]
        }
      }
    },
    "login": {
      "tokenStore": {
        "enabled": true
      }
    },
    "httpSettings": {
      "forwardProxy": {
        "convention": "Standard"
      }
    }
  }
}
```

### 8.4 PostgreSQL Configuration
Server: psql-dokument-hub-prod.postgres.database.azure.com
Database: dokument_hub
Version: 15
Compute: B2ms (2 vCores, 8GB RAM)
Storage: 32 GB (auto-grow enabled)
Backup Retention: 7 days
High Availability: Zone-redundant (Production)
Firewall Rules:

Allow Azure Services: Enabled
Allow Container Apps: Configured via Private Endpoint

Connection String:
postgresql://adminuser@psql-dokument-hub-prod:PASSWORD@psql-dokument-hub-prod.postgres.database.azure.com:5432/dokument_hub?sslmode=require

### 8.5 Blob Storage Configuration
Account: stdokumenthubprod
Tier: Standard (General Purpose v2)
Replication: LRS (Locally Redundant Storage)
Performance: Standard
Access Tier: Hot
Containers:

templates

Public Access: None
Lifecycle: Retain indefinitely


previews

Public Access: None (access via SAS tokens)
Lifecycle: Delete after 90 days if not accessed


generated-documents

Public Access: None
Lifecycle: Delete after 30 days



CORS Settings:

Allowed Origins: https://dokumenthub.proaktiv.no
Allowed Methods: GET, POST, PUT, DELETE
Allowed Headers: *
Exposed Headers: Content-Length, Content-Type
Max Age: 3600


---

## 9. Security & Authentication

### 9.1 Authentication Flow
User Request
│
▼
Azure Front Door / CDN
│
▼
Container Apps (Easy Auth Enabled)
│
├─> Unauthenticated?
│   └─> Redirect to Microsoft Login
│       └─> Entra ID Authentication
│           └─> Redirect back with token
│
▼
Authenticated Request
│
├─> Easy Auth injects headers:
│   - X-MS-CLIENT-PRINCIPAL-NAME (email)
│   - X-MS-CLIENT-PRINCIPAL-ID (user ID)
│   - X-MS-CLIENT-PRINCIPAL (Base64 encoded user info)
│
▼
FastAPI Backend
│
├─> Extract user from headers
├─> Validate user
└─> Process request

### 9.2 Authorization Middleware
```python
# backend/app/middleware/auth.py
from fastapi import Request, HTTPException
from typing import Optional
import base64
import json

class AuthContext:
    def __init__(self, email: str, user_id: str, name: str):
        self.email = email
        self.user_id = user_id
        self.name = name
    
    @property
    def is_admin(self) -> bool:
        # Check if user is admin (based on email domain or group membership)
        admin_emails = ["troyian@proaktiv.no"]  # Configure via env var
        return self.email in admin_emails

def get_current_user(request: Request) -> AuthContext:
    """
    Extract user information from Easy Auth headers.
    
    Headers injected by Azure Easy Auth:
    - X-MS-CLIENT-PRINCIPAL-NAME: user email
    - X-MS-CLIENT-PRINCIPAL-ID: user ID
    - X-MS-CLIENT-PRINCIPAL: Base64 encoded JSON with full user info
    """
    email = request.headers.get("X-MS-CLIENT-PRINCIPAL-NAME")
    user_id = request.headers.get("X-MS-CLIENT-PRINCIPAL-ID")
    
    if not email or not user_id:
        # Try to extract from X-MS-CLIENT-PRINCIPAL
        principal_header = request.headers.get("X-MS-CLIENT-PRINCIPAL")
        if principal_header:
            try:
                principal_data = json.loads(
                    base64.b64decode(principal_header).decode("utf-8")
                )
                email = principal_data.get("claims", [{}])[0].get("val")
                user_id = principal_data.get("userId")
            except:
                pass
    
    if not email:
        raise HTTPException(
            status_code=401,
            detail="Authentication required"
        )
    
    # Extract name from email (or fetch from Entra ID if needed)
    name = email.split("@")[0].title()
    
    return AuthContext(email=email, user_id=user_id, name=name)
```

### 9.3 API Security Headers
```python
# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

app = FastAPI(title="Proaktiv Dokument Hub API")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://dokumenthub.proaktiv.no",
        "https://ca-dokument-hub-frontend.*.azurecontainerapps.io"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trusted Host
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=[
        "dokumenthub.proaktiv.no",
        "*.azurecontainerapps.io"
    ]
)

# Security Headers
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response
```

### 9.4 Data Encryption

**At Rest:**
- Azure Blob Storage: Encrypted by default with Microsoft-managed keys
- PostgreSQL: Transparent Data Encryption (TDE) enabled
- Key Vault: Hardware Security Module (HSM) backed

**In Transit:**
- All API calls over HTTPS/TLS 1.2+
- Vitec API calls over HTTPS
- Internal Container App communication over mTLS

---

## 10. Document Preview Strategy

### 10.1 PDF Files
**Frontend:** Use `react-pdf` (PDF.js wrapper)
```tsx
// frontend/src/components/templates/TemplatePreview.tsx
import { Document, Page, pdfjs } from 'react-pdf';
import 'react-pdf/dist/esm/Page/AnnotationLayer.css';
import 'react-pdf/dist/esm/Page/TextLayer.css';

pdfjs.GlobalWorkerOptions.workerSrc = `//cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjs.version}/pdf.worker.min.js`;

export function PDFPreview({ url }: { url: string }) {
  const [numPages, setNumPages] = useState<number>(0);
  const [pageNumber, setPageNumber] = useState<number>(1);

  return (
    <div>
      <Document
        file={url}
        onLoadSuccess={({ numPages }) => setNumPages(numPages)}
      >
        <Page pageNumber={pageNumber} />
      </Document>
      
      <div className="flex justify-between mt-4">
        <Button
          onClick={() => setPageNumber(Math.max(1, pageNumber - 1))}
          disabled={pageNumber === 1}
        >
          Previous
        </Button>
        <span>
          Page {pageNumber} of {numPages}
        </span>
        <Button
          onClick={() => setPageNumber(Math.min(numPages, pageNumber + 1))}
          disabled={pageNumber === numPages}
        >
          Next
        </Button>
      </div>
    </div>
  );
}
```

### 10.2 Word Files (.docx)

**Backend:** Convert to PDF for preview
```python
# backend/app/services/document_preview.py
import subprocess
from pathlib import Path
from azure.storage.blob import BlobServiceClient
import tempfile
import logging

logger = logging.getLogger(__name__)

async def generate_word_preview(
    blob_url: str,
    storage_client: BlobServiceClient
) -> str:
    """
    Convert Word document to PDF for preview.
    
    Uses LibreOffice headless mode for conversion.
    
    Args:
        blob_url: URL to Word document in Blob Storage
        storage_client: Azure Storage client
    
    Returns:
        URL to generated PDF preview
    """
    try:
        # Download Word file to temp
        with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as temp_docx:
            # Download from blob storage
            blob_data = storage_client.download_blob(blob_url)
            temp_docx.write(blob_data.readall())
            docx_path = temp_docx.name
        
        # Convert to PDF using LibreOffice
        output_dir = Path(docx_path).parent
        subprocess.run([
            "soffice",
            "--headless",
            "--convert-to", "pdf",
            "--outdir", str(output_dir),
            docx_path
        ], check=True, timeout=30)
        
        # Upload PDF to previews container
        pdf_path = docx_path.replace(".docx", ".pdf")
        preview_blob_name = f"{Path(blob_url).stem}_preview.pdf"
        
        with open(pdf_path, "rb") as pdf_file:
            blob_client = storage_client.get_blob_client(
                container="previews",
                blob=preview_blob_name
            )
            blob_client.upload_blob(pdf_file, overwrite=True)
        
        # Clean up temp files
        Path(docx_path).unlink()
        Path(pdf_path).unlink()
        
        preview_url = blob_client.url
        logger.info(f"Generated preview: {preview_url}")
        return preview_url
        
    except Exception as e:
        logger.error(f"Failed to generate Word preview: {e}")
        raise
```

**Dockerfile addition:**
```dockerfile
# Install LibreOffice for document conversion
RUN apt-get update && apt-get install -y \
    libreoffice \
    libreoffice-writer \
    && rm -rf /var/lib/apt/lists/*
```

---

## 11. Deployment Strategy

### 11.1 CI/CD Pipeline (GitHub Actions)

**Backend CI/CD (.github/workflows/backend-ci.yml):**
```yaml
name: Backend CI/CD

on:
  push:
    branches: [main, develop]
    paths:
      - 'backend/**'
  pull_request:
    branches: [main]
    paths:
      - 'backend/**'

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt -r requirements-dev.txt
      
      - name: Run tests
        run: |
          cd backend
          pytest --cov=app --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./backend/coverage.xml

  build-and-deploy:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Login to Azure
        uses: azure/login@v1
        with:
          creds: ${{ secrets.AZURE_CREDENTIALS }}
      
      - name: Build and push Docker image
        run: |
          az acr login --name acrdokumenthubprod
          docker build -t acrdokumenthubprod.azurecr.io/dokument-hub-backend:${{ github.sha }} ./backend
          docker push acrdokumenthubprod.azurecr.io/dokument-hub-backend:${{ github.sha }}
      
      - name: Deploy to Container App
        run: |
          az containerapp update \
            --name ca-dokument-hub-backend \
            --resource-group rg-proaktiv-dokument-hub-prod \
            --image acrdokumenthubprod.azurecr.io/dokument-hub-backend:${{ github.sha }}
      
      - name: Run database migrations
        run: |
          # Run migrations via Container App job or exec
          az containerapp exec \
            --name ca-dokument-hub-backend \
            --resource-group rg-proaktiv-dokument-hub-prod \
            --command "alembic upgrade head"
```

### 11.2 Database Migrations

**Alembic migration example:**
```python
# backend/alembic/versions/001_initial_schema.py
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSONB

def upgrade():
    # Create templates table
    op.create_table(
        'templates',
        sa.Column('id', UUID, primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('file_name', sa.String(255), nullable=False),
        sa.Column('file_type', sa.String(10), nullable=False),
        sa.Column('file_size_bytes', sa.BigInteger, nullable=False),
        sa.Column('azure_blob_url', sa.Text, nullable=False),
        sa.Column('azure_blob_container', sa.String(100), server_default='templates'),
        sa.Column('status', sa.String(20), server_default='draft'),
        sa.Column('version', sa.Integer, server_default='1'),
        sa.Column('created_by', sa.String(255), nullable=False),
        sa.Column('created_at', sa.DateTime, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_by', sa.String(255), nullable=False),
        sa.Column('updated_at', sa.DateTime, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('published_at', sa.DateTime, nullable=True),
        sa.Column('preview_url', sa.Text, nullable=True),
        sa.Column('page_count', sa.Integer, nullable=True),
        sa.Column('language', sa.String(10), server_default='nb-NO'),
        sa.Column('vitec_merge_fields', ARRAY(sa.Text), nullable=True),
        sa.Column('metadata', JSONB, nullable=True),
    )
    
    # Create indexes
    op.create_index('idx_templates_status', 'templates', ['status'])
    op.create_index('idx_templates_created_at', 'templates', ['created_at'])
    
    # ... (rest of tables)

def downgrade():
    op.drop_table('templates')
```

### 11.3 Environment-Specific Configuration

**Development (.env.dev):**
```bash
DATABASE_URL=postgresql://admin:password@localhost:5432/dokument_hub_dev
AZURE_STORAGE_CONNECTION_STRING=UseDevelopmentStorage=true
KEY_VAULT_URL=https://kv-dokument-hub-dev.vault.azure.net/
VITEC_INSTALLATION_ID=MSPROATEST
VITEC_ENVIRONMENT=qa
LOG_LEVEL=DEBUG
```

**Production (.env.prod):**
```bash
DATABASE_URL=<from-key-vault>
AZURE_STORAGE_CONNECTION_STRING=<from-key-vault>
KEY_VAULT_URL=https://kv-dokument-hub-prod.vault.azure.net/
VITEC_INSTALLATION_ID=<production-id>
VITEC_ENVIRONMENT=production
LOG_LEVEL=INFO
```

---

## 12. Monitoring & Logging

### 12.1 Application Insights Configuration
```python
# backend/app/main.py
from opencensus.ext.azure.log_exporter import AzureLogHandler
from opencensus.ext.azure import metrics_exporter
import logging

# Configure Azure Application Insights
logger = logging.getLogger(__name__)
logger.addHandler(
    AzureLogHandler(
        connection_string='InstrumentationKey=<your-key>'
    )
)

# Track custom metrics
exporter = metrics_exporter.new_metrics_exporter(
    connection_string='InstrumentationKey=<your-key>'
)

# Custom metrics
@app.middleware("http")
async def track_request_metrics(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    
    # Track request duration
    properties = {
        'custom_dimensions': {
            'endpoint': request.url.path,
            'method': request.method,
            'status_code': response.status_code
        }
    }
    logger.info(f"Request processed in {duration:.2f}s", extra=properties)
    
    return response
```

### 12.2 Logging Structure
```python
# backend/app/utils/logging.py
import logging
from pythonjsonlogger import jsonlogger

def setup_logging():
    """Configure structured JSON logging"""
    logger = logging.getLogger()
    
    handler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter(
        '%(timestamp)s %(level)s %(name)s %(message)s %(user_email)s %(request_id)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
```

### 12.3 Alerts

**Critical Alerts:**
1. **High Error Rate:** > 5% 5xx errors in 5 minutes
2. **Vitec API Failures:** Connection test fails 3 times in 10 minutes
3. **Database Connection Issues:** Cannot connect to PostgreSQL
4. **Storage Failures:** Blob upload/download fails repeatedly

**Warning Alerts:**
1. **Slow Response Times:** P95 latency > 2 seconds
2. **Low Disk Space:** Storage account > 80% capacity
3. **High Memory Usage:** Container App memory > 80%

---

## 13. Phase 1 vs Phase 2 Roadmap

### Phase 1: Core Document Management (MVP)
**Timeline:** 4-6 weeks  
**Status:** Immediate Development

**Features:**
✅ User authentication via Microsoft Entra ID  
✅ Template upload (Word/PDF/Excel)  
✅ Azure Blob Storage integration  
✅ Document preview (PDF direct, Word-to-PDF conversion)  
✅ Metadata management (title, description)  
✅ Tag system (create, assign, filter)  
✅ Category system (create, assign, filter)  
✅ Basic version control (overwrite with history)  
✅ Search and filter functionality  
✅ Template status workflow (Draft → Published → Archived)  
✅ Audit logging (who did what, when)  
✅ Admin dashboard with statistics  
✅ Vitec connection test endpoint (verify API access)  

**Deliverables:**
- Working Next.js frontend with Shadcn UI
- FastAPI backend with PostgreSQL database
- Azure infrastructure (Container Apps, Storage, Key Vault)
- CI/CD pipeline (GitHub Actions)
- Basic documentation

**Success Criteria:**
- Admins can upload templates in < 30 seconds
- Preview generation completes in < 10 seconds
- All employees can search and download templates
- 99.9% uptime
- Zero security vulnerabilities

---

### Phase 2: Vitec Integration & Template Hydration
**Timeline:** 6-8 weeks after Phase 1  
**Status:** Future Enhancement

**Features:**
🔄 Full Vitec API integration  
🔄 Fetch estates (properties/cases) from Vitec  
🔄 Fetch contacts (sellers, buyers) from Vitec  
🔄 Fetch departments and employees  
🔄 Merge field configuration UI  
🔄 Template merge field mapping  
🔄 Generate documents with Vitec data  
🔄 Preview merged documents before download  
🔄 Bulk document generation  
🔄 Automated template distribution (optional)  
🔄 Advanced analytics (usage tracking per employee)  
🔄 Employee-facing portal (non-admin users)  

**Technical Requirements:**
- Redis caching for Vitec API responses
- Background job processing (Celery/Dramatiq)
- Advanced document merge logic (python-docx, PyPDF2)
- WebSocket for real-time merge progress
- Enhanced audit logging for generated documents

**Success Criteria:**
- Template merge completes in < 5 seconds
- 100% accurate data population from Vitec
- Support for complex merge scenarios (tables, lists)
- Employee adoption rate > 80% within 3 months

---

## 14. Testing Strategy

### 14.1 Backend Tests

**Unit Tests (pytest):**
```python
# backend/tests/test_templates.py
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db

client = TestClient(app)

def test_create_template_success():
    """Test successful template upload"""
    response = client.post(
        "/api/templates",
        files={"file": ("test.docx", b"fake content", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
        data={
            "title": "Test Template",
            "status": "draft"
        },
        headers={"X-MS-CLIENT-PRINCIPAL-NAME": "test@proaktiv.no"}
    )
    assert response.status_code == 201
    assert response.json()["title"] == "Test Template"

def test_create_template_invalid_file_type():
    """Test upload rejection for invalid file types"""
    response = client.post(
        "/api/templates",
        files={"file": ("test.exe", b"fake content", "application/octet-stream")},
        data={"title": "Test"},
        headers={"X-MS-CLIENT-PRINCIPAL-NAME": "test@proaktiv.no"}
    )
    assert response.status_code == 400
    assert "Invalid file type" in response.json()["detail"]
```

**Integration Tests:**
```python
# backend/tests/test_vitec_integration.py
import pytest
from app.services.vitec_client import VitecHubClient

@pytest.mark.asyncio
async def test_vitec_connection():
    """Test Vitec API connectivity"""
    client = VitecHubClient(
        installation_id="MSPROATEST",
        access_key="test-key",
        environment="qa"
    )
    result = await client.test_connection()
    assert result["status"] == "success"
```

### 14.2 Frontend Tests

**Component Tests (Jest + React Testing Library):**
```typescript
// frontend/src/components/templates/__tests__/TemplateCard.test.tsx
import { render, screen } from '@testing-library/react';
import { TemplateCard } from '../TemplateCard';

describe('TemplateCard', () => {
  it('renders template information', () => {
    const template = {
      id: '123',
      title: 'Test Template',
      status: 'published',
      file_type: 'docx'
    };
    
    render(<TemplateCard template={template} />);
    
    expect(screen.getByText('Test Template')).toBeInTheDocument();
    expect(screen.getByText('published')).toBeInTheDocument();
  });
});
```

**E2E Tests (Playwright):**
```typescript
// frontend/tests/e2e/template-upload.spec.ts
import { test, expect } from '@playwright/test';

test('admin can upload a template', async ({ page }) => {
  await page.goto('/templates/new');
  
  // Upload file
  const fileInput = page.locator('input[type="file"]');
  await fileInput.setInputFiles('test-files/sample.docx');
  
  // Fill metadata
  await page.fill('input[name="title"]', 'E2E Test Template');
  await page.fill('textarea[name="description"]', 'Test description');
  
  // Submit
  await page.click('button[type="submit"]');
  
  // Verify success
  await expect(page.locator('.success-message')).toBeVisible();
  await expect(page).toHaveURL(/\/templates\/[a-f0-9-]+/);
});
```

---

## 15. Success Metrics

### 15.1 Performance Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Template Upload Time | < 30 seconds | Time from file select to success message |
| Preview Generation (Word) | < 10 seconds | Time to convert Word → PDF |
| Preview Generation (PDF) | < 2 seconds | Time to display PDF |
| API Response Time (List) | < 500ms | P95 latency for GET /api/templates |
| API Response Time (Detail) | < 200ms | P95 latency for GET /api/templates/{id} |
| Search Results | < 1 second | Time to display filtered results |
| Vitec API Call | < 2 seconds | Time to fetch estate data |
| Template Download | < 5 seconds | Time to generate SAS URL and start download |

### 15.2 Reliability Metrics

| Metric | Target |
|--------|--------|
| Uptime | 99.9% (< 44 minutes downtime/month) |
| Error Rate | < 1% of all requests |
| Vitec API Success Rate | > 99% |
| Storage Upload Success | > 99.9% |

### 15.3 User Adoption Metrics

| Metric | Target (3 months post-launch) |
|--------|-------------------------------|
| Active Users | 80% of employees |
| Templates Uploaded | > 100 templates |
| Monthly Downloads | >