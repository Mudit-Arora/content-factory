#!/usr/bin/env python3
"""Test script to run the content generation agent."""

import asyncio
import json
import sys
import tempfile
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from agent.agent import run_content_generation
from agent.tools import get_generated_content


async def main():
    """Run a test of the agent."""
    # Sample brand description
    brand_description = """
    Sustainable fashion brand targeting millennial women, focuses on eco-friendly
    materials and ethical manufacturing. Our aesthetic is minimalist with earthy
    tones and natural textures. We believe in slow fashion and quality over quantity.
    """.strip()

    # Create temporary output directory
    output_dir = Path(tempfile.gettempdir()) / "content-factory-test"
    output_dir.mkdir(exist_ok=True)

    print(f"🚀 Starting agent test...")
    print(f"📁 Output directory: {output_dir}")
    print(f"🏷️  Brand: {brand_description[:100]}...")
    print("-" * 80)

    # Run the agent
    result = await run_content_generation(
        brand_description=brand_description,
        output_dir=str(output_dir)
    )

    print("-" * 80)
    print(f"📊 Result status: {result['status']}")

    if result["status"] == "success":
        # Get the generated content
        content = get_generated_content()

        if content and "posts" in content:
            posts = content["posts"]
            print(f"✅ Successfully generated {len(posts)} posts!")
            print("\n📝 Generated Posts:")
            print("=" * 80)

            for post in posts:
                print(f"\n📌 Post {post['post_number']} - {post['day']}")
                print(f"   Topic: {post['topic']}")
                print(f"   Copy: {post['post_copy']}")
                print(f"   Hashtags: {post['hashtags']}")
                print(f"   Image URL: {post['image_url'][:80]}...")
                print(f"   Best time: {post['best_time_to_post']}")

            # Save to file
            output_file = output_dir / "test_results.json"
            with open(output_file, "w") as f:
                json.dump(content, f, indent=2)
            print(f"\n💾 Full results saved to: {output_file}")
        else:
            print("⚠️  No posts generated")
            print(f"Content: {content}")
    else:
        print(f"❌ Error: {result.get('error')}")
        if "traceback" in result:
            print(f"\nTraceback:\n{result['traceback']}")


if __name__ == "__main__":
    asyncio.run(main())
