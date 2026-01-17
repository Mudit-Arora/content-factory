#!/usr/bin/env python3
"""
Test script for Yutori API tools in isolation.

This script tests the yutori_scrape_trends and yutori_research_status tools
without requiring the full agent setup.

Usage:
    python -m src.agent.test_yutori

Requirements:
    - YUTORI_API_KEY environment variable must be set
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

from src.agent.tools import yutori_scrape_trends, yutori_research_status


async def test_yutori_scrape_trends():
    """Test the yutori_scrape_trends tool with a sample query."""
    print("=" * 80)
    print("TEST: yutori_scrape_trends")
    print("=" * 80)
    
    # Check if API key is set
    if not os.getenv("YUTORI_API_KEY"):
        print("❌ ERROR: YUTORI_API_KEY environment variable not set")
        print("   Please set it in your .env file or environment")
        return None
    
    # Test query
    test_query = "sustainable fashion trends 2024"
    num_results = 5
    
    print(f"\n📝 Test Query: '{test_query}'")
    print(f"📊 Number of results: {num_results}")
    print("\n🔄 Calling yutori_scrape_trends...\n")
    
    try:
        # Call the tool
        result_str = await yutori_scrape_trends.ainvoke({
            "query": test_query,
            "num_results": num_results
        })
        
        # Parse the JSON response
        result = json.loads(result_str)
        
        print("\n✅ Response received:")
        print(json.dumps(result, indent=2))
        
        # Check for errors
        if "error" in result:
            print(f"\n❌ API returned an error: {result['error']}")
            return None
        
        # Extract task_id if present
        task_id = result.get("task_id") or result.get("id")
        if task_id:
            print(f"\n✅ Task created successfully!")
            print(f"📋 Task ID: {task_id}")
            return task_id
        else:
            print("\n⚠️  Warning: No task_id found in response")
            return None
            
    except Exception as e:
        print(f"\n❌ Exception occurred: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return None


async def test_yutori_research_status(task_id: str):
    """Test the yutori_research_status tool with a task ID."""
    print("\n" + "=" * 80)
    print("TEST: yutori_research_status")
    print("=" * 80)
    
    print(f"\n📋 Task ID: {task_id}")
    print("\n🔄 Checking task status...\n")
    
    max_attempts = 10
    wait_seconds = 5
    
    for attempt in range(1, max_attempts + 1):
        try:
            print(f"Attempt {attempt}/{max_attempts}...")
            
            # Call the tool
            result_str = await yutori_research_status.ainvoke({
                "task_id": task_id
            })
            
            # Parse the JSON response
            result = json.loads(result_str)
            
            # Check for errors
            if "error" in result:
                print(f"❌ API returned an error: {result['error']}")
                break
            
            # Get status
            status = result.get("status", "unknown")
            print(f"   Status: {status}")
            
            # Check if completed
            if status == "succeeded":
                print("\n✅ Task completed successfully!")
                print("\n📊 Results:")
                print(json.dumps(result, indent=2))
                
                # Try to extract and display trends
                if "result" in result:
                    trends_data = result["result"]
                    if isinstance(trends_data, dict) and "trends" in trends_data:
                        trends = trends_data["trends"]
                        print(f"\n📈 Found {len(trends)} trends:")
                        for i, trend in enumerate(trends, 1):
                            print(f"\n  {i}. {trend.get('title', 'N/A')}")
                            print(f"     Description: {trend.get('description', 'N/A')[:100]}...")
                            print(f"     URL: {trend.get('url', 'N/A')}")
                            if 'relevance_score' in trend:
                                print(f"     Relevance: {trend['relevance_score']}")
                break
            
            elif status == "failed":
                print("\n❌ Task failed!")
                print(json.dumps(result, indent=2))
                break
            
            elif status in ["queued", "running"]:
                if attempt < max_attempts:
                    print(f"   ⏳ Task still processing. Waiting {wait_seconds} seconds...\n")
                    await asyncio.sleep(wait_seconds)
                else:
                    print(f"\n⚠️  Task still processing after {max_attempts} attempts")
                    print("   Final status:")
                    print(json.dumps(result, indent=2))
            
            else:
                print(f"\n⚠️  Unknown status: {status}")
                print(json.dumps(result, indent=2))
                break
                
        except Exception as e:
            print(f"\n❌ Exception occurred: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            break


async def main():
    """Run all Yutori tests."""
    print("\n" + "🧪" * 40)
    print("YUTORI API TOOLS TEST SUITE")
    print("🧪" * 40 + "\n")
    
    # Test 1: Scrape trends
    task_id = await test_yutori_scrape_trends()
    
    # Test 2: Check status (only if we got a task_id)
    if task_id:
        await test_yutori_research_status(task_id)
    else:
        print("\n⚠️  Skipping status check test (no task_id from previous test)")
    
    print("\n" + "=" * 80)
    print("TEST SUITE COMPLETED")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
