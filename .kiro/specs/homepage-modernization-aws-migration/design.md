# Design Document

## Overview

This design document outlines the technical approach for modernizing the Geoglypha homepage and migrating the website from Google Cloud Platform to Amazon Web Services. The project will maintain the existing content structure while improving visual design, user experience, and hosting infrastructure.

The modernization will focus on:
- Enhanced visual design with improved typography, spacing, and modern UI patterns
- Better mobile responsiveness and accessibility
- Optimized asset loading and performance
- Complete migration to AWS infrastructure (S3, CloudFront, Route 53)
- Automated deployment pipeline

## Architecture

### Current Architecture
- Static HTML/CSS/JavaScript website
- Hosted on Google Cloud Storage
- Assets served from `storage.googleapis.com/geoglypha1/`
- Multiple project pages: Cahokia (Leaflet map), Cuneiform translator, Stonehenge 3D model
- External dependencies: Leaflet.js, Three.js

### Target Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         User Browser                         │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ HTTPS
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    CloudFront CDN                            │
│  - SSL/TLS Termination                                       │
│  - Edge Caching                                              │
│  - Gzip Compression                                          │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    S3 Static Website                         │
│  Bucket: geoglypha-website                                   │
│  - index.html (homepage)                                     │
│  - cahokia.html, cuneiform.html, stonehenge.html            │
│  - /assets/css/                                              │
│  - /assets/js/                                               │
│  - /assets/images/                                           │
│  - /data/ (GeoJSON files)                                    │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    Route 53 (Optional)                       │
│  - DNS Management                                            │
│  - Custom Domain Configuration                               │
└─────────────────────────────────────────────────────────────┘
```

### Deployment Pipeline

```
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│   Local      │      │   AWS CLI    │      │   S3 Bucket  │
│   Changes    │─────▶│   Sync       │─────▶│   Upload     │
└──────────────┘      └──────────────┘      └──────────────┘
                                                     │
                                                     ▼
                                            ┌──────────────┐
                                            │  CloudFront  │
                                            │  Invalidation│
                                            └──────────────┘
```

## Components and Interfaces

### 1. Homepage Modernization

#### Visual Design System

**Color Palette** (Enhanced from existing):
```css
:root {
    --primary-color: #2d5a4a;        /* Darker, richer green */
    --primary-light: #3a6351;        /* Original primary */
    --primary-dark: #1f3d33;         /* Deeper shade */
    
    --secondary-color: #f2edd7;      /* Warm off-white */
    --secondary-light: #faf8f0;      /* Lighter variant */
    
    --accent-color: #a0937d;         /* Muted gold */
    --accent-hover: #8a7b69;         /* Darker on hover */
    
    --text-primary: #1a202c;         /* Near black */
    --text-secondary: #4a5568;       /* Medium gray */
    --text-light: #f5f5f5;           /* Light text */
    
    --border-color: #e2e8f0;         /* Subtle borders */
    --shadow-sm: 0 2px 4px rgba(0,0,0,0.1);
    --shadow-md: 0 4px 8px rgba(0,0,0,0.12);
    --shadow-lg: 0 8px 16px rgba(0,0,0,0.15);
}
```

**Typography System**:
```css
/* Font Stack */
--font-display: 'Playfair Display', Georgia, serif;  /* Headers */
--font-body: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
--font-mono: 'Fira Code', 'Courier New', monospace;

