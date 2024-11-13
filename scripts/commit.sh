#! /bin/bash

# Check if git changes exist
if [ -z "$(git status --porcelain)" ]; then
    # Print a message
    echo -e "\nNo changes to push\n"
    # Exit with an error code
    exit 1
else
    # Print a message
    echo -e "\nChanges found...\n"
fi

# Run an update to requirements.txt
echo "Updating requirements.txt..."
pip list --outdated --format=columns | tail -n +3 | awk '{print $1}' | xargs pip install -U

# Update the requirements.txt file
pip freeze > requirements.txt

# Add all changes to the staging area
git add .

# get user input for a commit message
echo -e "Enter a commit message: "

# Read the user input
read -r

# Commit the changes
git commit -m "$REPLY"

