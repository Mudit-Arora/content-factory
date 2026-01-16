# Automated Social Media Content Factory - Technical Overview

## Project Summary
**Time Constraint:** 3 hours (hackathon)  
**Goal:** Build an autonomous agent system that generates a week's worth of social media posts with images based on user's brand description.

**Demo Flow:**
1. User enters brand/niche description in simple web form
2. System autonomously creates 7 posts with matching images
3. User downloads ZIP file containing spreadsheet + images
4. Content is ready to schedule on social media platforms

---

## System Architecture

### High-Level Components

```
User → Browser (Simple HTML) → FastAPI Backend → Cline Agent → MCP Server (Yutori + Freepik)
                                       ↓
                                  ZIP Download
```

### Technology Stack
- **Frontend:** Plain HTML + vanilla JavaScript (no frameworks)
- **Backend:** FastAPI (Python 3.10+)
- **Agent:** Cline (MCP-enabled AI agent)
- **Tools:** Yutori (web scraping), Freepik (image generation)
- **Output:** Excel/CSV spreadsheet + PNG images in ZIP file

---

## Component Specifications

### 1. Frontend (Browser)

**File:** `index.html` + `styles.css` + `script.js`

**Requirements:**
- Simple, clean form with single textarea for brand description
- Submit button that triggers POST request
- Loading spinner that shows during processing (2-3 min expected)
- Auto-download ZIP file on completion
- Error display if generation fails

**Form Fields:**
- `brand_description` (textarea, required): Multi-line text input for brand/niche description
  - Example: "Sustainable fashion brand targeting millennial women, focuses on eco-friendly materials and ethical manufacturing"
  
**UI States:**
1. **Idle:** Form visible, submit enabled
2. **Loading:** Form disabled, spinner visible, status text
3. **Success:** Auto-download ZIP, success message
4. **Error:** Error message displayed, form re-enabled

**Sample HTML Structure:**
```html
<form id="contentForm">
  <label for="brand">Describe your brand/niche:</label>
  <textarea id="brand" name="brand_description" rows="6" required 
            placeholder="E.g., Tech startup focused on AI productivity tools for remote teams..."></textarea>
  <button type="submit">Generate Content</button>
</form>
<div id="loading" style="display:none;">
  <div class="spinner"></div>
  <p>Generating your content... This takes 2-3 minutes</p>
</div>
<div id="result"></div>
```

**JavaScript Behavior:**
```javascript
// On form submit:
// 1. Prevent default
// 2. Show loading spinner
// 3. POST to /api/generate with form data
// 4. Wait for response (synchronous, may take 2-3 min)
// 5. On success: trigger download of returned ZIP
// 6. On error: show error message
```

---

### 2. FastAPI Backend

**File:** `main.py`

**Endpoint Specification:**

#### POST `/api/generate`

**Request:**
```json
{
  "brand_description": "string (required, 50-1000 characters)"
}
```

**Response (Success):**
- **Status:** 200
- **Content-Type:** `application/zip`
- **Headers:** `Content-Disposition: attachment; filename="social_content_{timestamp}.zip"`
- **Body:** Binary ZIP file containing:
  - `social_posts.xlsx` (or .csv)
  - `images/post_1.png`
  - `images/post_2.png`
  - ... (7 images total)

**Response (Error):**
```json
{
  "error": "string",
  "detail": "string"
}
```
- **Status:** 500 (processing error) or 400 (validation error)

**Processing Flow:**
1. Validate request payload
2. Generate unique job ID for logging
3. Call Cline agent with prompt template
4. **Block and wait** for Cline to complete (synchronous)
5. Collect generated files from working directory
6. Package files into ZIP
7. Return ZIP as download
8. Clean up temporary files

**Implementation Notes:**
- Set request timeout to 5 minutes (generous for 3-minute typical runtime)
- Use Python's `zipfile` module to create archive
- Cline should save outputs to a predictable directory (e.g., `./output/{job_id}/`)
- FastAPI should serve from `./output/{job_id}/` then delete after response

**Error Handling:**
- Timeout after 5 minutes → 500 error
- Missing Cline executable → 500 error
- Invalid brand description → 400 error
- File generation failure → 500 error

