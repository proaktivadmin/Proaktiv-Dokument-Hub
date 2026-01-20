# Social Media & Google Business Integration Feature

## Overview
Integrate social media feeds (Instagram, Facebook) and Google Business profiles for offices and key brokers, with analytics and engagement metrics to track marketing performance.

## User Story
As an admin, I want to see social media activity and Google Business metrics for each office and key brokers, so I can monitor marketing effectiveness and engagement across all locations.

## Design Requirements

### Visual Style
- **Interactive feed cards** with modern, clean design
- **Embedded social media posts** (Instagram/Facebook)
- **Real-time metrics** with trend indicators (↑ ↓)
- **Responsive grid layout** matching app aesthetic
- **Color-coded performance** (green = growing, red = declining)

### Key Metrics to Display
- **Followers/Likes**: Current count + growth rate
- **Engagement Rate**: Likes, comments, shares per post
- **Post Frequency**: Posts per week/month
- **Reach/Impressions**: How many people see content
- **Top Performing Posts**: Most engagement
- **Response Time**: For Google Business reviews

## Data Sources

### 1. Instagram Business API
- **Endpoint**: Instagram Graph API
- **Authentication**: Facebook Business account required
- **Metrics Available**:
  - Follower count
  - Media insights (likes, comments, saves, reach)
  - Profile views
  - Website clicks
  - Impressions

### 2. Facebook Graph API
- **Endpoint**: Facebook Pages API
- **Authentication**: Facebook App + Page access token
- **Metrics Available**:
  - Page likes
  - Post reach and engagement
  - Page views
  - Actions on page (calls, directions, website clicks)

### 3. Google My Business API
- **Endpoint**: Google Business Profile API
- **Authentication**: Google OAuth 2.0
- **Metrics Available**:
  - Total reviews and average rating
  - Review response rate and time
  - Search views and map views
  - Customer actions (calls, direction requests, website visits)
  - Photos uploaded

## Database Schema

### New Tables

#### `social_media_accounts`
```sql
CREATE TABLE social_media_accounts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  office_id UUID REFERENCES offices(id) ON DELETE CASCADE,
  employee_id UUID REFERENCES employees(id) ON DELETE CASCADE,
  platform VARCHAR(50) NOT NULL, -- 'instagram', 'facebook', 'google_business'
  account_handle VARCHAR(255), -- @username or page name
  account_url TEXT NOT NULL,
  account_id VARCHAR(255), -- Platform-specific ID
  access_token TEXT, -- Encrypted API token
  is_active BOOLEAN DEFAULT true,
  is_featured BOOLEAN DEFAULT false, -- For key brokers
  use_for_marketing BOOLEAN DEFAULT false, -- Brokers using for work
  last_synced_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  
  CONSTRAINT check_owner CHECK (
    (office_id IS NOT NULL AND employee_id IS NULL) OR
    (office_id IS NULL AND employee_id IS NOT NULL)
  ),
  CONSTRAINT unique_account UNIQUE (platform, account_id)
);

CREATE INDEX idx_social_accounts_office ON social_media_accounts(office_id);
CREATE INDEX idx_social_accounts_employee ON social_media_accounts(employee_id);
CREATE INDEX idx_social_accounts_platform ON social_media_accounts(platform);
```

#### `social_media_metrics`
```sql
CREATE TABLE social_media_metrics (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  account_id UUID REFERENCES social_media_accounts(id) ON DELETE CASCADE,
  metric_date DATE NOT NULL,
  
  -- Common metrics
  followers_count INTEGER,
  following_count INTEGER,
  posts_count INTEGER,
  
  -- Engagement metrics
  total_likes INTEGER,
  total_comments INTEGER,
  total_shares INTEGER,
  engagement_rate DECIMAL(5,2), -- Percentage
  
  -- Reach metrics
  impressions INTEGER,
  reach INTEGER,
  profile_views INTEGER,
  
  -- Action metrics
  website_clicks INTEGER,
  email_clicks INTEGER,
  phone_clicks INTEGER,
  direction_requests INTEGER,
  
  -- Google Business specific
  search_views INTEGER,
  map_views INTEGER,
  reviews_count INTEGER,
  average_rating DECIMAL(3,2),
  review_response_rate DECIMAL(5,2),
  avg_response_time_hours DECIMAL(6,2),
  
  created_at TIMESTAMP DEFAULT NOW(),
  
  CONSTRAINT unique_metric_date UNIQUE (account_id, metric_date)
);

CREATE INDEX idx_metrics_account ON social_media_metrics(account_id);
CREATE INDEX idx_metrics_date ON social_media_metrics(metric_date);
```