/* Type Scale */
--text-xs: 0.75rem;    /* 12px */
--text-sm: 0.875rem;   /* 14px */
--text-base: 1rem;     /* 16px */
--text-lg: 1.125rem;   /* 18px */
--text-xl: 1.25rem;    /* 20px */
--text-2xl: 1.5rem;    /* 24px */
--text-3xl: 1.875rem;  /* 30px */
--text-4xl: 2.25rem;   /* 36px */
--text-5xl: 3rem;      /* 48px */
```

**Spacing System**:
```css
--space-1: 0.25rem;   /* 4px */
--space-2: 0.5rem;    /* 8px */
--space-3: 0.75rem;   /* 12px */
--space-4: 1rem;      /* 16px */
--space-6: 1.5rem;    /* 24px */
--space-8: 2rem;      /* 32px */
--space-12: 3rem;     /* 48px */
--space-16: 4rem;     /* 64px */
--space-24: 6rem;     /* 96px */
```

#### Component Improvements

**Navigation Bar**:
- Sticky header with subtle shadow on scroll
- Smooth scroll behavior for anchor links
- Mobile hamburger menu with slide-in animation
- Active page indicator
- Search functionality (future enhancement)

**Hero Section**:
- Full-width background image with parallax effect
- Gradient overlay for text readability
- Animated entrance for heading and CTA
- Optimized image loading (WebP with fallback)

**Project Cards**:
- Consistent card design with hover effects
- Image lazy loading
- Skeleton loading states
- Tag system for categorization
- "Coming Soon" badge for future projects

**Gallery Section**:
- Masonry grid layout for varied image sizes
- Lightbox modal for full-size viewing
- Image optimization and responsive srcset
- Smooth transitions and animations

**Footer**:
- Multi-column layout with sitemap
- Social media links
- Newsletter signup (future enhancement)
- Copyright and legal links

### 2. AWS Infrastructure Components

#### S3 Bucket Configuration

**Bucket Structure**:
```
geoglypha-website/
├── index.html
├── cahokia.html
├── cuneiform.html
├── stonehenge.html
├── geoglyph_visualization.html
├── 404.html
├── assets/
│   ├── css/
│   │   ├── main.css
│   │   ├── cunestyles.css
│   │   └── normalize.css
│   ├── js/
│   │   ├── main.js
│   │   ├── cunescript.js
│   │   └── cuneiform_library.py (if needed)
│   └── images/
│       ├── hero/
│       ├── projects/
│       ├── gallery/
│       └── icons/
├── data/
│   ├── cahokiaboundary.geojson
│   ├── cmounds.geojson
│   ├── Mounds.geojson
│   └── amazon_geoglyphs.xls
└── graphita/
    ├── graphitia.html
    ├── styles.css
    └── images/
```

**Bucket Policy** (Public Read Access):
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::geoglypha-website/*"
    }
  ]
}
```

**Static Website Hosting Configuration**:
- Index document: `index.html`
- Error document: `404.html`
- Redirect rules for old GCS URLs (if needed)

#### CloudFront Distribution

**Configuration**:
- Origin: GCS bucket website endpoint
- Viewer Protocol Policy: Redirect HTTP to HTTPS
- Allowed HTTP Methods: GET, HEAD, OPTIONS
- Compress Objects Automatically: Yes
- Price Class: Use All Edge Locations (or optimize based on audience)

**Cache Behaviors**:
```
Path Pattern: *.html
- Min TTL: 0
- Max TTL: 86400 (1 day)
- Default TTL: 3600 (1 hour)

Path Pattern: /assets/*
- Min TTL: 86400 (1 day)
- Max TTL: 31536000 (1 year)
- Default TTL: 604800 (1 week)

Path Pattern: /data/*
- Min TTL: 3600 (1 hour)
- Max TTL: 86400 (1 day)
- Default TTL: 3600 (1 hour)
```

**Custom Error Responses**:
- 404: Return 404.html with 404 status code
- 403: Return 404.html with 404 status code

#### Route 53 (Optional)

**DNS Configuration** (if custom domain):
- A Record (Alias): Points to CloudFront distribution
- AAAA Record (Alias): IPv6 support
- CNAME for www subdomain

### 3. Asset Migration Strategy

#### Image Migration Process

1. **Inventory Current Assets**:
   - Scan all HTML files for GCS URLs
   - Create manifest of all images and their locations
   - Document image dimensions and formats

2. **Optimization Pipeline**:
   - Convert images to WebP format (with JPEG/PNG fallback)
   - Generate responsive image sizes (thumbnail, medium, large)
   - Compress images without quality loss
   - Add alt text for accessibility

3. **Upload to S3**:
   - Maintain original file structure
   - Set appropriate Content-Type headers
   - Configure Cache-Control headers
   - Enable S3 Transfer Acceleration for faster uploads

4. **Update References**:
   - Replace all `storage.googleapis.com/geoglypha1/` URLs
   - Use relative paths where possible
   - Update to CloudFront URLs for external references

#### URL Migration Mapping

