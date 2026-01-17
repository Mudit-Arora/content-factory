# API Tools Test Scripts

This directory contains test scripts for testing the Yutori and Freepik API tools in isolation, without requiring the full agent setup.

## Test Files

- **`test_yutori.py`** - Tests Yutori research API tools
- **`test_freepik.py`** - Tests Freepik image generation API tools
- **`test_all_tools.py`** - Runs all tests in sequence with environment validation

## Prerequisites

### Required Environment Variables

Create a `.env` file in the project root with the following variables:

```bash
# Yutori API
YUTORI_API_KEY=your_yutori_api_key_here

# Freepik API
FREEPIK_API_KEY=your_freepik_api_key_here
FREEPIK_MYSTIC_URL=https://api.freepik.com/v1/ai/mystic
```

### Required Dependencies

Make sure you have installed all project dependencies:

```bash
pip install -r requirements.txt
# or
uv pip install -r requirements.txt
```

## Running the Tests

All commands should be run from the **project root directory** (`/Users/gavin/hackathons/content-factory`).

### Test All Tools (Recommended)

Run the comprehensive test suite that checks environment variables and tests all tools:

```bash
python -m src.agent.test_all_tools
```

### Test Yutori Only

Test just the Yutori research API tools:

```bash
python -m src.agent.test_yutori
```

This will:
1. Call `yutori_scrape_trends` with a sample query
2. Poll `yutori_research_status` until the task completes
3. Display the research results

### Test Freepik Only

Test just the Freepik image generation API tools:

```bash
python -m src.agent.test_freepik
```

This will:
1. Call `freepik_generate_image` with a sample prompt
2. Poll `freepik_check_status` until the image is generated
3. Display the image URL

## What Each Test Does

### Yutori Tests (`test_yutori.py`)

**Test 1: `yutori_scrape_trends`**
- Sends a research query: "sustainable fashion trends 2024"
- Requests 5 trend results
- Returns a task ID for polling

**Test 2: `yutori_research_status`**
- Polls the task status every 5 seconds
- Maximum 10 attempts (50 seconds total)
- Displays the research results when complete
- Shows trend titles, descriptions, URLs, and relevance scores

### Freepik Tests (`test_freepik.py`)

**Test 1: `freepik_generate_image`**
- Generates an image with a sample prompt about sustainable fashion
- Uses 1:1 aspect ratio (Instagram format)
- Returns a task ID for polling

**Test 2: `freepik_check_status`**
- Polls the task status every 5 seconds
- Maximum 20 attempts (100 seconds total)
- Displays the image URL when generation is complete

**Test 3: `test_multiple_aspect_ratios`** (Optional, commented out)
- Tests different aspect ratios: 1:1, 16:9, 9:16, 4:3
- Uncomment in the `main()` function to enable

## Expected Output

### Successful Yutori Test Output

```
🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪
YUTORI API TOOLS TEST SUITE
🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪

================================================================================
TEST: yutori_scrape_trends
================================================================================

📝 Test Query: 'sustainable fashion trends 2024'
📊 Number of results: 5

🔄 Calling yutori_scrape_trends...

✅ Response received:
{
  "task_id": "abc123...",
  "status": "queued"
}

✅ Task created successfully!
📋 Task ID: abc123...

================================================================================
TEST: yutori_research_status
================================================================================

📋 Task ID: abc123...

🔄 Checking task status...

Attempt 1/10...
   Status: running
   ⏳ Task still processing. Waiting 5 seconds...

Attempt 2/10...
   Status: succeeded

✅ Task completed successfully!

📊 Results:
{
  "status": "succeeded",
  "result": {
    "trends": [...]
  }
}

📈 Found 5 trends:

  1. Circular Fashion Economy
     Description: The shift towards circular fashion models...
     URL: https://example.com/trend1
     Relevance: 0.95
  ...
```

### Successful Freepik Test Output

```
🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪
FREEPIK API TOOLS TEST SUITE
🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪

================================================================================
TEST: freepik_generate_image
================================================================================

📝 Test Prompt: 'A modern minimalist Instagram post...'
📐 Aspect Ratio: 1:1

🔄 Calling freepik_generate_image...

✅ Response received:
{
  "task_id": "xyz789...",
  "status": "PENDING"
}

✅ Image generation task created successfully!
📋 Task ID: xyz789...

================================================================================
TEST: freepik_check_status
================================================================================

📋 Task ID: xyz789...

🔄 Checking task status...

Attempt 1/20...
   Status: PROCESSING
   ⏳ Image still generating. Waiting 5 seconds...

Attempt 2/20...
   Status: COMPLETED

✅ Image generation completed successfully!

🖼️  Image URL: https://cdn.freepik.com/...
```

## Troubleshooting

### Missing Environment Variables

```
❌ ERROR: YUTORI_API_KEY environment variable not set
   Please set it in your .env file or environment
```

**Solution:** Create or update your `.env` file with the required API keys.

### API Authentication Errors

```
❌ API returned an error: Yutori HTTP error 401: Unauthorized
```

**Solution:** Check that your API key is correct and active.

### Import Errors

```
ModuleNotFoundError: No module named 'src'
```

**Solution:** Make sure you're running the command from the project root directory.

### Timeout Issues

If tasks are taking too long:
- Increase `max_attempts` in the test scripts
- Increase `wait_seconds` between polling attempts
- Check the API service status

## Customizing Tests

### Change Test Queries/Prompts

Edit the test scripts to use your own queries:

```python
# In test_yutori.py
test_query = "your custom research query here"
num_results = 10

# In test_freepik.py
test_prompt = "your custom image prompt here"
aspect_ratio = "16:9"  # or "1:1", "9:16", "4:3"
```

### Adjust Polling Settings

```python
# In test scripts
max_attempts = 20  # Number of status checks
wait_seconds = 5   # Seconds between checks
```

## Integration with Main Agent

These tools are used by the main agent in `agent.py`. The test scripts help verify that:
1. API credentials are configured correctly
2. API endpoints are accessible
3. Request/response formats are correct
4. Polling logic works as expected

Once tests pass, the tools should work correctly when called by the LangChain agent.