#### `social_media_posts`
```sql
CREATE TABLE social_media_posts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  account_id UUID REFERENCES social_media_accounts(id) ON DELETE CASCADE,
  platform_post_id VARCHAR(255) NOT NULL,
  post_type VARCHAR(50), -- 'image', 'video', 'carousel', 'reel'
  caption TEXT,
  media_url TEXT,
  thumbnail_url TEXT,
  permalink TEXT,
  
  -- Engagement
  likes_count INTEGER DEFAULT 0,
  comments_count INTEGER DEFAULT 0,
  shares_count INTEGER DEFAULT 0,
  saves_count INTEGER DEFAULT 0,
  
  -- Reach
  impressions INTEGER DEFAULT 0,
  reach INTEGER DEFAULT 0,
  
  posted_at TIMESTAMP NOT NULL,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  
  CONSTRAINT unique_platform_post UNIQUE (account_id, platform_post_id)
);

CREATE INDEX idx_posts_account ON social_media_posts(account_id);
CREATE INDEX idx_posts_date ON social_media_posts(posted_at);
```

## API Endpoints

### Social Media Accounts
```
GET    /api/social-accounts                    # List all accounts
GET    /api/social-accounts/{id}               # Get account details
POST   /api/social-accounts                    # Create account
PUT    /api/social-accounts/{id}               # Update account
DELETE /api/social-accounts/{id}               # Delete account

GET    /api/offices/{id}/social-accounts       # Office social accounts
GET    /api/employees/{id}/social-accounts     # Employee social accounts
GET    /api/social-accounts/featured           # Featured broker accounts
```

### Metrics & Analytics
```
GET    /api/social-accounts/{id}/metrics       # Get metrics for account
GET    /api/social-accounts/{id}/metrics/summary  # Summary stats
GET    /api/social-accounts/{id}/posts         # Recent posts
GET    /api/social-accounts/{id}/top-posts     # Top performing posts
POST   /api/social-accounts/{id}/sync          # Trigger sync from platform
```

### Aggregated Analytics
```
GET    /api/analytics/social-overview          # All offices combined
GET    /api/analytics/social-by-office         # Grouped by office
GET    /api/analytics/social-growth            # Growth trends
GET    /api/analytics/top-performers           # Best performing accounts
```

## UI Components

### 1. Office Detail Page - Social Media Section

```
┌─────────────────────────────────────────────────────────┐
│ Social Media & Online Presence                          │
├─────────────────────────────────────────────────────────┤
│                                                          │
│ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐    │
│ │  Instagram   │ │  Facebook    │ │ Google Maps  │    │
│ │  @stavanger  │ │  Proaktiv    │ │  ★★★★★ 4.8  │    │
│ │  2.4K ↑ 5%   │ │  3.1K ↑ 3%   │ │  127 reviews │    │
│ └──────────────┘ └──────────────┘ └──────────────┘    │
│                                                          │
│ Recent Posts                                            │
│ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐          │
│ │ [img]  │ │ [img]  │ │ [img]  │ │ [img]  │          │
│ │ ❤ 234  │ │ ❤ 189  │ │ ❤ 156  │ │ ❤ 142  │          │
│ └────────┘ └────────┘ └────────┘ └────────┘          │
│                                                          │
│ Key Brokers on Instagram                                │
│ ┌────────────────┐ ┌────────────────┐                 │
│ │ @johndoe       │ │ @janedoe       │                 │
│ │ 1.2K followers │ │ 980 followers  │                 │
│ │ ⚡ Active      │ │ ⚡ Active      │                 │
│ └────────────────┘ └────────────────┘                 │
└─────────────────────────────────────────────────────────┘
```

