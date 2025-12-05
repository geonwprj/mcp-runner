#!/bin/bash
set -e

if [ -z "$PYPI_URL" ]; then
    echo "Error: PYPI_URL environment variable is not set."
    exit 1
fi

echo "Installing service from $PYPI_URL..."
pip install "$PYPI_URL"

# Determine the module to run
if [ -z "$PYPY_MODEL" ]; then
    # Try to extract from URL (basic heuristic, might need adjustment based on actual URL format)
    # Assuming URL ends with /package-name-version.whl or similar, or just package name
    # This is a fallback and might be brittle.
    echo "Warning: PYPY_MODEL not set. Attempting to guess..."
    # For now, we'll just fail if not set, as guessing is risky without knowing URL format.
    echo "Error: PYPY_MODEL environment variable is not set."
    exit 1
else
    MODULE_NAME="$PYPY_MODEL"
fi

echo "Running module: $MODULE_NAME"
exec python -m "$MODULE_NAME"