```
Old: https://storage.googleapis.com/geoglypha1/index.html
New: https://d1234567890.cloudfront.net/index.html
     or https://www.geoglypha.com/

Old: https://storage.googleapis.com/geoglypha1/images/cahokia_woodhenge.jpg
New: /assets/images/projects/cahokia_woodhenge.jpg

Old: https://storage.googleapis.com/geoglypha1/graphita/graphitia.html
New: /graphita/graphitia.html
```

### 4. Deployment Automation

#### PowerShell Deployment Script

**Features**:
- Sync local files to S3 bucket
- Only upload changed files (checksum comparison)
- Set appropriate Content-Type and Cache-Control headers
- Invalidate CloudFront cache for updated files
- Dry-run mode for testing
- Colored output for success/error messages

**Script Structure**:
```powershell
# deploy.ps1
param(
    [switch]$DryRun,
    [switch]$Force,
    [string]$Profile = "default"
)

# Configuration
$BucketName = "geoglypha-website"
$CloudFrontDistributionId = "E1234567890ABC"
$LocalPath = "."

# Functions
function Sync-ToS3 { }
function Invalidate-CloudFront { }
function Set-ContentTypes { }

# Main execution
```

#### GitHub Actions Workflow (Future Enhancement)

```yaml
name: Deploy to AWS
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v1
      - name: Sync to S3
        run: aws s3 sync . s3://geoglypha-website --delete
      - name: Invalidate CloudFront
        run: aws cloudfront create-invalidation --distribution-id ${{ secrets.CLOUDFRONT_ID }} --paths "/*"
```

## Data Models

### Project Card Data Structure

```javascript
{
  id: "cahokia-mounds",
  title: "Cahokia Mounds",
  description: "Interactive mapping of North America's largest pre-Columbian city.",
  thumbnail: "/assets/images/projects/cahokia_woodhenge.jpg",
  link: "/cahokia.html",
  tags: ["archaeology", "maps", "north-america"],
  status: "active", // active | coming-soon | archived
  featured: true,
  order: 1
}
```

### Image Asset Metadata

```javascript
{
  originalPath: "https://storage.googleapis.com/geoglypha1/images/cahokia_woodhenge.jpg",
  newPath: "/assets/images/projects/cahokia_woodhenge.jpg",
  s3Key: "assets/images/projects/cahokia_woodhenge.jpg",
  formats: {
    webp: "/assets/images/projects/cahokia_woodhenge.webp",
    jpeg: "/assets/images/projects/cahokia_woodhenge.jpg"
  },
  sizes: {
    thumbnail: { width: 400, height: 300 },
    medium: { width: 800, height: 600 },
    large: { width: 1600, height: 1200 }
  },
  altText: "Cahokia Woodhenge reconstruction showing wooden posts in circular formation",
  migrated: true,
  migratedDate: "2025-12-07"
}
```

## Error Handling

### Client-Side Error Handling

**Image Loading Failures**:
```javascript
// Fallback for WebP images
<picture>
  <source srcset="image.webp" type="image/webp">
  <img src="image.jpg" alt="Description" onerror="this.src='/assets/images/placeholder.jpg'">
</picture>
```

**GeoJSON Loading Failures**:
```javascript
fetch('data/cahokiaboundary.geojson')
  .then(response => {
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return response.json();
  })
  .catch(error => {
    console.error('Error loading GeoJSON:', error);
    // Display user-friendly error message
    showErrorMessage('Unable to load map data. Please refresh the page.');
  });
```

**External Library Loading**:
```javascript
// Leaflet.js fallback
if (typeof L === 'undefined') {
  console.error('Leaflet library failed to load');
  document.getElementById('map').innerHTML = 
    '<p>Map functionality is currently unavailable. Please try again later.</p>';
}
```

### Server-Side Error Handling

**S3 Bucket Errors**:
- 403 Forbidden: Check bucket policy and IAM permissions
- 404 Not Found: Serve custom 404.html page
- 503 Service Unavailable: CloudFront will retry from origin

**CloudFront Errors**:
- Custom error pages for 4xx and 5xx errors
- Automatic retry logic for transient failures
- Monitoring and alerting via CloudWatch

## Testing Strategy

### 1. Visual Regression Testing

**Tools**: Percy, BackstopJS, or manual screenshot comparison

**Test Cases**:
- Homepage renders correctly on desktop (1920x1080, 1366x768)
- Homepage renders correctly on tablet (768x1024)
- Homepage renders correctly on mobile (375x667, 414x896)
- All project cards display properly
- Navigation menu works on all screen sizes
- Footer layout is correct