### 2. Social Media Dashboard Page

```
┌─────────────────────────────────────────────────────────┐
│ Social Media Overview                                    │
├─────────────────────────────────────────────────────────┤
│                                                          │
│ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐    │
│ │ Total        │ │ Avg Engage   │ │ Total Reach  │    │
│ │ Followers    │ │ Rate         │ │              │    │
│ │ 24,567 ↑ 4%  │ │ 3.2% ↑ 0.3%  │ │ 156K ↑ 12%   │    │
│ └──────────────┘ └──────────────┘ └──────────────┘    │
│                                                          │
│ Performance by Office                                   │
│ ┌─────────────────────────────────────────────────────┐│
│ │ Office         Instagram  Facebook  Google  Total   ││
│ │ Stavanger      2.4K ↑     3.1K ↑    4.8★   High    ││
│ │ Sandnes        1.8K ↑     2.3K →    4.6★   Medium  ││
│ │ Bergen         3.2K ↑     4.5K ↑    4.9★   High    ││
│ └─────────────────────────────────────────────────────┘│
│                                                          │
│ Top Performing Posts (Last 30 Days)                     │
│ ┌────────────────────────────────────────────────────┐ │
│ │ [thumbnail] "Nytt salg i Stavanger sentrum!"       │ │
│ │ @stavanger • Instagram • 456 likes • 23 comments   │ │
│ └────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

### 3. Component Structure

```
frontend/src/components/social-media/
├── SocialMediaCard.tsx           # Individual account card
├── SocialMediaFeed.tsx            # Posts grid/feed
├── SocialMetricsWidget.tsx        # Metrics display
├── InstagramEmbed.tsx             # Instagram post embed
├── FacebookEmbed.tsx              # Facebook post embed
├── GoogleBusinessCard.tsx         # Google Business widget
├── SocialMediaDashboard.tsx       # Full dashboard
├── TrendIndicator.tsx             # ↑ ↓ growth arrows
└── EngagementChart.tsx            # Line/bar charts
```

## Implementation Plan

### Phase 1: Database & Basic UI
1. **Create database migrations**
   - `social_media_accounts` table
   - `social_media_metrics` table
   - `social_media_posts` table

2. **Seed initial data**
   - Add existing social media URLs from offices
   - Mark featured brokers
   - Set `use_for_marketing` flags

3. **Build basic UI components**
   - Social media cards on office pages
   - Link to external profiles
   - Display follower counts (manual entry initially)

### Phase 2: API Integration
1. **Instagram Business API**
   - OAuth flow for authentication
   - Fetch account insights
   - Fetch recent posts
   - Store metrics in database

2. **Facebook Graph API**
   - OAuth flow for authentication
   - Fetch page insights
   - Fetch recent posts
   - Store metrics in database

3. **Google My Business API**
   - OAuth flow for authentication
   - Fetch location insights
   - Fetch reviews and ratings
   - Store metrics in database

### Phase 3: Analytics & Metrics
1. **Metrics collection service**
   - Background job to sync daily
   - Store historical data
   - Calculate growth rates
   - Identify trends

2. **Analytics dashboard**
   - Aggregate metrics across offices
   - Compare performance
   - Top performers
   - Growth charts

### Phase 4: Advanced Features
1. **Post scheduling** (future)
2. **Sentiment analysis** on comments/reviews
3. **Competitor tracking**
4. **Automated reporting**

## API Authentication & Setup

### Instagram Business API
```python
# Required: Facebook Business account + Instagram Business account
# Setup:
# 1. Create Facebook App
# 2. Add Instagram Graph API
# 3. Get Page Access Token
# 4. Exchange for long-lived token

# Example request:
GET https://graph.facebook.com/v18.0/{instagram-account-id}
  ?fields=followers_count,media_count,username
  &access_token={access-token}
