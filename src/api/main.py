"""FastAPI backend for the content factory."""

import os
import tempfile
import uuid

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from src.agent.agent import run_content_generation
from src.agent.tools import get_generated_content

app = FastAPI(
    title="Content Factory API",
    description="Generate a week's worth of social media content with AI",
    version="0.1.0",
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class GenerateRequest(BaseModel):
    """Request body for content generation."""

    brand_description: str = Field(
        ...,
        min_length=50,
        max_length=1000,
        description="Description of the brand/niche for content generation (50-1000 characters)",
        examples=[
            "Sustainable fashion brand targeting millennial women, focuses on eco-friendly materials and ethical manufacturing. Our aesthetic is minimalist with earthy tones and natural textures."
        ],
    )


class PostContent(BaseModel):
    """A single social media post."""

    post_number: int
    day: str
    topic: str
    post_copy: str
    hashtags: str
    image_url: str
    image_prompt: str
    best_time_to_post: str


class GenerateResponse(BaseModel):
    """Response containing generated content."""

    posts: list[PostContent]


class ErrorResponse(BaseModel):
    """Error response model."""

    error: str
    detail: str


@app.post(
    "/api/generate",
    response_model=GenerateResponse,
    responses={
        200: {"model": GenerateResponse, "description": "Generated content"},
        400: {"model": ErrorResponse, "description": "Validation error"},
        500: {"model": ErrorResponse, "description": "Processing error"},
    },
)
async def generate_content(request: GenerateRequest):
    """
    Generate a week's worth of social media content.

    Returns JSON with 7 posts including:
    - Post copy (captions)
    - Hashtags
    - Image URLs from Freepik
    - Suggested posting times
    """
    job_id = str(uuid.uuid4())
    output_dir = os.path.join(tempfile.gettempdir(), f"content-factory-{job_id}")
    os.makedirs(output_dir, exist_ok=True)

    try:
        # Run the content generation agent
        print(f"Starting content generation for job {job_id}")
        result = await run_content_generation(
            brand_description=request.brand_description,
            output_dir=output_dir,
        )

        if result["status"] != "success":
            error_msg = result.get("error", "Unknown error")
            traceback_info = result.get("traceback", "")
            print(f"Agent error: {error_msg}\n{traceback_info}")
            raise HTTPException(
                status_code=500,
                detail={"error": "Generation failed", "detail": error_msg},
            )

        # Get the generated content from the tool
        content = get_generated_content()
        print(f"Generated content: {content}")

        if not content or "posts" not in content or not content["posts"]:
            # Try to get info from the last message
            last_message = ""
            if "result" in result and "messages" in result["result"]:
                messages = result["result"]["messages"]
                if messages:
                    last_msg = messages[-1]
                    # Extract content from different message types
                    if hasattr(last_msg, "content"):
                        if isinstance(last_msg.content, list):
                            # Handle list of content blocks
                            last_message = " ".join(
                                (
                                    str(block.get("text", block))
                                    if isinstance(block, dict)
                                    else str(block)
                                )
                                for block in last_msg.content
                            )
                        else:
                            last_message = str(last_msg.content)
                    else:
                        last_message = str(last_msg)

                    print(f"Last agent message: {last_message}")

            raise HTTPException(
                status_code=500,
                detail={
                    "error": "No content generated",
                    "detail": f"The agent did not produce any posts. Last message: {last_message[:500]}",
                },
            )

        return {"posts": content["posts"]}

    except HTTPException:
        raise
    except Exception as e:
        import traceback

        print(f"Unexpected error: {e}\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail={"error": "Content generation failed", "detail": str(e)},
        )


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


# Serve static files for frontend (mount last to not override API routes)
static_dir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "static"
)
if os.path.exists(static_dir):
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
