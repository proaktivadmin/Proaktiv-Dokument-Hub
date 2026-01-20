# Territory Heat Map Feature

## Overview
Implement an interactive vector-based map of Norway showing office locations and their market areas (postal code assignments) with a clean, modern design that matches the application's aesthetic.

## User Story
As an admin, I want to see a visual map of Norway with office locations and their assigned postal code territories, so I can understand market coverage and identify gaps or overlaps.

## Design Requirements

### Map Style
- **Vector-based** (not realistic/satellite imagery)
- **Clean, minimal design** matching the app's color scheme
- **Large enough** to clearly see locations and areas
- **County borders** (fylkesgrenser) clearly marked
- **Responsive** - works on desktop and tablet

### Color Scheme
- Background: `#FAFAF7` (matches current design)
- County borders: `#E5E5E5` (light gray)
- Office markers: Use office `color` field from database
- Territory areas: Semi-transparent office colors with opacity
- Hover states: Slightly darker/more opaque

## Technical Approach

### Map Library Options
1. **react-simple-maps** (Recommended)
   - Vector-based SVG maps
   - TopoJSON/GeoJSON support
   - Lightweight and performant
   - Easy to style with CSS
   - Good for choropleth/heat maps

2. **Recharts with custom SVG**
   - Already in use for other visualizations
   - Can render custom SVG paths
   - More control but more manual work

3. **D3.js** (if needed)
   - Most powerful but heavier
   - Overkill for this use case

**Recommendation**: Use `react-simple-maps` with TopoJSON for Norway

### Data Requirements

#### Norway GeoJSON/TopoJSON
- Need Norway map data with:
  - County (fylke) boundaries
  - Postal code boundaries (if available)
  - Simplified geometry for performance

Sources:
- **Kartverket** (Norwegian Mapping Authority) - official source
- **Natural Earth Data** - simplified world maps
- **GeoNorge** - Norwegian geospatial data portal

#### Office Data (Already Available)
From `offices` table:
- `id`, `name`, `short_code`
- `street_address`, `postal_code`, `city`
- `color` (for markers and territories)
- Coordinates (lat/long) - **Need to add or geocode from address**

#### Territory Data (Already Available)
From `office_territories` table:
- `office_id`, `postal_code`
- `source`, `priority`, `is_blacklisted`

## Implementation Plan

### Phase 1: Map Foundation
1. **Add Geocoding**
   - Add `latitude` and `longitude` columns to `offices` table
   - Create migration: `ALTER TABLE offices ADD COLUMN latitude FLOAT, ADD COLUMN longitude FLOAT`
   - Geocode existing offices from their addresses
   - Options: Use Nominatim (OpenStreetMap), Google Geocoding API, or manual entry

2. **Install Map Dependencies**
   ```bash
   cd frontend
   npm install react-simple-maps
   npm install --save-dev @types/react-simple-maps
   ```

3. **Obtain Norway Map Data**
   - Download TopoJSON for Norway with counties
   - Store in `frontend/public/maps/norway-counties.json`
   - Optionally: postal code boundaries if available

4. **Create Map Component**
   - `frontend/src/components/territories/TerritoryMap.tsx`
   - Render Norway with county borders
   - Add zoom and pan controls
   - Responsive container

### Phase 2: Office Markers
1. **Plot Office Locations**
   - Use office `latitude`/`longitude` to place markers
   - Circular markers with office `color`
   - Size based on number of territories or employees
   - Hover tooltip showing office name and stats

2. **Office Marker Component**
   - `frontend/src/components/territories/OfficeMarker.tsx`
   - Click to navigate to office detail page
   - Hover shows office info card

### Phase 3: Territory Heat Map
1. **Color Postal Code Areas**
   - Match postal codes to map geometry
   - Fill with office color (semi-transparent)
   - Handle overlapping territories (show conflict)
   - Blacklisted areas shown with striped pattern or different color

2. **Territory Legend**
   - Show all offices with their colors
   - Toggle visibility per office
   - Show territory count per office

### Phase 4: Interactivity
1. **Hover Effects**
   - Highlight postal code area on hover
   - Show tooltip with: postal code, area name, assigned office
   - Highlight corresponding office marker

