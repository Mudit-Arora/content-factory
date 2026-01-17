#!/bin/bash
# Convenience script to run API tool tests
# Usage: ./src/agent/run_tests.sh [yutori|freepik|all]

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Get the project root directory (2 levels up from this script)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/../.." && pwd )"

# Change to project root
cd "$PROJECT_ROOT"

echo -e "${BLUE}Project root: $PROJECT_ROOT${NC}"
echo ""

# Parse command line argument
TEST_TYPE="${1:-all}"

case "$TEST_TYPE" in
    yutori)
        echo -e "${GREEN}Running Yutori tests...${NC}"
        python -m src.agent.test_yutori
        ;;
    freepik)
        echo -e "${GREEN}Running Freepik tests...${NC}"
        python -m src.agent.test_freepik
        ;;
    all)
        echo -e "${GREEN}Running all API tool tests...${NC}"
        python -m src.agent.test_all_tools
        ;;
    *)
        echo -e "${RED}Invalid test type: $TEST_TYPE${NC}"
        echo ""
        echo "Usage: $0 [yutori|freepik|all]"
        echo ""
        echo "Examples:"
        echo "  $0           # Run all tests (default)"
        echo "  $0 all       # Run all tests"
        echo "  $0 yutori    # Run only Yutori tests"
        echo "  $0 freepik   # Run only Freepik tests"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}✅ Tests completed!${NC}"
