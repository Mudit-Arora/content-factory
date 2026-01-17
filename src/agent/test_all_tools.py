#!/usr/bin/env python3
"""
Comprehensive test script for all API tools (Yutori + Freepik).

This script runs both Yutori and Freepik tests in sequence.

Usage:
    python -m src.agent.test_all_tools

Requirements:
    - YUTORI_API_KEY environment variable must be set
    - FREEPIK_API_KEY environment variable must be set
    - FREEPIK_MYSTIC_URL environment variable must be set
    - Run from project root directory
"""

import asyncio
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def check_environment():
    """Check if all required environment variables are set."""
    print("=" * 80)
    print("ENVIRONMENT CHECK")
    print("=" * 80 + "\n")
    
    required_vars = {
        "YUTORI_API_KEY": "Yutori API key",
        "FREEPIK_API_KEY": "Freepik API key",
        "FREEPIK_MYSTIC_URL": "Freepik Mystic URL",
    }
    
    missing_vars = []
    
    for var_name, description in required_vars.items():
        value = os.getenv(var_name)
        if value:
            # Show partial value for security
            masked_value = value[:8] + "..." if len(value) > 8 else "***"
            print(f"✅ {var_name}: {masked_value}")
        else:
            print(f"❌ {var_name}: NOT SET")
            missing_vars.append(var_name)
    
    print()
    
    if missing_vars:
        print("⚠️  Missing environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease set these variables in your .env file or environment.")
        return False
    
    print("✅ All required environment variables are set!\n")
    return True


async def run_yutori_tests():
    """Run Yutori tests."""
    print("\n" + "🔵" * 40)
    print("YUTORI TESTS")
    print("🔵" * 40 + "\n")
    
    try:
        from src.agent.test_yutori import main as yutori_main
        await yutori_main()
    except Exception as e:
        print(f"\n❌ Yutori tests failed: {e}")
        import traceback
        traceback.print_exc()


async def run_freepik_tests():
    """Run Freepik tests."""
    print("\n" + "🟢" * 40)
    print("FREEPIK TESTS")
    print("🟢" * 40 + "\n")
    
    try:
        from src.agent.test_freepik import main as freepik_main
        await freepik_main()
    except Exception as e:
        print(f"\n❌ Freepik tests failed: {e}")
        import traceback
        traceback.print_exc()


async def main():
    """Run all tests."""
    print("\n" + "🧪" * 40)
    print("COMPLETE API TOOLS TEST SUITE")
    print("🧪" * 40 + "\n")
    
    # Check environment
    if not check_environment():
        print("\n❌ Environment check failed. Exiting.")
        sys.exit(1)
    
    # Run tests
    await run_yutori_tests()
    await run_freepik_tests()
    
    print("\n" + "=" * 80)
    print("ALL TESTS COMPLETED")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