**Sample Code Structure:**
```python
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
import subprocess
import zipfile
import os
import uuid

app = FastAPI()

class GenerateRequest(BaseModel):
    brand_description: str

@app.post("/api/generate")
async def generate_content(request: GenerateRequest):
    job_id = str(uuid.uuid4())
    output_dir = f"./output/{job_id}"
    
    # Validate input
    if len(request.brand_description) < 50:
        raise HTTPException(400, "Description too short")
    
    # Call Cline with MCP
    # Wait for completion
    # Package ZIP
    # Return file
    
    return FileResponse(
        zip_path,
        media_type="application/zip",
        filename=f"social_content_{job_id[:8]}.zip"
    )
```

---

### 3. Cline Agent Integration

**Role:** Orchestrates the entire content generation workflow

**Input from FastAPI:**
- Brand description string
- Output directory path

**Cline's Workflow:**

```
1. Receive brand description
2. Call Yutori MCP tool → scrape 5-10 trending topics in niche
3. Analyze trends → extract 7 best topics for posts
4. For each of 7 posts:
   a. Generate post copy (caption + hashtags)
   b. Create image prompt from post content
   c. Call Freepik MCP tool → generate image
   d. Save image as post_{n}.png
5. Compile all data into spreadsheet
6. Save spreadsheet as social_posts.xlsx
7. Signal completion to FastAPI
```

**Prompt Template for Cline:**

```
You are a social media content strategist. Generate a week's worth of posts (7 posts) for the following brand:

BRAND: {brand_description}

WORKFLOW:
1. Use Yutori to scrape trending topics related to this brand's niche
2. Select 7 diverse topics that align with the brand
3. For each topic, create:
   - Engaging post copy (100-150 characters for Instagram/Twitter)
   - 5 relevant hashtags
   - Image generation prompt (detailed, visual description)
4. Use Freepik to generate an image for each post
5. Save all data to an Excel spreadsheet with columns:
   - Post_Number (1-7)
   - Topic
   - Post_Copy
   - Hashtags
   - Image_Filename
   - Image_Prompt_Used
6. Save images as: post_1.png, post_2.png, ... post_7.png
7. Save spreadsheet as: social_posts.xlsx

OUTPUT REQUIREMENTS:
- All files must be saved to: {output_directory}
- Images in: {output_directory}/images/
- Spreadsheet: {output_directory}/social_posts.xlsx

Begin the workflow now.
```

**Expected Cline Behavior:**
- Autonomous execution without user intervention
- Use MCP tools via function calls
- Error recovery: if Freepik fails for one image, try alternate prompt
- File naming consistency
- Log progress for debugging

---

### 4. MCP Server & Tools