```

### Facebook Graph API
```python
# Required: Facebook Page
# Setup:
# 1. Create Facebook App
# 2. Add Pages API
# 3. Get Page Access Token

# Example request:
GET https://graph.facebook.com/v18.0/{page-id}
  ?fields=fan_count,engagement,posts{message,likes.summary(true)}
  &access_token={access-token}
```

### Google My Business API
```python
# Required: Google Business Profile
# Setup:
# 1. Enable Google Business Profile API
# 2. Create OAuth 2.0 credentials
# 3. Get user consent

# Example request:
GET https://mybusinessbusinessinformation.googleapis.com/v1/accounts/{account-id}/locations
  Authorization: Bearer {access-token}
```

## Data Sync Strategy

### Sync Frequency
- **Metrics**: Daily (overnight)
- **Posts**: Every 6 hours
- **Reviews**: Every hour (Google Business)
- **Manual sync**: On-demand via UI button

### Sync Service
```python
# backend/app/services/social_sync_service.py

class SocialSyncService:
    async def sync_instagram_account(account_id: UUID):
        # Fetch latest metrics
        # Fetch recent posts
        # Calculate engagement rates
        # Store in database
        
    async def sync_facebook_account(account_id: UUID):
        # Similar to Instagram
        
    async def sync_google_business(account_id: UUID):
        # Fetch reviews
        # Fetch insights
        # Calculate response metrics
        
    async def sync_all_accounts():
        # Background job (Celery/APScheduler)
        # Sync all active accounts
```

## Privacy & Security

### API Token Storage
- **Encrypt tokens** at rest (using `cryptography` library)
- **Store in environment variables** or secure vault
- **Rotate tokens** regularly
- **Revoke on account deletion**

### Data Access
- **Admin only** can view all metrics
- **Office managers** can view their office metrics
- **Brokers** can view their own metrics
- **Public data** only (no private messages/DMs)

## Acceptance Criteria

### Phase 1 (Basic UI)
- [ ] Social media accounts table created
- [ ] Office pages display social media links
- [ ] Featured brokers section on office pages
- [ ] Manual follower count entry working

### Phase 2 (API Integration)
- [ ] Instagram API connected and syncing
- [ ] Facebook API connected and syncing
- [ ] Google Business API connected and syncing
- [ ] Metrics stored in database

### Phase 3 (Analytics)
- [ ] Dashboard shows aggregate metrics
- [ ] Growth trends calculated and displayed
- [ ] Top performing posts identified
- [ ] Engagement rates calculated

### Phase 4 (Polish)
- [ ] Embedded posts display correctly
- [ ] Real-time sync button works
- [ ] Charts and graphs render smoothly
- [ ] Mobile responsive design

## Future Enhancements
- [ ] LinkedIn Company Pages integration
- [ ] TikTok Business API (when available)
- [ ] YouTube channel metrics
- [ ] Automated social media reports (PDF/email)
- [ ] Alerts for negative reviews
- [ ] Competitor benchmarking
- [ ] AI-powered content suggestions
- [ ] Social media calendar/scheduling

## Resources
- **Instagram Graph API**: https://developers.facebook.com/docs/instagram-api
- **Facebook Graph API**: https://developers.facebook.com/docs/graph-api
- **Google Business Profile API**: https://developers.google.com/my-business
- **OAuth 2.0**: https://oauth.net/2/
- **React Social Media Embeds**: https://www.npmjs.com/package/react-social-media-embed

## Cost Considerations
- **Instagram/Facebook API**: Free (with rate limits)
- **Google My Business API**: Free (with quotas)
- **Token storage**: Minimal (database storage)
- **Sync jobs**: Minimal (background processing)

## Implementation Priority
1. **High**: Database schema and basic UI (Phase 1)
2. **High**: Instagram and Google Business integration (Phase 2)
3. **Medium**: Facebook integration (Phase 2)
4. **Medium**: Analytics dashboard (Phase 3)
5. **Low**: Advanced features (Phase 4)
