#! /bin/bash

# Count the lines of code in the ice-track directory (excluding certain directories)

# exclude the following directories
excludes="__pycache__,migrations,venv,instance,docs"

# count the lines of code
cloc . --exclude-dir=$excludes