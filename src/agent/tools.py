"""LangChain tools for the content generation agent."""

import json
import os
from typing import Any

import httpx
from langchain_core.tools import tool

# Environment variable names
FREEPIK_API_KEY_ENV = "FREEPIK_API_KEY"
FREEPIK_MYSTIC_URL_ENV = "FREEPIK_MYSTIC_URL"
YUTORI_API_KEY_ENV = "YUTORI_API_KEY"
YUTORI_API_URL = "https://api.yutori.com/v1/research/tasks"

# Global storage for the generated content (will be returned via API)
_generated_content: dict[str, Any] = {}


def _get_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required env var: {name}")
    return value


def get_generated_content() -> dict[str, Any]:
    """Get the generated content from the last agent run."""
    return _generated_content.copy()


def clear_generated_content():
    """Clear the generated content storage."""
    global _generated_content
    _generated_content = {}


# ============== Yutori Tools ==============


@tool
async def yutori_scrape_trends(query: str, num_results: int = 10) -> str:
    """
    Scrape trending topics for a given niche/industry using Yutori's Research API.

    Args:
        query: Search query for niche/industry (e.g., 'sustainable fashion trends 2024')
        num_results: Number of trend results to return (default: 10)

    Returns:
        JSON string with task_id to poll for results, or error message.
    """
    headers = {
        "X-API-Key": _get_env(YUTORI_API_KEY_ENV),
        "Content-Type": "application/json",
    }
    payload: dict[str, Any] = {
        "query": query,
        "task_spec": {
            "output_schema": {
                "type": "json",
                "json_schema": {
                    "type": "object",
                    "properties": {
                        "trends": {
                            "type": "array",
                            "maxItems": num_results,
                            "items": {
                                "type": "object",
                                "properties": {
                                    "title": {
                                        "type": "string",
                                        "description": "Title of the trend",
                                    },
                                    "description": {
                                        "type": "string",
                                        "description": "Brief description of the trend",
                                    },
                                    "url": {
                                        "type": "string",
                                        "description": "Source URL for more details",
                                    },
                                    "relevance_score": {
                                        "type": "number",
                                        "description": "Relevance score from 0 to 1",
                                    },
                                },
                                "required": ["title", "description", "url"],
                            },
                        },
                    },
                    "required": ["trends"],
                },
            },
        },
    }
    try:
        # Use trust_env=False to bypass proxy restrictions
        async with httpx.AsyncClient(timeout=60, trust_env=False) as client:
            response = await client.post(YUTORI_API_URL, headers=headers, json=payload)
            response.raise_for_status()
            return json.dumps(response.json())
    except Exception as exc:
        return f"Yutori error: {exc}"


@tool
async def yutori_research_status(task_id: str) -> str:
    """
    Fetch status and results for a Yutori research task.

    Args:
        task_id: Yutori research task ID from yutori_scrape_trends response.

    Returns:
        JSON string with status (queued, running, succeeded, failed) and results when complete.
    """
    headers = {
        "X-API-Key": _get_env(YUTORI_API_KEY_ENV),
    }
    try:
        # Use trust_env=False to bypass proxy restrictions
        async with httpx.AsyncClient(timeout=60, trust_env=False) as client:
            response = await client.get(f"{YUTORI_API_URL}/{task_id}", headers=headers)
            response.raise_for_status()
            return json.dumps(response.json())
    except Exception as exc:
        return f"Yutori error: {exc}"


# ============== Freepik Tools ==============


@tool
async def freepik_generate_image(prompt: str, aspect_ratio: str = "1:1") -> str:
    """
    Generate an image using Freepik Mystic from a text prompt.

    Args:
        prompt: Detailed text prompt describing the image to generate.
        aspect_ratio: Aspect ratio for the image (default: "1:1" for Instagram).

    Returns:
        JSON string with task_id to poll for results, or error message.
    """
    base_url = _get_env(FREEPIK_MYSTIC_URL_ENV)
    headers = {
        "x-freepik-api-key": _get_env(FREEPIK_API_KEY_ENV),
        "Content-Type": "application/json",
    }
    payload = {
        "prompt": prompt,
        "aspect_ratio": aspect_ratio,
    }
    try:
        # Use trust_env=False to bypass proxy restrictions
        async with httpx.AsyncClient(timeout=60, trust_env=False) as client:
            response = await client.post(base_url, headers=headers, json=payload)
            response.raise_for_status()
            return json.dumps(response.json())
    except Exception as exc:
        return f"Freepik error: {exc}"


@tool
async def freepik_check_status(task_id: str) -> str:
    """
    Check the status of a Freepik image generation task.

    Args:
        task_id: The task ID from freepik_generate_image response.

    Returns:
        JSON string with status and image URL when complete (status: "COMPLETED").
    """
    base_url = _get_env(FREEPIK_MYSTIC_URL_ENV)
    headers = {
        "x-freepik-api-key": _get_env(FREEPIK_API_KEY_ENV),
    }
    try:
        # Use trust_env=False to bypass proxy restrictions
        async with httpx.AsyncClient(timeout=60, trust_env=False) as client:
            response = await client.get(f"{base_url}/{task_id}", headers=headers)
            response.raise_for_status()
            return json.dumps(response.json())
    except Exception as exc:
        return f"Freepik error: {exc}"


# ============== Content Output Tool ==============


@tool
def save_content_results(posts: list[dict[str, Any]]) -> str:
    """
    Save the generated social media content. This must be called at the end with all 7 posts.

    Args:
        posts: List of post dictionaries with keys:
            - post_number (int): 1-7
            - day (str): Day of the week ("Monday" through "Sunday")
            - topic (str): Topic of the post
            - post_copy (str): Post caption text (100-150 characters)
            - hashtags (str): Comma-separated hashtags
            - image_url (str): URL of the generated image from Freepik
            - image_prompt (str): Prompt used to generate image
            - best_time_to_post (str): Suggested posting time (e.g., "10:00 AM EST")

    Returns:
        Confirmation message.
    """
    global _generated_content
    _generated_content = {"posts": posts}
    return f"Successfully saved {len(posts)} posts. Content is ready for display."


def get_all_tools(output_dir: str) -> list:
    """Get all tools for the content generation agent."""
    # Clear any previous content
    clear_generated_content()

    return [
        yutori_scrape_trends,
        yutori_research_status,
        freepik_generate_image,
        freepik_check_status,
        save_content_results,
    ]
