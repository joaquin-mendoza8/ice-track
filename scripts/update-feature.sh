#!/bin/bash

# List of branches to exclude
EXCLUDED_BRANCHES=("stage" "main" "integration")

# Get the current branch name
CURRENT_BRANCH=$(git branch --show-current)

# Function to check if the current branch is in the excluded list
is_excluded_branch() {
    for branch in "${EXCLUDED_BRANCHES[@]}"; do
    if [ "$CURRENT_BRANCH" = "$branch" ]; then
        return 0
    fi
    done
    return 1
}

# Check if the current branch is in the excluded list
if is_excluded_branch; then
    echo "You are currently on a protected branch ($CURRENT_BRANCH). Please switch to a feature branch before running this script."
    exit 1
fi

# Fetch the latest changes from the remote repository
echo "Fetching the latest changes from the remote repository..."
git fetch origin

# Name of the dev branch to update from
DEV_BRANCH="stage"

# Switch to the dev branch and pull the latest updates
echo "Switching to the $DEV_BRANCH branch and pulling the latest updates..."
git checkout $DEV_BRANCH
git pull origin $DEV_BRANCH

# Switch back to the current feature branch
echo "Switching back to the $CURRENT_BRANCH branch..."
git checkout $CURRENT_BRANCH

# Merge the dev branch into the current feature branch
echo "Merging $DEV_BRANCH into $CURRENT_BRANCH..."
git merge $DEV_BRANCH

# Check for merge conflicts
if [ $? -ne 0 ]; then
    echo "Merge conflicts detected. Please resolve them and commit the changes."
else
    echo "Merge completed successfully! Your feature branch is now up-to-date with $DEV_BRANCH."
fi