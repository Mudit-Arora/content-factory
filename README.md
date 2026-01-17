# Content Factory 🎨

> AI-powered social media content generation for small businesses and creators

Generate a full week of professional social media content in minutes. Content Factory uses AI to research trends, write engaging posts, create custom images, and deliver everything ready to post.

![Content Factory Demo](https://img.shields.io/badge/Status-Hackathon%20Project-blue)
![Python](https://img.shields.io/badge/Python-3.11+-green)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-teal)

## ✨ Features

- **🤖 AI-Powered Content Generation**: Creates 7 unique posts tailored to your brand
- **🎨 Custom AI Images**: Generates relevant images using Freepik API
- **📊 Strategic Planning**: Suggests optimal posting times for each day
- **#️⃣ Smart Hashtags**: Generates relevant hashtags for maximum reach
- **💡 Trend Research**: Incorporates current trends into content
- **📱 Beautiful UI**: Clean, responsive web interface
- **📋 One-Click Copy**: Easy copying of post text and hashtags

## 🚀 Quick Start

### Prerequisites

- Python 3.11 or higher
- uv (Python package manager)
- Anthropic API key
- Freepik API key

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/content-factory.git
cd content-factory
```

2. **Install dependencies**
```bash
uv sync
```

3. **Set up environment variables**
```bash
cp env.sample .env
```

Edit `.env` and add your API keys:
```env
ANTHROPIC_API_KEY=your_anthropic_key_here
FREEPIK_API_KEY=your_freepik_key_here
```

4. **Run the application**
```bash
uv run uvicorn src.api.main:app --reload
```

5. **Open your browser**
Navigate to `http://localhost:8000`

## 🏗️ Architecture

```
content-factory/
├── src/
│   ├── agent/          # AI agent logic
│   │   ├── agent.py    # LangGraph agent orchestration
│   │   ├── tools.py    # Custom tools for content generation
│   │   └── prompts.py  # System prompts
│   ├── api/            # FastAPI backend
│   │   └── main.py     # API endpoints
│   └── mcp_servers/    # MCP server integration
└── static/             # Frontend files
    ├── index.html
    ├── script.js
    └── styles.css
```

## 🛠️ Tech Stack

### Backend
- **FastAPI**: High-performance async web framework
- **LangGraph**: AI agent workflow orchestration
- **Claude 3.5 Sonnet**: Advanced language model for content generation
- **Freepik API**: AI image generation

### Frontend
- **Vanilla JavaScript**: Lightweight and fast
- **Modern CSS**: Responsive design with gradients and animations

### Tools & Libraries
- **uv**: Fast Python package manager
- **Pydantic**: Data validation
- **HTTPX**: Async HTTP client

## 📖 How It Works

1. **User Input**: User describes their brand/niche (50-1000 characters)
2. **AI Agent**: LangGraph orchestrates multiple steps:
   - Researches trending topics
   - Generates 7 unique post concepts
   - Creates engaging copy and hashtags
   - Generates AI images via Freepik
   - Suggests optimal posting times
3. **Output**: Beautiful web interface displays all posts with images
4. **Export**: Users can copy text directly or download data

## 🎯 Use Cases

- **Small Businesses**: Generate consistent social media presence
- **Solopreneurs**: Save time on content creation
- **Marketing Agencies**: Quickly prototype content for clients
- **Content Creators**: Get inspiration and starting points
- **Startups**: Maintain social media without dedicated staff

## 🧪 Testing

Run the test suite:

```bash
# Test all tools
uv run python src/agent/test_all_tools.py

# Test Freepik integration
uv run python src/agent/test_freepik.py

# Test Yutori integration
uv run python src/agent/test_yutori.py
```

See `src/agent/TEST_RESULTS.md` for detailed test results.

## 📝 API Documentation

Once running, visit:
- **API Docs**: `http://localhost:8000/docs`
- **Health Check**: `http://localhost:8000/health`

### Main Endpoint

**POST** `/api/generate`

Request body:
```json
{
  "brand_description": "Your brand description here (50-1000 chars)"
}
```

Response:
```json
{
  "posts": [
    {
      "post_number": 1,
      "day": "Monday",
      "topic": "Product Feature",
      "post_copy": "Engaging post text...",
      "hashtags": "#relevant #hashtags",
      "image_url": "https://...",
      "image_prompt": "AI image description",
      "best_time_to_post": "9:00 AM"
    }
    // ... 6 more posts
  ]
}
```

## 🔑 Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `ANTHROPIC_API_KEY` | Anthropic API key for Claude | Yes |
| `FREEPIK_API_KEY` | Freepik API key for image generation | Yes |

## 🤝 Contributing

This is a hackathon project, but contributions are welcome!

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is built for educational and hackathon purposes.

## 🙏 Acknowledgments

- Built with [Claude](https://anthropic.com) by Anthropic
- Images powered by [Freepik API](https://freepik.com)
- Agent framework: [LangGraph](https://langchain-ai.github.io/langgraph/)


**Built with ❤️ for the Agent Orchestration Hackathon**
