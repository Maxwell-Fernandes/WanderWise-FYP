# Goa App Web Scraper - Architecture Plan

## Overview
This document outlines the architecture for scraping the goa.app website, a JavaScript-heavy Nuxt.js/Vue.js application, to extract structured tourism data.

## Target Website Analysis

### Website Characteristics
- **Framework**: Nuxt.js (Vue.js) with Server-Side Rendering (SSR)
- **Rendering**: JavaScript-heavy, requires browser automation
- **URL Pattern**: `https://goa.app/places/{place-slug}`

### HTML Structure Analysis (from Dharvalem Beach example)

#### Key Content Selectors

| Data Field | CSS Selector | Example Value |
|------------|--------------|---------------|
| Title | `h1.main-title` | "Dharvalem Beach" |
| Category | `.category-type-text .badge` | "Beaches" |
| Location | `.coinfo-brief__item span.text-capitalize` | "Canacona, South Goa" |
| Short Description | `.activity-detail__content-group.mb-2 p` | "Dharvalem beach is a small beach..." |
| Main Content | `.para-text` | Contains h3 headers and p paragraphs |
| Guidelines | `#guidelines .activity-list li span` | List of visitor guidelines |
| Tags | `.tags-container .tags-p` | Keywords/tags |
| Rating | `.vue-star-rating` | 5 stars |
| Map Coordinates | Google Maps iframe src or `__NUXT__` state | lat: 15.065162, lng: 73.967857 |

#### Content Structure
The main content in `.para-text` follows this pattern:
```html
<div class="para-text">
  <p><em>Introduction paragraph...</em></p>
  <h3>Section Title</h3>
  <p>Section content...</p>
  <h3>Another Section</h3>
  <p>More content...</p>
</div>
```

## Proposed Solution Architecture

### Technology Stack
- **Language**: Python 3.8+
- **Browser Automation**: Playwright (recommended) or Selenium
- **HTML Parsing**: BeautifulSoup4
- **Output Format**: JSON (can be converted to CSV)

### Why Playwright?
1. **Headless browser support**: Renders JavaScript completely
2. **Fast and reliable**: Better than Selenium for modern JS apps
3. **Auto-wait capabilities**: Waits for elements to load
4. **Python support**: Good Python bindings
5. **Lightweight**: Less resource-intensive than Selenium

## JSON Output Structure

```json
{
  "url": "https://goa.app/places/dharvalem-beach-goa",
  "scraped_at": "2024-11-01T10:30:00Z",
  "data": {
    "name": "Dharvalem Beach",
    "category": "Beaches",
    "subcategory": "South Goa Beach",
    "location": {
      "area": "Canacona",
      "region": "South Goa",
      "latitude": 15.065162,
      "longitude": 73.967857
    },
    "description": "Dharvalem beach is a small beach located to the north of Coco beach...",
    "detailed_content": {
      "sections": [
        {
          "title": "A Coastal Retreat",
          "content": "Dharvalem Beach, also known as the Small Cola Beach locally..."
        },
        {
          "title": "Nature's Canvas",
          "content": "As you step onto Dharvalem Beach..."
        }
      ],
      "full_html": "<p><em>Tucked away...</em></p><h3>A Coastal Retreat</h3>..."
    },
    "guidelines": [
      "There are no buses going to this beach...",
      "Transportation: Dharvalem Beach is accessible by..."
    ],
    "tags": ["dharvalem beach", "dharvalem beach goa", "south goa", ...],
    "rating": {
      "score": 5,
      "max_score": 5
    },
    "nearby_attractions": [
      {
        "name": "Cabo de Rama Beach",
        "category": "Beaches",
        "location": "Canaguinim, South Goa"
      }
    ],
    "popular_experiences": [
      {
        "name": "South Goa Hidden Beaches and Cliffs Trek",
        "location": "Canacona",
        "price": 1995,
        "bookings": "600+"
      }
    ]
  }
}
```

## Script Architecture

### Main Components

```
goa_app_scraper/
├── scraper.py           # Main scraper class
├── selectors.py         # CSS selectors configuration
├── parsers.py          # Content parsing functions
├── utils.py            # Utility functions
├── requirements.txt    # Dependencies
└── README.md           # Usage documentation
```

### Class Structure

```python
class GoaAppScraper:
    def __init__(self, headless=True)
    def scrape_place(self, url: str) -> dict
    def extract_title(self, page) -> str
    def extract_category(self, page) -> str
    def extract_location(self, page) -> dict
    def extract_description(self, page) -> str
    def extract_detailed_content(self, page) -> dict
    def extract_guidelines(self, page) -> list
    def extract_tags(self, page) -> list
    def extract_coordinates(self, page) -> dict
    def extract_nearby_attractions(self, page) -> list
    def save_to_json(self, data: dict, output_path: str)
```

