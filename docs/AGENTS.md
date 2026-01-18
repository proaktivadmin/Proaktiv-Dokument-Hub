# AGENTS.md - Proaktiv Document Hub Codebase Guide

**Last Updated**: January 2026
**Project**: Proaktiv Document Hub
**Status**: Active Development - Feature Expansion Phase

---

## 🎯 PROJECT OVERVIEW

### Mission
Centralize and modernize document management for Proaktiv's real estate operations, serving as the Master Template Library integrated with Vitec Next CRM.

### Core Architecture
- **Frontend**: Next.js 14 (App Router) + React + TypeScript
- **Backend**: FastAPI + Python 3.11+
- **Infrastructure**: Azure (Web Apps, Storage, Functions)
- **CRM Integration**: Vitec Next API
- **Microsoft Stack**: Graph API (Teams, SharePoint, Exchange)
- **Development**: Cursor IDE with Claude 4.5 Sonnet

### Current Features
- Document Hub with template library
- Vitec Next CRM integration
- Premium HTML document generation
- Internal documentation system

### Features In Development (This Sprint)
1. **Employee Management** - Role-based user management with Teams integration
2. **Leverandører Directory** - Supplier contact management with issue tracking
3. **Photo Export Automation** - Bulk property photo processing from proaktiv.no

---

## 🏗️ PROJECT STRUCTURE

```
proaktiv-dokument-hub/
├── frontend/                 # Next.js application
│   ├── app/                 # App router pages
│   ├── components/          # React components
│   ├── lib/                 # Utilities & helpers
│   └── public/              # Static assets
├── backend/                  # FastAPI application
│   ├── api/                 # API routes
│   ├── services/            # Business logic
│   ├── models/              # Data models
│   └── integrations/        # External API clients
├── docs/                    # Documentation
├── scripts/                 # Automation scripts
└── azure/                   # Infrastructure configs
```

---

## 🧠 AGENT ORCHESTRATION SYSTEM

### RALPH LOOP Workflow
This project uses the RALPH LOOP (Recursive Agentic Loop for Progressive Handling) methodology for feature development:

```
IDEA → PRD → PROGRESS.TXT → FEATURES → TASKS → RALPH LOOP → NEW SESSION
```

**How it works:**
1. **IDEA**: Feature concept is defined
2. **PRD**: Product Requirements Document created (see PRD.md)
3. **PROGRESS.TXT**: Track what's done/blocked/next
4. **FEATURES**: Break into logical feature units
5. **TASKS**: Each feature divided into actionable tasks
6. **RALPH LOOP**: Iterative development with continuous progress updates
7. **NEW SESSION**: Each Cursor session starts with full context from docs

### Current Sprint Structure
See `/docs/features/` for individual feature breakdowns:
- `employee-management/TASKS.md`
- `leverandorer/TASKS.md`
- `photo-export/TASKS.md`

---

## 💻 DEVELOPMENT PRINCIPLES

### Core Philosophy
**"Keep it simple, don't over-engineer"**
- This is a single-person app
- Quality over speed
- Ask questions when unclear
- Suggest alternatives when you have better solutions
- Take time to do it right

### Communication Style
- Be conversational and collaborative
- Brief progress notes (1-5 sentences) about what you just did
- Use markdown specs and bullet points for lists
- No excessive headings or bold text in casual chat
- Flag blockers and ask questions proactively

### Code Standards
```typescript
// TypeScript/React conventions
- Use TypeScript strict mode
- Functional components with hooks
- Server components by default in Next.js
- Client components only when needed (use 'use client')

// Python/FastAPI conventions  
- Type hints everywhere
- Pydantic models for validation
- Async/await for I/O operations
- Follow PEP 8 style guide
```

---

## 🔧 CRITICAL EXECUTION RULES

### Before Making Changes
1. **Search First**: Use codebase_search to understand existing patterns
2. **Read Context**: Always read relevant files before editing
3. **Check Dependencies**: Look for related code that might be affected
4. **Plan Approach**: Outline changes before executing

