import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Any, List, Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.append(str(CURRENT_DIR))

from mcp_server import call_tool as mcp_call_tool  # noqa: E402

app = FastAPI(title="Content Factory MCP HTTP Bridge")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ResearchRequest(BaseModel):
    prompt: str


class ResearchResult(BaseModel):
    contentIdea: str
    strategy: str
    imagePrompt: str


class ImageRequest(BaseModel):
    prompts: List[str]


class GeneratedImage(BaseModel):
    url: str
    alt: str


def _extract_first_json(items: list[Any]) -> dict[str, Any]:
    errors: list[str] = []
    for item in items:
        text = getattr(item, "text", None)
        if text is None:
            text = str(item)
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            errors.append(text)
    raise RuntimeError(errors[0] if errors else "Invalid MCP response")


def _find_first_url(obj: Any) -> Optional[str]:
    if isinstance(obj, str) and obj.startswith("http"):
        return obj
    if isinstance(obj, dict):
        for value in obj.values():
            found = _find_first_url(value)
            if found:
                return found
    if isinstance(obj, list):
        for value in obj:
            found = _find_first_url(value)
            if found:
                return found
    return None


def _find_task_id(obj: Any) -> Optional[str]:
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key in {"task_id", "taskId", "id"} and isinstance(value, str):
                return value
            found = _find_task_id(value)
            if found:
                return found
    if isinstance(obj, list):
        for value in obj:
            found = _find_task_id(value)
            if found:
                return found
    return None


def _extract_trends(payload: dict[str, Any]) -> list[dict[str, Any]]:
    for key in ("trends", "results", "data"):
        value = payload.get(key)
        if isinstance(value, list):
            return value
        if isinstance(value, dict):
            nested = _extract_trends(value)
            if nested:
                return nested
    return []


async def _call_tool_json(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    items = await mcp_call_tool(name, arguments)
    return _extract_first_json(items)


async def _poll_freepik_status(
    task_id: str, attempts: int, delay_s: float
) -> dict[str, Any]:
    for _ in range(attempts):
        await asyncio.sleep(delay_s)
        payload = await _call_tool_json("freepik_mystic_status", {"task_id": task_id})
        if _find_first_url(payload):
            return payload
        status = str(payload.get("data", {}).get("status", "")).upper()
        if status in {"FAILED", "ERROR"}:
            break
    return {}


async def _cline_orchestrate_research(prompt: str) -> list[ResearchResult]:
    # This function represents the Cline orchestration layer.
    # Today it calls MCP tools directly; swap this with real Cline orchestration later.
    yutori = await _call_tool_json(
        "yutori_scrape_trends",
        {
            "query": prompt,
            "num_results": 6,
        },
    )
    trends = _extract_trends(yutori)
    results: list[ResearchResult] = []
    for trend in trends[:6]:
        title = trend.get("title") or prompt
        description = trend.get("description") or "Use a clear value prop and CTA."
        results.append(
            ResearchResult(
                contentIdea=title,
                strategy=description,
                imagePrompt=f"{title}. {description}".strip(),
            )
        )
    return results


async def _cline_orchestrate_images(prompts: list[str]) -> list[GeneratedImage]:
    # This function represents the Cline orchestration layer.
    # Today it calls MCP tools directly; swap this with real Cline orchestration later.
    attempts = int(os.getenv("MYSTIC_POLL_ATTEMPTS", "5"))
    delay_s = float(os.getenv("MYSTIC_POLL_DELAY_S", "4"))
    images: list[GeneratedImage] = []
    for prompt in prompts:
        generate = await _call_tool_json(
            "freepik_mystic_generate",
            {
                "prompt": prompt,
            },
        )
        image_url = _find_first_url(generate)
        if not image_url:
            task_id = _find_task_id(generate)
            if task_id:
                status_payload = await _poll_freepik_status(
                    task_id, attempts=attempts, delay_s=delay_s
                )
                image_url = _find_first_url(status_payload)

        if not image_url:
            raise RuntimeError(f"Freepik did not return an image for '{prompt}'")
        images.append(GeneratedImage(url=image_url, alt=prompt))
    return images


@app.post("/tools/get_research", response_model=List[ResearchResult])
async def get_research(payload: ResearchRequest):
    prompt = payload.prompt.strip()
    if not prompt:
        return JSONResponse(status_code=400, content={"error": "Prompt is empty"})
    results = await _cline_orchestrate_research(prompt)
    if not results:
        return JSONResponse(
            status_code=502, content={"error": "No trends returned from Yutori"}
        )
    return results


@app.post("/tools/generate_images", response_model=List[GeneratedImage])
async def generate_images(payload: ImageRequest):
    try:
        return await _cline_orchestrate_images(payload.prompts)
    except RuntimeError as exc:
        return JSONResponse(status_code=502, content={"error": str(exc)})


@app.get("/health")
async def health():
    return {"status": "ok", "env": os.getenv("ENV", "dev")}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
