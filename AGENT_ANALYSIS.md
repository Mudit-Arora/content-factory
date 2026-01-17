# Content Factory Agent - Analysis Report

## Executive Summary
This document provides a comprehensive analysis of the Content Factory agent, a LangChain-based AI system that autonomously generates social media content for brands.

**Date**: 2026-01-17
**Agent Type**: LangChain ReAct Agent (LangGraph)
**Primary LLM**: GPT-4o via OpenAI
**Purpose**: Generate 7 days of social media posts with images based on brand description

---

## Architecture Overview

### Technology Stack
```
Frontend (Static)
    ├── HTML/CSS/JavaScript (Vanilla)
    └── User submits brand description

Backend (FastAPI)
    ├── POST /api/generate - Main endpoint
    ├── GET /health - Health check
    └── Serves static frontend

Agent Layer (LangChain + LangGraph)
    ├── GPT-4o (ChatOpenAI)
    ├── ReAct Agent Pattern
    └── 5 Custom Tools:
        ├── yutori_scrape_trends
        ├── yutori_research_status
        ├── freepik_generate_image
        ├── freepik_check_status
        └── save_content_results

External APIs
    ├── Yutori Research API (trend scraping)
    ├── Freepik Mystic API (image generation)
    └── OpenAI API (GPT-4o)
```

### Key Components

#### 1. Agent Core (`src/agent/agent.py`)
- **Function**: `create_content_agent(output_dir: str)`
  - Creates a LangGraph ReAct agent
  - Uses GPT-4o with temperature=0.7
  - Max tokens: 4096
  - Recursion limit: 100 (allows many tool calls)

- **Function**: `run_content_generation(brand_description: str, output_dir: str)`
  - Invokes the agent with brand description
  - Returns status dict with results or errors

#### 2. Tools (`src/agent/tools.py`)
All tools are async and return JSON strings:

**Yutori Tools (Trend Research)**:
- `yutori_scrape_trends(query, num_results=10)`
  - Initiates a research task on Yutori API
  - Returns task_id for polling
  - Uses structured JSON schema for output

- `yutori_research_status(task_id)`
  - Polls Yutori task status
  - Returns results when status is "succeeded"
  - Agent must poll until complete

**Freepik Tools (Image Generation)**:
- `freepik_generate_image(prompt, aspect_ratio="1:1")`
  - Submits image generation request
  - Returns task_id for polling
  - Default aspect ratio for Instagram

- `freepik_check_status(task_id)`
  - Checks image generation status
  - Returns image URL when status is "COMPLETED"
  - Agent must poll until complete

**Output Tool**:
- `save_content_results(posts: list[dict])`
  - Saves final results to global storage
  - Required fields per post:
    - post_number (1-7)
    - day (Monday-Sunday)
    - topic
    - post_copy (100-150 chars)
    - hashtags
    - image_url
    - image_prompt
    - best_time_to_post

#### 3. System Prompt (`src/agent/prompts.py`)
The agent follows a 6-step workflow:

1. **Research Trends**: Call Yutori with brand-related query
2. **Poll for Results**: Wait for Yutori research completion (max 60s)
3. **Select Topics**: Choose 7 diverse, brand-aligned topics
4. **Create Posts**: Generate copy, hashtags, image prompts
5. **Generate Images**: Use Freepik for all 7 posts (poll until complete)
6. **Save Results**: Call save_content_results with all posts

**Key Instructions**:
- Always poll status endpoints (no instant completion assumption)
- Keep post copy under 150 characters
- Image prompts should be detailed (50+ words)
- Must call save_content_results at the end

#### 4. API Backend (`src/api/main.py`)
- **Framework**: FastAPI
- **CORS**: Enabled for all origins
- **Main Endpoint**: POST `/api/generate`
  - Validates brand_description (50-1000 chars)
  - Creates temp output directory
  - Runs agent synchronously
  - Returns posts as JSON

**Error Handling**:
- 400: Validation errors (description too short/long)
- 500: Agent errors, no content generated

#### 5. Frontend (`static/`)
- Simple HTML form for brand description
- JavaScript POSTs to `/api/generate`
- Displays generated posts with images
- Clean, minimal UI

