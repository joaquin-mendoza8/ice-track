#! /bin/bash

# Creates an Entity-Relationship Diagram (ERD) from the database as a PNG file

# check if a venv is active
if [ -z "$VIRTUAL_ENV" ]; then
    # print an error message
    echo -e "\nError: No virtual environment found\n"
    # exit with an error code
    exit 1
else
    # print a message
    echo -e "Virtual environment found..."
fi

# installs graphviz and erdalchemy if not already installed
pip install graphviz eralchemy -q

# get the path of the database
DB_PATH=$(find instance -name "*.db")

# check if the database exists
if [ -z "$DB_PATH" ]; then
    # print an error message
    echo -e "\nError: No database found\n"
    # exit with an error code
    exit 1
else
    # print a message
    echo -e "Database found..."
fi

# set a title string for the ERD
TITLE="Entity-Relationship Diagram"

# create the ERD
eralchemy --exclude-tables "alembic_version" --exclude-tables "sessions" -i sqlite:///$DB_PATH -o erd.png

# print a message
echo -e "ERD created..."