### When Making Code Changes
1. **NEVER Output Code to Chat**: Use edit_file tool instead
2. **Small, Focused Edits**: One logical change per edit
3. **Add Necessary Imports**: Include all required dependencies
4. **Test After Changes**: Verify compilation and basic functionality
5. **Update PROGRESS.md**: Log what was completed

### Tool Usage Patterns
```
# ALWAYS prefer semantic search over grep
✓ codebase_search("user authentication flow")
✗ grep_search("def login")

# Read before editing
✓ read_file("components/UserCard.tsx")
→ edit_file("components/UserCard.tsx", ...)

# Parallel tool calls for independent operations
✓ [codebase_search("api routes"), list_dir("backend/api")]

# Sequential for dependent operations
✓ read_file() → understand → edit_file()
```

---

## 🔌 INTEGRATION PATTERNS

### Vitec Next API
```python
# Location: backend/integrations/vitec_client.py

class VitecClient:
    """
    Integration with Vitec Next CRM
    - Partner Portal API access
    - OAuth authentication
    - Rate limiting handled
    """
    
    async def get_employees(self) -> List[Employee]:
        """Fetch all employees with system roles"""
        
    async def get_suppliers(self) -> List[Supplier]:
        """Fetch active partner integrations"""
```

**Common Operations:**
- Employee sync: `/api/vitec/employees`
- Supplier list: `/api/vitec/suppliers`  
- Property data: `/api/vitec/properties/{id}`

### Microsoft Graph API
```python
# Location: backend/integrations/microsoft_graph.py

class GraphClient:
    """
    Microsoft 365 integration
    - Teams groups management
    - SharePoint file operations
    - Exchange email sending
    """
    
    async def get_teams_groups(self) -> List[Team]:
        """Fetch all Teams groups"""
        
    async def send_email(self, to: List[str], subject: str, body: str):
        """Send email via Exchange"""
```

**Authentication:**
- Uses Azure AD app registration
- Client credentials flow for service account
- Scopes: `Mail.Send`, `Group.Read.All`, `Sites.ReadWrite.All`

### Azure Storage
```python
# Location: backend/services/storage.py

# WebDAV access for photo exports
WEBDAV_PATH = "proaktiv.no/shared/"

# Azure Blob Storage for documents
STORAGE_CONTAINER = "documents"
```

---

## 📊 DATABASE PATTERNS

### Models Structure
```python
# backend/models/

class Employee(BaseModel):
    id: str
    name: str
    email: str
    roles: List[str]  # e.g., ["eiendomsmegler", "superbruker"]
    office_location: str
    active: bool

class Supplier(BaseModel):
    id: str
    name: str
    category: str
    is_connected: bool
    account_manager: ContactInfo
    integration_details: Optional[Dict]
    
class Issue(BaseModel):
    id: str
    supplier_id: str
    title: str
    description: str
    status: IssueStatus  # Open | InProgress | Resolved
    created_at: datetime
    resolved_at: Optional[datetime]
```

---

## 🎨 FRONTEND PATTERNS

### Component Structure
```typescript
// components/
// ├── ui/              # Reusable UI components
// ├── features/        # Feature-specific components
// └── layouts/         # Layout components

// Example: Feature component
export function EmployeeList({ filters }: EmployeeListProps) {
  const { employees, isLoading } = useEmployees(filters)
  
  if (isLoading) return <Skeleton />
  
  return (
    <div className="grid gap-4">
      {employees.map(emp => (
        <EmployeeCard key={emp.id} employee={emp} />
      ))}
    </div>
  )
}
```

### API Routes (Next.js)
```typescript
// app/api/employees/route.ts

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url)
  const role = searchParams.get('role')
  
  const response = await fetch(`${API_URL}/employees?role=${role}`)
  return Response.json(await response.json())
}
```

---

## 🚀 COMMON WORKFLOWS

