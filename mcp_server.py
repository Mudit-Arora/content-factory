import argparse
import asyncio
import json
import os
from typing import Any

import httpx
from mcp.server import Server
from mcp.types import Tool, TextContent

server = Server("content-factory-toolkit")




def _get_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required env var: {name}")
    return value


async def _post_to_freepik(url: str, payload: dict[str, Any]) -> dict[str, Any]:
    headers = {
        "x-freepik-api-key": _get_env(FREEPIK_API_KEY_ENV),
        "Content-Type": "application/json",
    }
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="freepik_mystic_generate",
            description=(
                "Generate an image using Freepik Mystic from a text prompt with "
                "optional parameters."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "prompt": {"type": "string", "description": "Text prompt"},
                    "resolution": {
                        "type": "string",
                        "description": "Output resolution (e.g., 1k, 2k, 4k).",
                    },
                    "aspect_ratio": {
                        "type": "string",
                        "description": "Aspect ratio (e.g., 1:1, 4:5, 16:9).",
                    },
                    "engine": {
                        "type": "string",
                        "description": "Generation engine.",
                    },
                    "model": {
                        "type": "string",
                        "description": "Model identifier.",
                    },
                    "creative_detailing": {
                        "type": "string",
                        "description": "Creative detailing level.",
                    },
                    "styling": {
                        "type": "object",
                        "description": "Styling instructions (style, color, character, etc.).",
                        "additionalProperties": True,
                    },
                    "structure_reference": {
                        "type": "string",
                        "description": "Structure reference image URL.",
                    },
                    "style_reference": {
                        "type": "string",
                        "description": "Style reference image URL.",
                    },
                    "adherence": {
                        "type": "string",
                        "description": "Adherence level for reference guidance.",
                    },
                    "hdr": {
                        "type": "boolean",
                        "description": "Enable HDR-like enhancement.",
                    },
                    "fixed_generation": {
                        "type": "boolean",
                        "description": "Enable deterministic generation.",
                    },
                    "webhook_url": {
                        "type": "string",
                        "description": "Webhook callback URL.",
                    },
                    "params": {
                        "type": "object",
                        "description": "Optional extra Mystic API parameters",
                        "additionalProperties": True,
                    },
                },
                "required": ["prompt"],
            },
        ),
        Tool(
            name="freepik_mystic_status",
            description="Fetch status/result for a Mystic generation task.",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {"type": "string", "description": "Mystic task id"},
                },
                "required": ["task_id"],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict):
    base_url = _get_env(FREEPIK_MYSTIC_URL_ENV)
    if name == "freepik_mystic_generate":
        payload = {
            "prompt": arguments["prompt"],
            "resolution": arguments.get("resolution"),
            "aspect_ratio": arguments.get("aspect_ratio"),
            "engine": arguments.get("engine"),
            "model": arguments.get("model"),
            "creative_detailing": arguments.get("creative_detailing"),
            "styling": arguments.get("styling"),
            "structure_reference": arguments.get("structure_reference"),
            "style_reference": arguments.get("style_reference"),
            "adherence": arguments.get("adherence"),
            "hdr": arguments.get("hdr"),
            "fixed_generation": arguments.get("fixed_generation"),
            "webhook_url": arguments.get("webhook_url"),
        }
        payload = {key: value for key, value in payload.items() if value is not None}
        if isinstance(arguments.get("params"), dict):
            payload.update(arguments["params"])
        try:
            data = await _post_to_freepik(base_url, payload)
            return [TextContent(type="text", text=json.dumps(data))]
        except Exception as exc:
            return [TextContent(type="text", text=f"Freepik error: {exc}")]
    if name == "freepik_mystic_status":
        task_id = arguments["task_id"]
        try:
            async with httpx.AsyncClient(timeout=60) as client:
                response = await client.get(
                    f"{base_url}/{task_id}",
                    headers={"x-freepik-api-key": _get_env(FREEPIK_API_KEY_ENV)},
                )
                response.raise_for_status()
                return [TextContent(type="text", text=json.dumps(response.json()))]
        except Exception as exc:
            return [TextContent(type="text", text=f"Freepik error: {exc}")]
    return [TextContent(type="text", text=f"Unknown tool: {name}")]


async def _run_smoke_test(
    poll_attempts: int = 0,
    poll_delay_s: float = 5.0,
    poll_until_complete: bool = False,
) -> None:
    result = await call_tool(
        "freepik_mystic_generate",
        {
            "prompt": "Minimalist fitness poster, modern typography, teal accents",
        },
    )
    print("Smoke test result:")
    task_id = None
    for item in result:
        text = getattr(item, "text", item)
        print(text)
        try:
            payload = json.loads(text)
            task_id = payload.get("data", {}).get("task_id")
        except Exception:
            continue

    if task_id and poll_attempts > 0:
        for attempt in range(1, poll_attempts + 1):
            await asyncio.sleep(poll_delay_s)
            status = await call_tool(
                "freepik_mystic_status",
                {"task_id": task_id},
            )
            print(f"Smoke test status attempt {attempt}:")
            for item in status:
                text = getattr(item, "text", item)
                print(text)
                if poll_until_complete:
                    try:
                        payload = json.loads(text)
                        if payload.get("data", {}).get("status") == "COMPLETED":
                            return
                    except Exception:
                        continue


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--smoke-test",
        action="store_true",
        help="Run a basic Freepik Mystic generation test and exit.",
    )
    parser.add_argument(
        "--smoke-poll-attempts",
        type=int,
        default=0,
        help="Number of status polls to perform after smoke test.",
    )
    parser.add_argument(
        "--smoke-poll-delay",
        type=float,
        default=5.0,
        help="Delay in seconds between smoke test status polls.",
    )
    parser.add_argument(
        "--smoke-poll-until-complete",
        action="store_true",
        help="Stop polling early when a COMPLETED status is returned.",
    )
    args = parser.parse_args()

    if args.smoke_test:
        asyncio.run(
            _run_smoke_test(
                poll_attempts=args.smoke_poll_attempts,
                poll_delay_s=args.smoke_poll_delay,
                poll_until_complete=args.smoke_poll_until_complete,
            )
        )
    else:
        server.run()