## Implementation Steps

### Step 1: Setup and Dependencies
```python
# requirements.txt
playwright==1.40.0
beautifulsoup4==4.12.2
lxml==4.9.3
python-dateutil==2.8.2
```

### Step 2: Initialize Browser
- Launch Playwright in headless mode
- Set appropriate user agent
- Configure viewport and timeouts

### Step 3: Navigate and Wait
- Navigate to URL
- Wait for main content to load
- Handle any popups or overlays

### Step 4: Extract Content
- Use CSS selectors to extract each field
- Parse and clean HTML content
- Handle missing fields gracefully

### Step 5: Process and Output
- Structure data into JSON format
- Save to file
- Log results

## Error Handling Strategy

| Error Type | Handling Strategy |
|------------|-------------------|
| Network timeout | Retry with exponential backoff (max 3 retries) |
| Element not found | Log warning, return None for field |
| Invalid URL | Validate URL format before scraping |
| JavaScript error | Take screenshot, save page HTML for debugging |
| Rate limiting | Implement delays between requests |

## Usage Examples

### Single URL Scraping
```python
from scraper import GoaAppScraper

scraper = GoaAppScraper()
result = scraper.scrape_place("https://goa.app/places/dharvalem-beach-goa")
scraper.save_to_json(result, "output/dharvalem_beach.json")
```

### Batch Scraping from File
```python
from scraper import GoaAppScraper

scraper = GoaAppScraper()
urls = [
    "https://goa.app/places/dharvalem-beach-goa",
    "https://goa.app/places/palolem-beach",
    # ... more URLs
]

for url in urls:
    result = scraper.scrape_place(url)
    scraper.save_to_json(result, f"output/{result['data']['name'].lower().replace(' ', '_')}.json")
```

### Interactive Mode
```python
from scraper import GoaAppScraper

scraper = GoaAppScraper()

while True:
    url = input("Enter URL (or 'quit' to exit): ")
    if url.lower() == 'quit':
        break
    
    result = scraper.scrape_place(url)
    print(f"Scraped: {result['data']['name']}")
    scraper.save_to_json(result, f"output/{result['data']['name']}.json")
```

## Mapping to Existing CSV Schema

The scraped JSON can be mapped to the existing `Wanderwise_datasetnew.csv` schema:

| JSON Field | CSV Column | Notes |
|------------|------------|-------|
| data.name | name | Direct mapping |
| data.category | category | May need normalization |
| data.location.region | subcategory | e.g., "South Goa Beach" |
| data.location.latitude | latitude | Direct mapping |
| data.location.longitude | longitude | Direct mapping |
| data.description | description | Direct mapping |
| - | entry_fee_inr | Default to 0 or extract if available |
| - | is_free | Default to TRUE for beaches |
| - | opening_time | Default to "00:00" |
| - | closing_time | Default to "23:59" |
| data.detailed_content.sections | - | Additional context for description |
| data.guidelines | tips | Join with "\n" |
| data.tags | instagram_tags | Convert to #hashtags |

## Performance Considerations

1. **Rate Limiting**: Add 2-3 second delays between requests
2. **Caching**: Cache rendered pages for repeated scraping
3. **Parallel Processing**: Use async Playwright for batch scraping
4. **Resource Cleanup**: Properly close browser instances

## Testing Strategy

1. **Unit Tests**: Test each extraction function
2. **Integration Tests**: Test full scraping workflow
3. **Sample Data**: Use provided HTML for regression testing
4. **Edge Cases**: Test with missing fields, different page types

## Next Steps

1. [ ] Create the scraper.py file with Playwright setup
2. [ ] Implement CSS selectors in selectors.py
3. [ ] Create parsing functions in parsers.py
4. [ ] Add error handling and logging
5. [ ] Test with provided URL
6. [ ] Create usage documentation

## Alternative: Direct API Approach

The website exposes data in the `__NUXT__` JavaScript variable. An alternative approach:

```javascript
// Accessible via browser console
window.__NUXT__
```

This contains server-rendered state including:
- `attractionData`: Main place information
- `relatedActivities`: Nearby experiences
- `relatedPlaces`: Nearby attractions

A JavaScript-based scraper could extract this directly:
```javascript
const nuxtData = await page.evaluate(() => window.__NUXT__);
```

This approach is more reliable but requires understanding the internal data structure.