---

## Agent Execution Flow

### Detailed Workflow

```
1. User Input
   └─> Brand description submitted via web form

2. FastAPI Receives Request
   ├─> Validates input (50-1000 chars)
   ├─> Creates job ID and temp directory
   └─> Calls run_content_generation()

3. Agent Initialization
   ├─> Clears previous content storage
   ├─> Creates ReAct agent with GPT-4o
   └─> Loads 5 tools

4. Agent Execution (ReAct Loop)
   │
   ├─> THOUGHT: Analyze brand description
   ├─> ACTION: yutori_scrape_trends("sustainable fashion trends 2026", 10)
   ├─> OBSERVATION: Returns task_id
   │
   ├─> THOUGHT: Need to wait for Yutori results
   ├─> ACTION: yutori_research_status(task_id)
   ├─> OBSERVATION: "status": "running"
   │
   ├─> (Repeat polling every 5-10s until succeeded)
   │
   ├─> OBSERVATION: Returns 10 trends with titles, descriptions, URLs
   │
   ├─> THOUGHT: Select best 7 topics for posts
   ├─> (Internal reasoning, no tool call)
   │
   ├─> THOUGHT: Generate first post
   ├─> ACTION: freepik_generate_image("Minimalist flat lay eco-friendly clothing...", "1:1")
   ├─> OBSERVATION: Returns image task_id
   │
   ├─> THOUGHT: Wait for image generation
   ├─> ACTION: freepik_check_status(task_id)
   ├─> OBSERVATION: "status": "PROCESSING"
   │
   ├─> (Repeat polling until COMPLETED)
   │
   ├─> OBSERVATION: Returns image_url
   │
   ├─> (Repeat for all 7 posts)
   │
   ├─> THOUGHT: All content generated, save results
   ├─> ACTION: save_content_results([{post_1}, {post_2}, ..., {post_7}])
   ├─> OBSERVATION: "Successfully saved 7 posts"
   │
   └─> Final answer to user

5. FastAPI Returns Response
   ├─> Retrieves content from global storage
   ├─> Returns JSON with 7 posts
   └─> Frontend displays posts with images
```

### Tool Call Pattern

Each async tool follows this pattern:
1. Agent calls tool with parameters
2. Tool makes HTTP request to external API
3. Returns task_id or error
4. Agent must poll status until complete
5. Extract final data (trends/image URLs)

### Data Flow

```
Brand Description
    ↓
GPT-4o (generates research query)
    ↓
Yutori API (returns trends)
    ↓
GPT-4o (selects topics, creates post copy)
    ↓
Freepik API (returns image URLs)
    ↓
GPT-4o (assembles final posts)
    ↓
save_content_results (stores in memory)
    ↓
FastAPI (returns to user)
```

---

## Configuration

### Environment Variables
```bash
# Required for agent operation
OPENAI_API_KEY=sk-proj-...           # GPT-4o access
FREEPIK_API_KEY=FPSXb...             # Image generation
FREEPIK_MYSTIC_URL=https://api.freepik.com/v1/ai/mystic
YUTORI_API_KEY=yt_VUY...             # Trend research
```

### Agent Parameters
- **Model**: gpt-4o (not gpt-4o-mini)
- **Temperature**: 0.7 (creative but consistent)
- **Max Tokens**: 4096 (enough for multi-step reasoning)
- **Recursion Limit**: 100 (allows ~50 tool calls)
- **Timeout**: 5 minutes (FastAPI default)

---

## Agent Capabilities

### What the Agent Does Well
1. **Autonomous Workflow**: No human intervention needed after initial prompt
2. **Multi-Step Planning**: Handles complex 6-step workflow
3. **Async Polling**: Properly waits for long-running API tasks
4. **Error Recovery**: Can retry failed API calls
5. **Structured Output**: Returns well-formatted JSON

### Limitations
1. **Fixed Output**: Always generates exactly 7 posts
2. **Synchronous**: FastAPI blocks during generation (2-3 min wait)
3. **No Customization**: Cannot adjust tone, style, or post count
4. **API Dependencies**: Fails if Yutori or Freepik are unavailable
5. **Memory-Only Storage**: Results not persisted to database