### Adding a New Feature
1. Create feature directory in `/docs/features/{feature-name}/`
2. Write TASKS.md with breakdown
3. Update PROGRESS.md with feature status
4. Implement backend models → services → API routes
5. Create frontend components → pages → integration
6. Test end-to-end functionality
7. Update PRD.md to mark feature complete

### Debugging Issues
1. Check PROGRESS.md for recent changes
2. Use codebase_search to find related code
3. Read error logs and stack traces
4. Add console.log / print statements strategically
5. Test in isolation before integration
6. Document solution in PROGRESS.md

### Working with External APIs
1. Check `/backend/integrations/` for existing clients
2. Review API documentation (links in comments)
3. Test with small requests first
4. Handle rate limiting and errors
5. Cache responses when appropriate
6. Log all external API calls

---

## 🎯 CURRENT SPRINT GOALS

### Employee Management Feature
**Status**: Planning → Implementation
**Files**: `/docs/features/employee-management/`
- [ ] Backend: Employee model with Vitec Next integration
- [ ] Backend: Teams groups API integration
- [ ] Frontend: Employee list with role filtering
- [ ] Frontend: Email group composer
- [ ] Testing: End-to-end employee workflows

### Leverandører Directory
**Status**: Planning
**Files**: `/docs/features/leverandorer/`
- [ ] Backend: Supplier model with issue tracking
- [ ] Backend: Vitec Next supplier sync
- [ ] Frontend: Connected vs Available views
- [ ] Frontend: Issue logging interface
- [ ] Frontend: Metrics dashboard

### Photo Export Automation
**Status**: Planning
**Files**: `/docs/features/photo-export/`
- [ ] Script: Excel file parser (yellow highlights)
- [ ] Script: Playwright automation for proaktiv.no/export
- [ ] Script: WebDAV folder monitoring
- [ ] Script: Local file copy operations
- [ ] Testing: Full automation workflow

---

## 📚 KEY RESOURCES

### Documentation Links
- **Vitec Next API**: [Partner Portal Documentation]
- **Microsoft Graph**: https://docs.microsoft.com/en-us/graph/
- **Next.js 14**: https://nextjs.org/docs
- **FastAPI**: https://fastapi.tiangolo.com/

### Internal Docs
- Brand Guidelines: `/docs/brand/proaktiv-guidelines.md`
- API Specifications: `/docs/api/`
- Deployment Guide: `/docs/deployment/azure-setup.md`

---

## ⚠️ IMPORTANT NOTES

### Norwegian Context
- **Language**: UI primarily in Norwegian (Bokmål)
- **Date Format**: DD.MM.YYYY
- **Location**: Stavanger, Rogaland, Norway

### Vitec Next Roles
These are the system roles that exist in Vitec Next:
- `eiendomsmegler` - Real estate agent
- `eiendomsmeglerfullmektig` - Associate real estate agent  
- `daglig leder` - Managing director
- `superbruker` - Super user (admin)
- `oppgjør` - Settlement/closing

### Security Considerations
- Never commit API keys or secrets
- Use Azure Key Vault for production secrets
- Environment variables for local development
- Sanitize user inputs from external APIs

---

## 🔄 SESSION CONTINUITY

### Starting a New Session
1. Read PROGRESS.md to understand current state
2. Check last entry to see what was completed
3. Review any blockers or questions
4. Continue from where previous session ended

### Ending a Session
1. Update PROGRESS.md with completed tasks
2. Note any blockers or questions for next session
3. Commit working code (don't leave broken state)
4. Document any technical decisions made

---

## 📞 GETTING HELP

### When Stuck
1. Search codebase for similar patterns
2. Check PROGRESS.md for context
3. Ask specific questions with code context
4. Suggest alternative approaches
5. Don't struggle in silence - ask for clarification

### Providing Feedback
User prefers:
- Clear, actionable suggestions
- Alternative solutions when available
- Questions when requirements are ambiguous
- Taking time to ensure quality

---

**Remember**: This is a one-person app. Keep things simple, don't over-engineer, and focus on quality over speed. When in doubt, ask questions!
