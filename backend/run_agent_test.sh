#!/bin/bash

# Agent Database Change Validation Runner
echo "🧪 Running Agent Database Change Validation..."
echo "=============================================="

# Activate virtual environment and run the test
source ../venv/bin/activate
python test_agent_database_changes.py

# Exit with the Python script's exit code
exit $?
