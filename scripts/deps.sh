#! /bin/bash

# Check if a venv is active
if [ -z "$VIRTUAL_ENV" ]; then
    # Print an error message
    echo -e "\nError: No virtual environment found\n"
    # Exit with an error code
    exit 1
else
    # Print a message
    echo -e "\nVirtual environment found...\n"
fi

# Check if the file "requirements.txt" exists
if [ -f requirements.txt ]; then
    # Install the dependencies
    echo -e "Installing dependencies...\n"
    pip install -r requirements.txt
else
    # Print an error message
    echo -e "Error: requirements.txt not found\n"
fi