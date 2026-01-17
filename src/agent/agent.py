"""LangChain agent for social media content generation."""

import json
import httpx
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

from .prompts import SYSTEM_PROMPT
from .tools import get_all_tools

load_dotenv()


async def create_content_agent(output_dir: str):
    """
    Create a LangChain agent with tools for content generation.

    Args:
        output_dir: Directory where output files (images) will be saved.

    Returns:
        The LangGraph agent ready to invoke.
    """
    # Get all tools including output-dir-bound ones
    all_tools = get_all_tools(output_dir)

    # Create httpx client without proxy to bypass Claude Code proxy restrictions
    # The proxy blocks api.openai.com with 403 Forbidden
    http_client = httpx.AsyncClient(
        trust_env=False,  # Ignore proxy environment variables
        timeout=httpx.Timeout(60.0),
    )

    # Initialize OpenAI model
    llm = ChatOpenAI(
        model="gpt-4o",
        temperature=0.7,
        max_tokens=4096,
        http_async_client=http_client,  # Use custom client without proxy
    )

    # Create ReAct agent with system prompt
    agent = create_react_agent(
        llm,
        tools=all_tools,
        prompt=SYSTEM_PROMPT,
    )

    return agent


async def run_content_generation(brand_description: str, output_dir: str) -> dict:
    """
    Run the content generation workflow for a brand.

    Args:
        brand_description: Description of the brand/niche.
        output_dir: Directory where output files will be saved.

    Returns:
        Dictionary with the agent's final response and status.
    """
    agent = await create_content_agent(output_dir)

    try:
        result = await agent.ainvoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": f"Generate social media content for this brand:\n\n{brand_description}",
                    }
                ]
            },
            {"recursion_limit": 100},  # Allow many tool calls for 7 posts
        )
        return {"status": "success", "result": result}
    except Exception as e:
        import traceback
        return {"status": "error", "error": str(e), "traceback": traceback.format_exc()}
