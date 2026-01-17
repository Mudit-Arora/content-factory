# Quick Start: Testing API Tools

## TL;DR

```bash
# 1. Set up your .env file with API keys
cp env.sample .env
# Edit .env and add your API keys

# 2. Run all tests
python -m src.agent.test_all_tools

# Or use the convenience script
./src/agent/run_tests.sh
```

## Quick Commands

From the project root directory:

```bash
# Test everything (recommended first run)
python -m src.agent.test_all_tools

# Test only Yutori
python -m src.agent.test_yutori

# Test only Freepik
python -m src.agent.test_freepik

# Using the shell script
./src/agent/run_tests.sh all      # All tests
./src/agent/run_tests.sh yutori   # Yutori only
./src/agent/run_tests.sh freepik  # Freepik only
```

## Required Environment Variables

```bash
# .env file
YUTORI_API_KEY=your_key_here
FREEPIK_API_KEY=your_key_here
FREEPIK_MYSTIC_URL=https://api.freepik.com/v1/ai/mystic
```

## What Gets Tested

### Yutori
- ✅ API authentication
- ✅ Creating research tasks
- ✅ Polling task status
- ✅ Retrieving research results
- ✅ Parsing trend data

### Freepik
- ✅ API authentication
- ✅ Creating image generation tasks
- ✅ Polling task status
- ✅ Retrieving image URLs
- ✅ Different aspect ratios (optional)

## Expected Results

### Success ✅
- Both tools create tasks successfully
- Status polling works
- Results are retrieved and displayed
- No errors or exceptions

### Common Issues

| Error | Solution |
|-------|----------|
| `YUTORI_API_KEY environment variable not set` | Add API key to `.env` file |
| `HTTP error 401: Unauthorized` | Check API key is correct |
| `ModuleNotFoundError: No module named 'src'` | Run from project root |
| Task times out | Increase `max_attempts` in test file |

## Next Steps

After tests pass:
1. ✅ API tools are working correctly
2. ✅ Ready to use in the main agent
3. ✅ Can run full content generation workflow

See `TEST_README.md` for detailed documentation.
