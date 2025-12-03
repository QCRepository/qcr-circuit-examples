#!/bin/bash

# Test script for validating requirements.txt and requirements.lock files
# Usage: ./test_requirements.sh [--lock] [--run] [example_name]
#   --lock    Use requirements.lock instead of requirements.txt
#   --run     Also run example.py after installation
#   example_name  Test only specific example (e.g., "grover")

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Parse arguments
USE_LOCK=false
RUN_EXAMPLE=false
SPECIFIC_EXAMPLE=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --lock)
            USE_LOCK=true
            shift
            ;;
        --run)
            RUN_EXAMPLE=true
            shift
            ;;
        *)
            SPECIFIC_EXAMPLE="$1"
            shift
            ;;
    esac
done

# Determine which requirements file to use
if [ "$USE_LOCK" = true ]; then
    REQ_FILE="requirements.lock"
else
    REQ_FILE="requirements.txt"
fi

echo "========================================"
echo "Testing Circuit Examples Requirements"
echo "========================================"
echo "Using: $REQ_FILE"
echo "Run examples: $RUN_EXAMPLE"
echo ""

# Get repository root (script is in .github/scripts/)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

# Find all example directories (directories containing example.py)
if [ -n "$SPECIFIC_EXAMPLE" ]; then
    EXAMPLES=$(find "$SCRIPT_DIR" -type d -name "$SPECIFIC_EXAMPLE" 2>/dev/null)
    if [ -z "$EXAMPLES" ]; then
        echo -e "${RED}Example '$SPECIFIC_EXAMPLE' not found${NC}"
        exit 1
    fi
else
    EXAMPLES=$(find "$SCRIPT_DIR" -name "example.py" -type f | xargs -I {} dirname {} | sort -u)
fi

# Counters
TOTAL=0
PASSED=0
FAILED=0
FAILED_LIST=""

# Test each example
for example_dir in $EXAMPLES; do
    example_name=$(echo "$example_dir" | sed "s|$SCRIPT_DIR/||")
    TOTAL=$((TOTAL + 1))

    echo "----------------------------------------"
    echo -e "${YELLOW}Testing: $example_name${NC}"

    cd "$example_dir"

    # Check if requirements file exists
    if [ ! -f "$REQ_FILE" ]; then
        echo -e "${RED}  ✗ Missing $REQ_FILE${NC}"
        FAILED=$((FAILED + 1))
        FAILED_LIST="$FAILED_LIST\n  - $example_name (missing $REQ_FILE)"
        continue
    fi

    # Check if .python-version exists
    if [ ! -f ".python-version" ]; then
        echo -e "${YELLOW}  ⚠ Missing .python-version${NC}"
    fi

    # Create virtual environment
    echo "  Creating virtual environment..."
    python3 -m venv .test_venv 2>/dev/null || {
        echo -e "${RED}  ✗ Failed to create venv${NC}"
        FAILED=$((FAILED + 1))
        FAILED_LIST="$FAILED_LIST\n  - $example_name (venv creation failed)"
        continue
    }

    # Activate and install
    source .test_venv/bin/activate

    echo "  Installing dependencies..."
    pip install --upgrade pip -q
    if pip install -r "$REQ_FILE" -q 2>/dev/null; then
        echo -e "${GREEN}  ✓ Dependencies installed${NC}"

        # Test imports based on requirements
        echo "  Testing imports..."
        IMPORT_OK=true

        if grep -q "qiskit" "$REQ_FILE"; then
            python -c "import qiskit; print(f'    qiskit {qiskit.__version__}')" 2>/dev/null || IMPORT_OK=false
        fi

        if grep -q "qiskit-aer" "$REQ_FILE"; then
            python -c "from qiskit_aer import AerSimulator; print('    qiskit-aer OK')" 2>/dev/null || IMPORT_OK=false
        fi

        if grep -q "piquasso" "$REQ_FILE"; then
            python -c "import piquasso; print(f'    piquasso {piquasso.__version__}')" 2>/dev/null || IMPORT_OK=false
        fi

        if grep -q "scipy" "$REQ_FILE"; then
            python -c "import scipy; print(f'    scipy {scipy.__version__}')" 2>/dev/null || IMPORT_OK=false
        fi

        if grep -q "numpy" "$REQ_FILE"; then
            python -c "import numpy; print(f'    numpy {numpy.__version__}')" 2>/dev/null || IMPORT_OK=false
        fi

        if [ "$IMPORT_OK" = true ]; then
            echo -e "${GREEN}  ✓ Imports successful${NC}"

            # Optionally run example
            if [ "$RUN_EXAMPLE" = true ] && [ -f "example.py" ]; then
                echo "  Running example.py..."
                if timeout 60 python example.py > /dev/null 2>&1; then
                    echo -e "${GREEN}  ✓ Example ran successfully${NC}"
                    PASSED=$((PASSED + 1))
                else
                    echo -e "${RED}  ✗ Example failed to run${NC}"
                    FAILED=$((FAILED + 1))
                    FAILED_LIST="$FAILED_LIST\n  - $example_name (example.py failed)"
                fi
            else
                PASSED=$((PASSED + 1))
            fi
        else
            echo -e "${RED}  ✗ Import test failed${NC}"
            FAILED=$((FAILED + 1))
            FAILED_LIST="$FAILED_LIST\n  - $example_name (import failed)"
        fi
    else
        echo -e "${RED}  ✗ Installation failed${NC}"
        FAILED=$((FAILED + 1))
        FAILED_LIST="$FAILED_LIST\n  - $example_name (pip install failed)"
    fi

    # Cleanup
    deactivate
    rm -rf .test_venv

    cd "$SCRIPT_DIR"
done

# Summary
echo ""
echo "========================================"
echo "SUMMARY"
echo "========================================"
echo "Total:  $TOTAL"
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"

if [ $FAILED -gt 0 ]; then
    echo ""
    echo "Failed examples:"
    echo -e "$FAILED_LIST"
    exit 1
else
    echo ""
    echo -e "${GREEN}All tests passed!${NC}"
    exit 0
fi