### 2. Functional Testing

**Manual Testing Checklist**:
- [ ] All internal links work correctly
- [ ] All external links open in new tabs
- [ ] Contact form validation works (if implemented)
- [ ] Mobile menu opens and closes
- [ ] Smooth scroll to anchor links
- [ ] Image lazy loading works
- [ ] Cahokia map loads and displays GeoJSON data
- [ ] Cuneiform translator functions correctly
- [ ] Stonehenge 3D model renders and is interactive
- [ ] Gallery lightbox opens and navigates

### 3. Performance Testing

**Metrics to Measure**:
- First Contentful Paint (FCP): < 1.5s
- Largest Contentful Paint (LCP): < 2.5s
- Time to Interactive (TTI): < 3.5s
- Cumulative Layout Shift (CLS): < 0.1
- Total page size: < 2MB (initial load)

**Tools**:
- Lighthouse (Chrome DevTools)
- WebPageTest
- GTmetrix

**Optimization Targets**:
- Enable Gzip/Brotli compression
- Minify CSS and JavaScript
- Optimize images (WebP, responsive sizes)
- Implement lazy loading for images
- Use CDN (CloudFront) for all assets
- Leverage browser caching

### 4. Accessibility Testing

**WCAG 2.1 Level AA Compliance**:
- [ ] All images have alt text
- [ ] Color contrast ratios meet minimum standards (4.5:1 for normal text)
- [ ] Keyboard navigation works for all interactive elements
- [ ] Focus indicators are visible
- [ ] Semantic HTML is used (headings, landmarks, lists)
- [ ] Forms have proper labels
- [ ] No content flashes more than 3 times per second

**Tools**:
- axe DevTools
- WAVE Browser Extension
- Lighthouse Accessibility Audit

### 5. Cross-Browser Testing

**Browsers to Test**:
- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)
- Mobile Safari (iOS)
- Chrome Mobile (Android)

**Test Cases**:
- CSS Grid and Flexbox layouts
- CSS custom properties (variables)
- JavaScript ES6+ features
- WebP image support with fallbacks
- Three.js 3D rendering (Stonehenge)
- Leaflet.js map functionality

### 6. AWS Infrastructure Testing

**S3 Testing**:
- [ ] Bucket policy allows public read access
- [ ] Static website hosting is enabled
- [ ] Index and error documents are configured
- [ ] All files uploaded successfully
- [ ] Content-Type headers are correct
- [ ] Cache-Control headers are set appropriately

**CloudFront Testing**:
- [ ] Distribution is deployed and active
- [ ] HTTPS works correctly
- [ ] HTTP redirects to HTTPS
- [ ] Caching behavior is correct for different file types
- [ ] Custom error pages display properly
- [ ] Gzip compression is enabled

**Deployment Script Testing**:
- [ ] Dry-run mode works without uploading
- [ ] Only changed files are uploaded
- [ ] CloudFront invalidation is triggered
- [ ] Error handling works for AWS API failures
- [ ] Progress output is clear and informative

### 7. Migration Validation

**Asset Migration Checklist**:
- [ ] All images migrated from GCS to S3
- [ ] All GCS URLs updated to new paths
- [ ] Image quality maintained after optimization
- [ ] No broken image links
- [ ] GeoJSON files accessible
- [ ] External library CDN links still work

**URL Testing**:
- Create a script to crawl all pages and check for:
  - Broken links (404 errors)
  - Mixed content warnings (HTTP resources on HTTPS pages)
  - Old GCS URLs that weren't updated
  - Slow-loading resources

## Design Decisions and Rationales

### 1. Why AWS over Google Cloud?

**Cost Efficiency**:
- S3 + CloudFront typically cheaper for static sites than GCS
- AWS Free Tier includes 50GB data transfer out per month
- More predictable pricing structure

**Feature Set**:
- CloudFront has more edge locations globally
- Better integration with other AWS services (Route 53, Certificate Manager)
- More mature tooling and documentation

**Flexibility**:
- Easier to add serverless functions (Lambda@Edge) in the future
- Better support for custom domains and SSL certificates
- More granular caching controls

### 2. Why Static Site over Dynamic Framework?