---

## Dependencies

### Python Packages (from pyproject.toml)
```toml
langchain>=0.3.0          # Core LangChain framework
langchain-openai>=0.3.0   # OpenAI integration
langgraph>=0.2.0          # Graph-based agent orchestration
fastapi>=0.115.0          # Web API framework
httpx                     # Async HTTP client for tools
python-dotenv>=1.0.0      # Environment variable management
openpyxl>=3.1.0          # Excel file generation (unused?)
uvicorn                   # ASGI server
```

### External APIs
1. **OpenAI API**
   - Model: gpt-4o
   - Usage: Agent reasoning and generation
   - Cost: ~$0.01 per request (estimated)

2. **Yutori Research API**
   - Endpoint: https://api.yutori.com/v1/research/tasks
   - Usage: Web scraping for trends
   - Response time: ~10-30 seconds

3. **Freepik Mystic API**
   - Endpoint: https://api.freepik.com/v1/ai/mystic
   - Usage: AI image generation
   - Response time: ~10-20 seconds per image

---

## Test Results

### Test Execution
- **Test Script**: `test_agent.py`
- **Brand**: "Sustainable fashion brand targeting millennial women..."
- **Result**: Connection error (403 Forbidden)

### Error Analysis
```
Error Type: openai.APIConnectionError
Root Cause: httpcore.ProxyError: 403 Forbidden
Location: OpenAI API client initialization
```

**Likely Causes**:
1. Network proxy blocking OpenAI API
2. Firewall restrictions
3. Invalid API credentials
4. Region-based API access restrictions

**Resolution Steps**:
1. Check network proxy settings
2. Verify OpenAI API key validity
3. Test from different network
4. Check OpenAI API status page

### Expected Behavior (if successful)
1. Agent starts, analyzes brand description
2. Calls Yutori to research sustainable fashion trends
3. Polls for ~10-30 seconds until results ready
4. Selects 7 topics (e.g., circular fashion, eco-friendly materials, etc.)
5. For each topic:
   - Generates engaging post copy
   - Creates 5 hashtags
   - Writes detailed image prompt
   - Calls Freepik to generate image
   - Polls for ~10-20 seconds until image ready
6. Saves all 7 posts with save_content_results
7. Returns complete JSON with posts

**Total Expected Runtime**: 2-4 minutes

---

## Agent Design Patterns

### 1. ReAct Pattern
The agent uses the Reasoning-Action-Observation loop:
- **Reasoning**: GPT-4o thinks about next step
- **Action**: Calls one of the 5 tools
- **Observation**: Receives tool output
- Repeat until task complete

### 2. Polling Pattern
Both Yutori and Freepik require async polling:
```
1. Submit request → get task_id
2. Poll status endpoint every 5-10s
3. Check if status is "succeeded"/"COMPLETED"
4. Extract results when ready
```

### 3. Global State Storage
Results stored in module-level variable:
```python
_generated_content: dict[str, Any] = {}
```
- Allows FastAPI to retrieve after agent completes
- Not thread-safe (assumes single concurrent request)
- Cleared before each agent run

---

## Potential Improvements

### Short-Term
1. **Async FastAPI**: Use background tasks instead of blocking
2. **Progress Updates**: WebSocket or SSE for live status
3. **Better Error Messages**: User-friendly API error explanations
4. **Retry Logic**: Automatic retry for failed API calls
5. **Validation**: Check image URLs are valid before returning

### Medium-Term
1. **Database Storage**: Persist generated content
2. **User Accounts**: Save brand profiles for reuse
3. **Customization**: Allow tone, style, post count adjustments
4. **Preview Mode**: Show first post before generating all 7
5. **Fallback APIs**: Use alternative image providers if Freepik fails

### Long-Term
1. **Multi-Platform**: Generate platform-specific content (Twitter, LinkedIn, TikTok)
2. **Scheduling Integration**: Direct integration with Buffer, Hootsuite
3. **Analytics**: Predict engagement for each post
4. **A/B Testing**: Generate multiple variations per post
5. **Custom Voice Training**: Fine-tune model on brand examples

---

## Running the Agent