**Configuration:** `mcp_config.json` (or Cline's MCP settings)

#### Tool 1: Yutori (Web Scraping)

**Purpose:** Scrape trending topics in user's niche

**Function Signature:**
```json
{
  "name": "yutori_scrape_trends",
  "description": "Scrape trending topics for a given niche/industry",
  "parameters": {
    "query": "string (required) - Search query for niche",
    "num_results": "integer (default: 10) - Number of results to return"
  }
}
```

**Example Call:**
```json
{
  "tool": "yutori_scrape_trends",
  "parameters": {
    "query": "sustainable fashion trends 2024",
    "num_results": 10
  }
}
```

**Expected Response:**
```json
{
  "trends": [
    {
      "title": "Circular Fashion Economy",
      "description": "Brands embracing rental and resale models...",
      "url": "https://...",
      "relevance_score": 0.95
    },
    ...
  ]
}
```

**Implementation Notes:**
- Yutori should scrape from: Twitter trends, Reddit, Google Trends, industry blogs
- Return structured data (title, description, source URL)
- Filter for recency (last 30 days preferred)

#### Tool 2: Freepik (Image Generation)

**Purpose:** Generate on-brand images for social media posts

**Function Signature:**
```json
{
  "name": "freepik_generate_image",
  "description": "Generate an AI image from text prompt",
  "parameters": {
    "prompt": "string (required) - Detailed image description",
    "style": "string (optional) - Image style (e.g., 'photorealistic', 'illustration', 'minimal')",
    "aspect_ratio": "string (default: '1:1') - Aspect ratio for social media",
    "output_path": "string (required) - Where to save the image"
  }
}
```

**Example Call:**
```json
{
  "tool": "freepik_generate_image",
  "parameters": {
    "prompt": "Minimalist flat lay of eco-friendly clothing items on natural linen background, soft lighting, Instagram aesthetic",
    "style": "photorealistic",
    "aspect_ratio": "1:1",
    "output_path": "./output/abc123/images/post_1.png"
  }
}
```

**Expected Response:**
```json
{
  "success": true,
  "image_path": "./output/abc123/images/post_1.png",
  "prompt_used": "Minimalist flat lay of...",
  "generation_time": 12.3
}
```

**Implementation Notes:**
- Images should be Instagram-ready (1080x1080px minimum)
- PNG format preferred
- Style should match brand aesthetic (extracted from brand description)

#### Tool 3: File Output Helper (Custom)

**Purpose:** Save results back to FastAPI in structured format

**Function Signature:**
```json
{
  "name": "save_results",
  "description": "Signal completion and save output manifest",
  "parameters": {
    "output_dir": "string (required) - Output directory path",
    "files": "array (required) - List of generated files",
    "status": "string (required) - 'success' or 'error'"
  }
}
```

**Example Call:**
```json
{
  "tool": "save_results",
  "parameters": {
    "output_dir": "./output/abc123",
    "files": [
      "social_posts.xlsx",
      "images/post_1.png",
      "images/post_2.png",
      ...
    ],
    "status": "success"
  }
}
```

---

### 5. Output Format Specification

#### Spreadsheet (social_posts.xlsx or .csv)

**Columns:**
1. **Post_Number** (integer): 1-7
2. **Day** (string): "Monday", "Tuesday", etc.
3. **Topic** (string): Trending topic this post addresses
4. **Post_Copy** (string): 100-150 character engaging caption
5. **Hashtags** (string): 5 hashtags (comma-separated or space-separated)
6. **Image_Filename** (string): "post_1.png", etc.
7. **Image_Prompt** (string): Prompt used to generate image
8. **Best_Time_To_Post** (string): Suggested posting time (e.g., "10:00 AM EST")

**Example Row:**
| Post_Number | Day | Topic | Post_Copy | Hashtags | Image_Filename | Image_Prompt | Best_Time_To_Post |
|-------------|-----|-------|-----------|----------|----------------|--------------|-------------------|
| 1 | Monday | Circular Fashion | "Fashion that gives back 🌍 Our new rental program makes sustainable style accessible to everyone!" | #CircularFashion #EcoStyle #SustainableCloset #RentalFashion #GreenLiving | post_1.png | Minimalist flat lay of eco-friendly clothing... | 10:00 AM EST |

#### Images (post_1.png through post_7.png)

**Specifications:**
- Format: PNG
- Resolution: 1080x1080px (Instagram square)
- Aspect Ratio: 1:1
- File Size: < 5MB each
- Color Space: RGB
- Naming: `post_1.png`, `post_2.png`, ..., `post_7.png`
- Location: `images/` subdirectory in output

**Content Guidelines:**
- High-quality, professional appearance
- On-brand colors and aesthetic
- No text overlay (text is in Post_Copy)
- Social media ready (no watermarks beyond Freepik's standard)

#### ZIP File Structure

```
social_content_abc12345.zip
├── social_posts.xlsx
└── images/
    ├── post_1.png
    ├── post_2.png
    ├── post_3.png
    ├── post_4.png
    ├── post_5.png
    ├── post_6.png
    └── post_7.png
```

---

## Implementation Priorities

### Must-Have (Core Demo)
1. ✅ Simple HTML form with brand input
2. ✅ FastAPI endpoint that blocks until completion
3. ✅ Cline calls Yutori → gets trends
4. ✅ Cline generates 7 post copies
5. ✅ Cline calls Freepik → generates 7 images
6. ✅ Cline creates spreadsheet
7. ✅ FastAPI packages and returns ZIP

### Nice-to-Have (If Time Permits)
- Better error messages in UI
- Progress updates during generation
- Preview of first post before full generation
- Brand tone customization (formal/casual/funny)
- Ability to regenerate specific posts

### Explicitly Out-of-Scope (Do NOT Build)
- User authentication
- Database storage
- Job queue / async processing
- Multiple simultaneous requests
- Edit/save/history features
- Payment integration

---

## Testing Strategy

### Manual Testing Checklist

**Frontend:**
- [ ] Form validates empty input
- [ ] Loading spinner appears on submit
- [ ] ZIP auto-downloads on success
- [ ] Error message displays on failure

**Backend:**
- [ ] `/api/generate` accepts valid request
- [ ] Endpoint times out after 5 minutes
- [ ] ZIP contains all 8 files (1 xlsx + 7 png)
- [ ] Files are not corrupted

**Cline Integration:**
- [ ] Cline receives brand description
- [ ] Yutori returns relevant trends
- [ ] Freepik generates 7 distinct images
- [ ] Spreadsheet has 7 rows with correct data
- [ ] All files saved to correct directory

**End-to-End:**
- [ ] Submit form → receive ZIP in < 5 minutes
- [ ] Open ZIP → extract files without errors
- [ ] Open XLSX → data is properly formatted
- [ ] Open images → high-quality, 1080x1080px
- [ ] Content matches brand description

### Test Brand Descriptions

**Test Case 1 (Simple):**
```
"Coffee shop in Seattle focused on artisan roasts and cozy community spaces"
```

**Test Case 2 (Complex):**
```
"B2B SaaS platform helping remote teams manage asynchronous communication. Target audience: tech companies with 50-200 employees. Professional, modern, productivity-focused brand voice."
```

**Test Case 3 (Niche):**
```
"Fitness brand for busy moms focusing on 15-minute home workouts, body positivity, and realistic wellness goals. Warm, encouraging, non-judgmental tone."
```

---

## Error Handling

### Expected Error Scenarios

1. **Yutori Returns No Results**
   - Fallback: Use generic industry topics
   - Message: "Could not find specific trends, using general topics"

2. **Freepik API Rate Limit**
   - Fallback: Use placeholder images or stock photos
   - Message: "Image generation limited, using alternatives"

3. **Cline Timeout (> 5 min)**
   - Response: 500 error
   - Message: "Content generation timed out, please try again"

4. **Invalid Brand Description**
   - Response: 400 error
   - Message: "Please provide a more detailed brand description (50+ characters)"

5. **File System Errors**
   - Response: 500 error
   - Message: "Unable to save files, please try again"

### Logging Strategy

**Log Levels:**
- INFO: Request received, Cline started, files generated
- WARNING: Partial failures, fallbacks used
- ERROR: Complete failures, timeouts

**Log Format:**
```
[timestamp] [job_id] [level] message
```

**Example:**
```
2024-01-16 14:30:00 abc12345 INFO Request received: brand_description="Coffee shop..."
2024-01-16 14:30:05 abc12345 INFO Cline workflow started
2024-01-16 14:31:20 abc12345 INFO Yutori returned 10 trends
2024-01-16 14:32:45 abc12345 WARNING Freepik retry needed for post_3.png
2024-01-16 14:33:10 abc12345 INFO All 7 images generated
2024-01-16 14:33:15 abc12345 INFO Spreadsheet created
2024-01-16 14:33:18 abc12345 INFO ZIP file packaged
2024-01-16 14:33:20 abc12345 INFO Response sent (duration: 3m 20s)
```

---

## Deployment Notes

### Local Development Setup

**Requirements:**
```
Python 3.10+
Node.js (optional, for frontend dev server)
Cline installed and configured
MCP server running with Yutori + Freepik
```

**Installation:**
```bash
# Backend
cd backend
pip install fastapi uvicorn python-multipart
python main.py

# Frontend
cd frontend
# Serve with any static server, e.g.:
python -m http.server 8000
# Or just open index.html in browser

# Access at: http://localhost:8000
```

### Hackathon Demo Environment

**Requirements:**
- Laptop with Python 3.10+ installed
- Cline running with MCP access
- Freepik API key configured
- Yutori scraping working
- Chrome/Firefox for browser demo

**Pre-Demo Checklist:**
- [ ] Test end-to-end with sample brand
- [ ] Clear output directory
- [ ] Have backup ZIP ready (in case of live demo failure)
- [ ] Prepare 2-3 brand descriptions for different verticals
- [ ] Test internet connection (for Freepik API)

---

## Security Considerations

### Input Validation
- Sanitize brand_description for XSS
- Limit input length (max 1000 characters)
- Rate limit: 1 request per IP per 5 minutes (optional)

### File System
- Use UUIDs for output directories (prevent path traversal)
- Clean up temporary files after ZIP download
- Limit output directory size (max 50MB)

### API Keys
- Store Freepik API key in environment variables
- Never expose API keys in frontend code
- Use separate dev/prod keys if applicable

---

## Success Criteria

### Minimum Viable Demo (Must Work)
- User enters brand → clicks submit
- Sees loading spinner for 2-3 minutes
- Downloads ZIP file
- ZIP contains 7 images + 1 spreadsheet
- Images are visually appealing and on-brand
- Spreadsheet data is accurate and useful

### Impressive Demo (Stretch Goals)
- Content quality impresses judges
- Images look professional and diverse
- Post copy is creative and engaging
- System completes in < 2 minutes
- Zero errors during live demo

### Judging Criteria Alignment
- **Autonomy:** Cline orchestrates entire workflow without human input ✓
- **Tool Usage:** Uses all 3 tools (Yutori + Freepik + MCP) heavily ✓
- **Real Problem:** Solves tedious content creation for SMBs ✓
- **Visual Impact:** Pretty images make demo memorable ✓
- **Completeness:** End-to-end working system ✓

---

## Timeline (3 Hours)

### Hour 1: Foundation (0:00 - 1:00)
- **0:00-0:20:** Set up project structure, install dependencies
- **0:20-0:40:** Create FastAPI endpoint skeleton
- **0:40-1:00:** Create basic HTML form with submit handler

### Hour 2: Core Functionality (1:00 - 2:00)
- **1:00-1:30:** Wire up Cline integration with FastAPI
- **1:30-1:45:** Test Yutori MCP tool (get trends working)
- **1:45-2:00:** Test Freepik MCP tool (generate 1 image)

### Hour 3: End-to-End + Polish (2:00 - 3:00)
- **2:00-2:20:** Complete Cline workflow (7 posts + spreadsheet)
- **2:20-2:40:** Implement ZIP packaging and download
- **2:40-2:50:** End-to-end testing with real brand descriptions
- **2:50-3:00:** Demo preparation (backup files, test script)

---

## Key Technical Decisions

### Why Synchronous (Blocking) Request?
- **Simplicity:** No job queue, no polling, no WebSockets
- **Time:** Saves 60+ minutes of implementation
- **Demo:** Users expect to wait for AI generation
- **Scalability:** Not needed for hackathon (1 user at a time)

### Why No Authentication?
- **Time:** Auth0 setup is 45+ minutes
- **Scope:** Not relevant to core demo
- **Judges:** Won't care about login flow

### Why Plain HTML?
- **Speed:** No React build setup, no state management
- **Reliability:** Fewer moving parts, easier debugging
- **Focus:** More time for Cline/MCP integration

### Why Excel/CSV?
- **Familiarity:** Users know how to use spreadsheets
- **Portable:** Easy to import into scheduling tools
- **Visual:** Can open and see all content at once

---

## Fallback Plan

### If Freepik Fails
- Use Unsplash API (free, no auth needed)
- Use DALL-E via OpenAI (requires API key)
- Use placeholder images with text descriptions

### If Yutori Fails
- Hardcode 20 generic topics per vertical
- Use Reddit API directly (no MCP needed)
- Skip trend scraping, generate posts from brand description only

### If Cline Fails
- Implement as Python script (direct MCP calls)
- Use OpenAI API directly (bypass Cline)
- Pre-generate content, show as "demo mode"

---

## Post-Hackathon Ideas (Do NOT Build Now)

- User accounts with saved brand profiles
- Scheduling integration (Buffer, Hootsuite)
- A/B testing suggestions for posts
- Analytics on predicted engagement
- Multi-platform optimization (Twitter, LinkedIn, TikTok)
- Custom brand voice training
- Competitor analysis
- Hashtag performance predictions

---

## Questions for Clarification

Before starting implementation, confirm:

1. **MCP Setup:** Is Cline already configured with Yutori + Freepik MCP servers?
2. **API Keys:** Do we have valid Freepik API credentials?
3. **Yutori Scope:** What sources can Yutori scrape (Reddit, Twitter, blogs)?
4. **File Storage:** Where should temporary files be stored during processing?
5. **Error Recovery:** Should Cline retry failed API calls automatically?

---

## Success Metrics

### Technical
- End-to-end generation time: < 3 minutes
- Zero crashes during demo
- All 7 images generated successfully
- Spreadsheet with complete data

### Business
- Judges understand the value proposition
- Demo feels "magical" (autonomous, impressive output)
- Content quality is professional enough to use
- System shows clear autonomy (minimal human input)

---

## Final Notes

**Keep It Simple:** Every feature adds complexity. When in doubt, cut it.

**Focus on Demo Quality:** Judges see the output, not the code. Make the content impressive.

**Test Early:** Don't wait until hour 2:45 to test end-to-end.

**Have a Backup:** Pre-generate one ZIP file in case live demo fails.

**Rehearse:** Practice the demo flow 2-3 times before presenting.

**Time Boxing:** If any component takes > 45 minutes, simplify or skip it.

---

## Contact & Support

**During Hackathon:**
- Keep this document open for reference
- Log all errors for debugging
- Take screenshots of successful outputs
- Save generated content as examples

**Resources:**
- FastAPI docs: https://fastapi.tiangolo.com
- Cline docs: (internal/GitHub)
- MCP specification: (if available)
- Freepik API: (documentation link)

---

END OF TECHNICAL OVERVIEW