2. **Click Actions**
   - Click postal code → show assignment details
   - Click office marker → navigate to office page
   - Click unassigned area → suggest assignment

3. **Filters**
   - Toggle layers by source (Vitec Next, Finn, etc.)
   - Show/hide blacklisted areas
   - Filter by office

## Database Changes

### Migration: Add Geocoding to Offices
```sql
-- Add latitude and longitude columns
ALTER TABLE offices ADD COLUMN latitude DOUBLE PRECISION;
ALTER TABLE offices ADD COLUMN longitude DOUBLE PRECISION;

-- Add index for spatial queries (optional, for future)
CREATE INDEX idx_offices_coordinates ON offices(latitude, longitude);
```

### Geocoding Script
Create `backend/scripts/geocode_offices.py`:
- Read offices with addresses
- Use Nominatim API to get coordinates
- Update database with lat/long
- Handle errors gracefully

## Component Structure

```
frontend/src/components/territories/
├── TerritoryMap.tsx          # Main map component
├── OfficeMarker.tsx           # Office location marker
├── TerritoryArea.tsx          # Postal code area (if custom rendering)
├── MapLegend.tsx              # Legend showing offices and colors
├── MapControls.tsx            # Zoom, pan, reset controls
└── TerritoryTooltip.tsx       # Hover tooltip
```

## API Endpoints (Existing)
- `GET /api/territories/map` - Returns GeoJSON with territories
- `GET /api/territories/stats` - Territory statistics
- `GET /api/offices` - Office list with locations

## New API Endpoints Needed
- `GET /api/offices/with-coordinates` - Offices with lat/long and territory counts
- `POST /api/offices/{id}/geocode` - Trigger geocoding for specific office

## UI Layout

```
┌─────────────────────────────────────────────────────────┐
│ Map Controls (Zoom +/-, Reset, Fullscreen)              │
├─────────────────────────────────────────────────────────┤
│                                                          │
│                    Norway Map                            │
│              (with county borders)                       │
│                                                          │
│    ● Office 1 (Stavanger)                               │
│       ● Office 2 (Sandnes)                              │
│                                                          │
│                                                          │
│                                                          │
└─────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────┐
│ Legend:                                                  │
│ ● Proaktiv Properties (6 territories)   [Toggle]        │
│ ● Sandnes (15 territories)              [Toggle]        │
│ ● Stavanger (23 territories)            [Toggle]        │
└─────────────────────────────────────────────────────────┘
```

## Acceptance Criteria
- [ ] Map displays Norway with clear county borders (fylkesgrenser)
- [ ] Vector-based, clean design matching app aesthetic
- [ ] Office locations plotted accurately based on addresses
- [ ] Each office has a colored marker using their `color` field
- [ ] Postal code territories shown with semi-transparent office colors
- [ ] Hover over territory shows postal code and assigned office
- [ ] Click office marker navigates to office detail page
- [ ] Legend shows all offices with toggle visibility
- [ ] Map is responsive and works on desktop/tablet
- [ ] County borders are clearly visible
- [ ] Performance is good (< 1s load time)

## Future Enhancements
- [ ] Postal code search with map highlight
- [ ] Territory assignment directly from map
- [ ] Conflict detection (overlapping territories)
- [ ] Export map as PNG/PDF
- [ ] 3D visualization option
- [ ] Historical territory changes over time
- [ ] Mobile-optimized touch controls

## Resources
- **react-simple-maps**: https://www.react-simple-maps.io/
- **Kartverket**: https://kartkatalog.geonorge.no/
- **Nominatim Geocoding**: https://nominatim.openstreetmap.org/
- **TopoJSON**: https://github.com/topojson/topojson
- **Norway GeoJSON**: https://github.com/deldersveld/topojson (has Norway data)

## Implementation Priority
1. **High**: Map foundation with county borders and office markers
2. **High**: Geocoding offices and plotting locations
3. **Medium**: Territory heat map coloring
4. **Medium**: Interactive hover and click
5. **Low**: Advanced filters and controls