**Current Needs**:
- Content is primarily static (educational resources, maps, tools)
- No user authentication or database requirements
- Simple content updates don't require a CMS

**Performance**:
- Static sites load faster (no server-side rendering)
- Better caching at CDN edge locations
- Lower latency for global users

**Cost**:
- No server costs (only storage and bandwidth)
- Scales automatically without infrastructure management
- Minimal maintenance overhead

**Future Flexibility**:
- Can add dynamic features via JavaScript and APIs
- Can integrate serverless functions for specific features
- Easy to migrate to a framework later if needed

### 3. Design System Approach

**Consistency**:
- CSS custom properties ensure consistent colors and spacing
- Reusable component patterns reduce code duplication
- Easier to maintain and update design across all pages

**Scalability**:
- New pages can use existing design tokens
- Component library can grow organically
- Design changes propagate automatically

**Developer Experience**:
- Clear naming conventions make code self-documenting
- Easier for collaborators to understand and contribute
- Reduces decision fatigue when building new features

### 4. Image Optimization Strategy

**WebP with Fallbacks**:
- WebP provides 25-35% better compression than JPEG
- Fallback ensures compatibility with older browsers
- Progressive enhancement approach

**Responsive Images**:
- Serve appropriately sized images for different devices
- Reduces bandwidth usage on mobile
- Improves page load times

**Lazy Loading**:
- Only load images as they enter viewport
- Reduces initial page load time
- Better user experience on slow connections

### 5. Deployment Automation

