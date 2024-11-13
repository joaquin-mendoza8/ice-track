#!/bin/bash

# Define color variables
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

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
    echo -e "${RED}You are currently on a protected branch ($CURRENT_BRANCH). Please switch to a feature branch before running this script.${NC}"
    exit 1
fi

# Fetch the latest changes from the remote repository
echo -e "${GREEN}Fetching the latest changes from the remote repository...${NC}"
git fetch origin

# Check if the fetch operation was successful
if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to fetch changes from the remote repository.${NC}"
    exit 1
fi

# Prompt the user to enter the dev branch name
read -p "Enter branch to update from (default: stage): " DEV_BRANCH_INPUT

# Name of the dev branch to update from
DEV_BRANCH="${DEV_BRANCH_INPUT:-stage}"

# Switch to the dev branch and pull the latest updates
echo -e "${GREEN}Switching to the $DEV_BRANCH branch and pulling the latest updates...${NC}"
git checkout $DEV_BRANCH
git pull origin $DEV_BRANCH

# Switch back to the current feature branch
echo -e "${GREEN}Switching back to the $CURRENT_BRANCH branch...${NC}"
git checkout $CURRENT_BRANCH

# Merge the dev branch into the current feature branch
echo -e "${GREEN}Merging $DEV_BRANCH into $CURRENT_BRANCH...${NC}"
git merge $DEV_BRANCH

# Check for merge conflicts
if [ $? -ne 0 ]; then
    echo -e "\e[31mMerge conflicts detected. Please resolve them and commit the changes.${NC}"
else
    echo -e "${GREEN}Merge completed successfully! Your feature branch is now up-to-date with $DEV_BRANCH.${NC}"
    echo -e "${GREEN}Please review the changes, test your code, and push the updates to the remote repository using 'git push'${NC}"
fi