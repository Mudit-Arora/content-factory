#!/usr/bin/env python3
"""
Test script for Freepik API tools in isolation.

This script tests the freepik_generate_image and freepik_check_status tools
without requiring the full agent setup.

Usage:
    python -m src.agent.test_freepik

Requirements:
    - FREEPIK_API_KEY environment variable must be set
    - FREEPIK_MYSTIC_URL environment variable must be set
    - Run from project root directory
"""

import asyncio
import json
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from src.agent.tools import freepik_generate_image, freepik_check_status


async def test_freepik_generate_image():
    """Test the freepik_generate_image tool with a sample prompt."""
    print("=" * 80)
    print("TEST: freepik_generate_image")
    print("=" * 80)
    
    # Check if API key is set
    if not os.getenv("FREEPIK_API_KEY"):
        print("❌ ERROR: FREEPIK_API_KEY environment variable not set")
        print("   Please set it in your .env file or environment")
        return None
    
    if not os.getenv("FREEPIK_MYSTIC_URL"):
        print("❌ ERROR: FREEPIK_MYSTIC_URL environment variable not set")
        print("   Please set it in your .env file or environment")
        return None
    
    # Test prompt
    test_prompt = (
        "A modern minimalist Instagram post featuring sustainable fashion. "
        "Show eco-friendly clothing on a clean white background with natural lighting. "
        "Professional photography style, high quality, trendy aesthetic."
    )
    aspect_ratio = "square_1_1"  # Freepik format
    
    print(f"\n📝 Test Prompt: '{test_prompt}'")
    print(f"📐 Aspect Ratio: {aspect_ratio}")
    print("\n🔄 Calling freepik_generate_image...\n")
    
    try:
        # Call the tool
        result_str = await freepik_generate_image.ainvoke({
            "prompt": test_prompt,
            "aspect_ratio": aspect_ratio
        })
        
        # Parse the JSON response
        result = json.loads(result_str)
        
        print("\n✅ Response received:")
        print(json.dumps(result, indent=2))
        
        # Check for errors
        if "error" in result:
            print(f"\n❌ API returned an error: {result['error']}")
            return None
        
        # Extract task_id (Freepik nests it in data object)
        task_id = result.get("task_id") or result.get("id") or result.get("taskId")
        if not task_id and "data" in result and isinstance(result["data"], dict):
            task_id = result["data"].get("task_id") or result["data"].get("id")
        if task_id:
            print(f"\n✅ Image generation task created successfully!")
            print(f"📋 Task ID: {task_id}")
            return task_id
        else:
            print("\n⚠️  Warning: No task_id found in response")
            print("   Response keys:", list(result.keys()))
            return None
            
    except Exception as e:
        print(f"\n❌ Exception occurred: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return None


async def test_freepik_check_status(task_id: str):
    """Test the freepik_check_status tool with a task ID."""
    print("\n" + "=" * 80)
    print("TEST: freepik_check_status")
    print("=" * 80)
    
    print(f"\n📋 Task ID: {task_id}")
    print("\n🔄 Checking task status...\n")
    
    max_attempts = 20  # Freepik might take longer
    wait_seconds = 5
    
    for attempt in range(1, max_attempts + 1):
        try:
            print(f"Attempt {attempt}/{max_attempts}...")
            
            # Call the tool
            result_str = await freepik_check_status.ainvoke({
                "task_id": task_id
            })
            
            # Parse the JSON response
            result = json.loads(result_str)
            
            # Check for errors
            if "error" in result:
                print(f"❌ API returned an error: {result['error']}")
                break
            
            # Get status (Freepik nests status in data object)
            status = result.get("status", "unknown")
            if status == "unknown" and "data" in result and isinstance(result["data"], dict):
                status = result["data"].get("status", "unknown")
            print(f"   Status: {status}")
            
            # Check if completed
            if status in ["COMPLETED", "completed", "succeeded", "success"]:
                print("\n✅ Image generation completed successfully!")
                print("\n📊 Full Response:")
                print(json.dumps(result, indent=2))
                
                # Try to extract image URL (Freepik returns array in data.generated)
                image_url = None
                if "image_url" in result:
                    image_url = result["image_url"]
                elif "url" in result:
                    image_url = result["url"]
                elif "data" in result and isinstance(result["data"], dict):
                    data = result["data"]
                    # Check for generated array
                    if "generated" in data and isinstance(data["generated"], list) and len(data["generated"]) > 0:
                        image_url = data["generated"][0]
                    else:
                        image_url = data.get("url") or data.get("image_url")
                elif "result" in result and isinstance(result["result"], dict):
                    image_url = result["result"].get("url") or result["result"].get("image_url")
                
                if image_url:
                    print(f"\n🖼️  Image URL: {image_url}")
                else:
                    print("\n⚠️  Could not find image URL in response")
                    print("   Available keys:", list(result.keys()))
                break
            
            elif status in ["FAILED", "failed", "error"]:
                print("\n❌ Image generation failed!")
                print(json.dumps(result, indent=2))
                break
            
            elif status in ["PENDING", "pending", "PROCESSING", "processing", "queued", "running"]:
                if attempt < max_attempts:
                    print(f"   ⏳ Image still generating. Waiting {wait_seconds} seconds...\n")
                    await asyncio.sleep(wait_seconds)
                else:
                    print(f"\n⚠️  Image still processing after {max_attempts} attempts")
                    print("   Final status:")
                    print(json.dumps(result, indent=2))
            
            else:
                print(f"\n⚠️  Unknown status: {status}")
                print(json.dumps(result, indent=2))
                
                # Still wait and retry for unknown status
                if attempt < max_attempts:
                    print(f"   ⏳ Retrying in {wait_seconds} seconds...\n")
                    await asyncio.sleep(wait_seconds)
                else:
                    break
                
        except Exception as e:
            print(f"\n❌ Exception occurred: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            break


async def test_multiple_aspect_ratios():
    """Test image generation with different aspect ratios."""
    print("\n" + "=" * 80)
    print("TEST: Multiple Aspect Ratios")
    print("=" * 80)
    
    aspect_ratios = ["square_1_1", "widescreen_16_9", "social_story_9_16", "classic_4_3"]
    test_prompt = "A beautiful sunset over mountains, professional photography"
    
    print(f"\n📝 Test Prompt: '{test_prompt}'")
    print(f"📐 Testing aspect ratios: {', '.join(aspect_ratios)}\n")
    
    for ratio in aspect_ratios:
        print(f"\n--- Testing {ratio} ---")
        try:
            result_str = await freepik_generate_image.ainvoke({
                "prompt": test_prompt,
                "aspect_ratio": ratio
            })
            result = json.loads(result_str)
            
            if "error" in result:
                print(f"❌ Error for {ratio}: {result['error']}")
            else:
                task_id = result.get("task_id") or result.get("id") or result.get("taskId")
                if task_id:
                    print(f"✅ Task created for {ratio}: {task_id}")
                else:
                    print(f"⚠️  No task_id for {ratio}")
        except Exception as e:
            print(f"❌ Exception for {ratio}: {e}")
        
        # Small delay between requests
        await asyncio.sleep(1)


async def main():
    """Run all Freepik tests."""
    print("\n" + "🧪" * 40)
    print("FREEPIK API TOOLS TEST SUITE")
    print("🧪" * 40 + "\n")
    
    # Test 1: Generate image
    task_id = await test_freepik_generate_image()
    
    # Test 2: Check status (only if we got a task_id)
    if task_id:
        await test_freepik_check_status(task_id)
    else:
        print("\n⚠️  Skipping status check test (no task_id from previous test)")
    
    # Test 3: Multiple aspect ratios (optional, commented out by default)
    # Uncomment to test different aspect ratios
    # print("\n")
    # await test_multiple_aspect_ratios()
    
    print("\n" + "=" * 80)
    print("TEST SUITE COMPLETED")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