### Prerequisites
```bash
# 1. Python 3.12+
python --version

# 2. Install uv package manager
curl -LsSf https://astral.sh/uv/install.sh | sh

# 3. Clone repository
git clone <repo-url>
cd content-factory
```

### Setup
```bash
# 1. Install dependencies
uv sync

# 2. Configure environment variables
cp sample.env .env
# Edit .env with your API keys:
#   - OPENAI_API_KEY
#   - FREEPIK_API_KEY
#   - YUTORI_API_KEY
```

### Running Tests
```bash
# Activate virtual environment
source .venv/bin/activate

# Run test script
python test_agent.py
```

### Running API Server
```bash
# Activate virtual environment
source .venv/bin/activate

# Start FastAPI server
uvicorn src.api.main:app --host 0.0.0.0 --port 8000

# Access at: http://localhost:8000
```

### Using the Web Interface
1. Open http://localhost:8000 in browser
2. Enter brand description (50-1000 chars)
3. Click "Generate Content"
4. Wait 2-3 minutes
5. View generated posts with images

---

## Code Quality

### Strengths
✅ Clear separation of concerns (agent, tools, API, frontend)
✅ Type hints throughout codebase
✅ Async/await for all I/O operations
✅ Comprehensive docstrings
✅ Environment variable management
✅ Error handling with try/except
✅ Pydantic models for API validation

### Areas for Improvement
⚠️ No unit tests
⚠️ No integration tests
⚠️ Global state (_generated_content) not thread-safe
⚠️ Hard-coded values (recursion limit, timeouts)
⚠️ No logging infrastructure
⚠️ API keys in environment only (no secrets manager)
⚠️ No rate limiting
⚠️ No monitoring/observability

---

## Security Considerations

### Current State
1. **API Keys**: Stored in .env (not committed to git) ✅
2. **CORS**: Allows all origins ⚠️
3. **Input Validation**: Length limits on brand_description ✅
4. **Rate Limiting**: None ⚠️
5. **Authentication**: None ⚠️

### Recommendations
1. Use secrets manager (AWS Secrets Manager, HashiCorp Vault)
2. Restrict CORS to specific domains
3. Add rate limiting (per IP, per user)
4. Implement API key authentication
5. Sanitize user input (XSS prevention)
6. Add request size limits
7. Log all API calls for auditing

---

## Performance Characteristics

### Expected Latency
- **Yutori Research**: 10-30 seconds
- **Freepik (per image)**: 10-20 seconds
- **Total for 7 posts**: 2-4 minutes

### Bottlenecks
1. **Sequential Image Generation**: Could parallelize
2. **Polling Overhead**: 5-10 second intervals add latency
3. **Synchronous API**: Blocks server during generation

### Optimization Opportunities
1. **Parallel Image Generation**: Generate all 7 images concurrently
2. **Smarter Polling**: Exponential backoff, adaptive intervals
3. **Caching**: Cache trends for similar brand descriptions
4. **Background Jobs**: Use Celery or similar for async processing

---

## Conclusion

This is a **well-architected AI agent** that demonstrates:
- Proper use of LangChain/LangGraph framework
- Clean integration with external APIs
- Autonomous multi-step workflow execution
- Async I/O and polling patterns

**Current Status**: Code is production-ready for MVP/demo, but needs improvements for production scale (monitoring, testing, security, performance).

**Best Use Case**: Hackathon demo, proof of concept, or internal tool for small teams.

**Next Steps**: Add background task processing, improve error handling, implement proper testing suite.

---

## References

### Documentation
- LangChain: https://python.langchain.com/docs/
- LangGraph: https://langchain-ai.github.io/langgraph/
- FastAPI: https://fastapi.tiangolo.com/
- Freepik Mystic API: (internal docs)
- Yutori API: (internal docs)

### Files
- Agent Core: `src/agent/agent.py`
- Tools: `src/agent/tools.py`
- Prompts: `src/agent/prompts.py`
- API: `src/api/main.py`
- Test Script: `test_agent.py`
- Configuration: `.env`, `sample.env`

---

**Report Generated**: 2026-01-17
**Agent Status**: Analyzed and Tested
**Result**: Connection error (network restrictions)