**PowerShell Script**:
- Native to Windows environment (user's system)
- No additional dependencies required
- Can be run manually or integrated into CI/CD

**Incremental Uploads**:
- Only upload changed files (faster deployments)
- Reduces bandwidth usage
- Minimizes CloudFront invalidation costs

**CloudFront Invalidation**:
- Ensures users see updated content immediately
- Targeted invalidation (only changed paths)
- Balances freshness with cost

## Database Integration Architecture (Future)

### RDS Integration for Dynamic Content

The architecture is designed to accommodate future database-driven features while maintaining the current static site performance. This hybrid approach allows specific projects to leverage RDS while keeping the core site static.

#### Hybrid Architecture Pattern

```
┌─────────────────────────────────────────────────────────────┐
│                         User Browser                         │
└────────────────┬───────────────────────┬────────────────────┘
                 │                       │
                 │ Static Content        │ Dynamic Content
                 ▼                       ▼
┌────────────────────────────┐  ┌──────────────────────────┐
│   CloudFront CDN           │  │   API Gateway            │
│   (Static Assets)          │  │   (REST/GraphQL API)     │
└────────────────────────────┘  └──────────┬───────────────┘
                 │                          │
                 ▼                          ▼
┌────────────────────────────┐  ┌──────────────────────────┐
│   S3 Static Website        │  │   Lambda Functions       │
│   - HTML/CSS/JS            │  │   - Query handlers       │
│   - Images                 │  │   - Business logic       │
└────────────────────────────┘  └──────────┬───────────────┘
                                            │
                                            ▼
                                   ┌──────────────────────────┐
                                   │   Amazon RDS             │
                                   │   (PostgreSQL/MySQL)     │
                                   │   - I Ching data         │
                                   │   - Ceremonial magic     │
                                   │   - Map metadata         │
                                   │   - User interactions    │
                                   └──────────────────────────┘
```

#### RDS Database Schema Planning

**I Ching Project Database**:
```sql
-- Hexagrams table
CREATE TABLE hexagrams (
    id SERIAL PRIMARY KEY,
    number INTEGER UNIQUE NOT NULL,
    name_chinese VARCHAR(50),
    name_english VARCHAR(100),
    binary_sequence VARCHAR(6),
    trigram_above VARCHAR(50),
    trigram_below VARCHAR(50),
    judgment TEXT,
    image TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Lines table (changing lines)
CREATE TABLE hexagram_lines (
    id SERIAL PRIMARY KEY,
    hexagram_id INTEGER REFERENCES hexagrams(id),
    line_position INTEGER CHECK (line_position BETWEEN 1 AND 6),
    line_text TEXT,
    is_changing BOOLEAN DEFAULT FALSE
);

-- Readings/Castings table (user interactions)
CREATE TABLE readings (
    id SERIAL PRIMARY KEY,
    hexagram_id INTEGER REFERENCES hexagrams(id),
    changing_lines INTEGER[],
    resulting_hexagram_id INTEGER REFERENCES hexagrams(id),
    reading_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    session_id VARCHAR(100),
    notes TEXT
);
```

**Ceremonial Magic Database**:
```sql
-- Rituals/Practices table
CREATE TABLE rituals (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200),
    tradition VARCHAR(100),
    description TEXT,
    instructions TEXT,
    difficulty_level VARCHAR(50),
    duration_minutes INTEGER,
    required_items TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Symbols/Sigils table
CREATE TABLE symbols (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200),
    tradition VARCHAR(100),
    image_url VARCHAR(500),
    meaning TEXT,
    usage_context TEXT,
    related_rituals INTEGER[] -- Array of ritual IDs
);

-- Correspondences table (planets, elements, etc.)
CREATE TABLE correspondences (
    id SERIAL PRIMARY KEY,
    category VARCHAR(100), -- 'planet', 'element', 'zodiac', etc.
    name VARCHAR(100),
    properties JSONB, -- Flexible structure for various attributes
    associations TEXT[]
);
```

**Enhanced Map Data (Geospatial with Metadata)**:
```sql
-- Sites table (archaeological/historical sites)
CREATE TABLE sites (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200),
    site_type VARCHAR(100), -- 'mound', 'temple', 'geoglyph', etc.
    location GEOGRAPHY(POINT, 4326), -- PostGIS extension
    description TEXT,
    culture VARCHAR(100),
    time_period VARCHAR(100),
    excavation_status VARCHAR(50),
    images TEXT[],
    geojson_data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Site metadata and research
CREATE TABLE site_research (
    id SERIAL PRIMARY KEY,
    site_id INTEGER REFERENCES sites(id),
    research_date DATE,
    findings TEXT,
    researchers TEXT[],
    references TEXT[]
);
```

#### API Layer Design

**Lambda Functions** (Node.js/Python):

```javascript
// Example: I Ching hexagram query
// Lambda: getHexagram
exports.handler = async (event) => {
    const { hexagramNumber } = JSON.parse(event.body);
    
    // Query RDS via connection pool
    const hexagram = await db.query(
        'SELECT * FROM hexagrams WHERE number = $1',
        [hexagramNumber]
    );
    
    const lines = await db.query(
        'SELECT * FROM hexagram_lines WHERE hexagram_id = $1 ORDER BY line_position',
        [hexagram.id]
    );
    
    return {
        statusCode: 200,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ hexagram, lines })
    };
};
```

**API Gateway Endpoints**:
```
GET  /api/hexagrams/{number}           - Get specific hexagram
POST /api/readings                     - Create new reading
GET  /api/rituals                      - List rituals (with filters)
GET  /api/rituals/{id}                 - Get specific ritual
GET  /api/sites                        - Get sites (with geospatial query)
GET  /api/sites/{id}                   - Get specific site details
POST /api/sites/{id}/visit             - Log site visit/interaction
```

#### RDS Configuration

**Instance Specifications** (Start small, scale as needed):
- Instance Class: db.t3.micro or db.t4g.micro (Free Tier eligible)
- Engine: PostgreSQL 15+ (with PostGIS for geospatial data)
- Storage: 20GB General Purpose SSD (gp3)
- Multi-AZ: No (initially), Yes (production)
- Backup Retention: 7 days

**Security Configuration**:
- VPC: Private subnet (not publicly accessible)
- Security Group: Only allow Lambda functions in same VPC
- Encryption: At rest (KMS) and in transit (SSL/TLS)
- IAM Database Authentication: Enabled for Lambda access

**Connection Pooling**:
- Use RDS Proxy to manage database connections from Lambda
- Prevents connection exhaustion
- Improves cold start performance

#### Frontend Integration Pattern

**Static Site + Dynamic Data**:
```javascript
// Example: Loading I Ching hexagram on static page
async function loadHexagram(number) {
    try {
        const response = await fetch(
            `https://api.geoglypha.com/hexagrams/${number}`
        );
        const data = await response.json();
        
        // Render hexagram data on static page
        renderHexagram(data);
    } catch (error) {
        console.error('Failed to load hexagram:', error);
        // Fallback to static content if available
    }
}
```

**Progressive Enhancement**:
- Static pages load immediately with basic content
- JavaScript fetches dynamic data from API
- Graceful degradation if API is unavailable
- Cache API responses in browser (IndexedDB/LocalStorage)

#### Cost Optimization Strategy

**RDS Costs**:
- Start with db.t3.micro (Free Tier: 750 hours/month for 12 months)
- Use Reserved Instances for predictable workloads (up to 60% savings)
- Enable automated backups to S3 (cheaper than snapshots)
- Monitor with CloudWatch and set up billing alerts

**Lambda Costs**:
- Free Tier: 1M requests/month, 400,000 GB-seconds compute
- Optimize function memory allocation (right-sizing)
- Use Lambda Provisioned Concurrency only if needed
- Consider Lambda@Edge for geographically distributed users

**Data Transfer Costs**:
- Keep Lambda and RDS in same VPC/AZ (no data transfer charges)
- Use CloudFront to cache API responses where appropriate
- Compress API responses (gzip)

#### Migration Path for Existing Projects

**Ceremonial Magic Site**:
1. Keep current static HTML as base
2. Add ritual database with detailed instructions
3. Create interactive ritual builder/planner
4. Add user notes/journal feature (optional authentication)
5. Implement correspondence lookup tool

**Enhanced Webmaps**:
1. Migrate GeoJSON data to PostGIS (RDS)
2. Add dynamic filtering and search
3. Enable user contributions (with moderation)
4. Add temporal data (show site changes over time)
5. Implement heatmaps and clustering for large datasets

**I Ching Site** (New Project):
1. Build hexagram database from classical texts
2. Create casting interface (virtual coins/yarrow stalks)
3. Implement reading interpretation engine
4. Add reading history and journal
5. Include commentary from multiple traditions

#### Development Workflow

**Local Development**:
```bash
# Use Docker for local RDS simulation
docker run --name geoglypha-postgres \
  -e POSTGRES_PASSWORD=localdev \
  -p 5432:5432 \
  -d postgis/postgis:15-3.3

