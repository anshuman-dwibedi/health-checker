#!/bin/bash

set -euo pipefail
trap 'echo "Error on line no: $LINENO -> Command failed: $BASH_COMMAND"; exit 1' ERR

# Get the absolute directory of where this script is located
SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)
CONFIG_FILE="$SCRIPT_DIR/src/python/config.json"

create_config_file() {
    if ! command -v python3 &> /dev/null; then
        echo "Error: Python 3 is not installed. Exiting."
        exit 1
    fi
    echo "Creating configuration file..."
    python3 "$SCRIPT_DIR/src/python/create_config.py"
}

# 1. Check if the specific config file exists
if [[ ! -f "$CONFIG_FILE" ]]; then
    echo "Config not found at $CONFIG_FILE. Searching project directory..."
    
    # 2. Search for any config.json starting from the script's root directory
    # -maxdepth 4 prevents searching the entire OS if things go sideways
    directory_search_res=$(find "$SCRIPT_DIR" -maxdepth 4 -name "config.json" -print -quit)

    if [[ -z "$directory_search_res" ]]; then
        echo "Config file not found in project. Initiating creation..."
        create_config_file
        # Re-verify path after creation
        CONFIG_FILE="$SCRIPT_DIR/src/python/config.json"
    else
        CONFIG_FILE="$directory_search_res"
        echo "Found config at: $CONFIG_FILE"
    fi
fi

echo "Running Health Checker using config: $CONFIG_FILE"

# The 'if' statement automatically handles the exit code without triggering 'set -e'
if python3 "$SCRIPT_DIR/src/python/health-checker.py"; then
    # This block runs if exit code is 0
    echo "------------------------------------------------"
    echo "SUCCESS: Health check returned exit code 0"
    
    if [[ -f "$SCRIPT_DIR/src/python/temp.txt" ]]; then
        LOG_FILE=$(cat "$SCRIPT_DIR/src/python/temp.txt")
        echo "Log Location: $LOG_FILE"
    fi
    echo "------------------------------------------------"
else
    EXIT_CODE=$?
    echo "------------------------------------------------"
    echo "FAILURE: Health check failed with exit code $EXIT_CODE"
    echo "------------------------------------------------"
    exit $EXIT_CODE
fi
