#!/bin/bash
# Helper script to extract API key from .env

if [ -f .env ]; then
    # Try different patterns
    KEY=$(grep -E "^APP_API_KEY\s*=" .env 2>/dev/null | head -1 | sed 's/^[^=]*=//' | sed 's/^[[:space:]]*//' | sed 's/[[:space:]]*$//' | tr -d '"' | tr -d "'")
    
    if [ -n "$KEY" ]; then
        echo "$KEY"
    else
        echo "APP_API_KEY not found in .env" >&2
        exit 1
    fi
else
    echo ".env file not found" >&2
    exit 1
fi