# Run Lambda functions locally with SAM CLI
sam local start-api --docker-network geoglypha-network
```

**Database Migrations**:
- Use Flyway or Liquibase for version-controlled schema changes
- Store migration scripts in version control
- Automated migrations in CI/CD pipeline

**Testing Strategy**:
- Unit tests for Lambda functions
- Integration tests with test database
- Load testing for API endpoints
- Geospatial query performance testing

## Future Enhancements

### Phase 2 Features (Post-MVP)

1. **Database-Driven Content** (Priority):
   - Amazon RDS (PostgreSQL with PostGIS)
   - Lambda functions for API layer
   - API Gateway for RESTful endpoints
   - I Ching hexagram database and casting interface
   - Ceremonial magic ritual database
   - Enhanced map data with metadata

2. **Content Management**:
   - Headless CMS integration (Contentful, Sanity)
   - Admin interface for non-technical updates
   - Version control for content changes

3. **Interactive Features**:
   - User comments on projects
   - Newsletter subscription
   - Contact form with email integration (SES)
   - User reading journals (I Ching)
   - Ritual planning tools

4. **Advanced Mapping**:
   - PostGIS-powered geospatial queries
   - Dynamic filtering and search
   - Custom map tiles
   - 3D terrain visualization
   - Time-series data visualization
   - User-contributed site data

5. **Search Functionality**:
   - Full-text search across all content
   - Algolia or AWS CloudSearch integration
   - Autocomplete suggestions
   - Geospatial search (find sites near location)

6. **Analytics and Monitoring**:
   - Google Analytics or AWS Pinpoint
   - Real User Monitoring (RUM)
   - Error tracking (Sentry)
   - RDS Performance Insights
   - API Gateway metrics

7. **Progressive Web App (PWA)**:
   - Service worker for offline access
   - App manifest for "Add to Home Screen"
   - Push notifications for new content
   - Offline I Ching readings

8. **Internationalization**:
   - Multi-language support
   - Localized content
   - Language switcher in navigation
   - I Ching translations (Chinese, English, etc.)

9. **Performance Optimizations**:
   - HTTP/3 support
   - Preloading critical resources
   - Code splitting for JavaScript
   - CSS-in-JS for component-scoped styles
   - RDS read replicas for scaling
   - ElastiCache for API response caching
