#!/bin/bash

# Comprehensive Resume Tools Test Runner
echo "🧪 Running Comprehensive Resume Tools Test..."
echo "=============================================="

# Activate virtual environment and run the test
source ../venv/bin/activate
python comprehensive_tool_test.py

# Exit with the Python script's exit code
exit $?
