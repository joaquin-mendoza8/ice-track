#! /bin/bash

# Count the lines of code in the ice-track directory (excluding certain directories)

# exclude the following directories
excludes="__pycache__,migrations,venv,instance,docs,"
include_exts="py,html,js,css,sh"

# count the lines of code
cloc . --exclude-dir=$excludes --include-ext=$include_exts