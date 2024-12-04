# ! /bin/bash

# Script to attempt to update the alembic database by creating a new migration and upgrading the database

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

# check if the migrations and instance directories exist
if [ ! -d "migrations" ] || [ ! -d "instance" ]; then
    # print an error message
    echo -e "\nError: No alembic database found\n"
    # exit with an error code
    exit 1
else
    # print a message
    echo -e "Alembic database found..."
fi

# set the base alembic command
ALEMBIC_CMD="flask --app app.app db"

# create a new migration (get user input for the migration message)
echo -e "\nCreating a new migration..."
echo -e "Enter a message for the migration:"
read MIGRATION_MESSAGE
$ALEMBIC_CMD migrate -m "$MIGRATION_MESSAGE"

# check if the migration was successful
if [ $? -eq 0 ]; then
    # print a message
    echo -e "Migration successful..."
    # upgrade the database
    echo -e "\nUpgrading the database..."
    $ALEMBIC_CMD upgrade
    # print a message
    echo -e "Database upgraded..."
else
    # print an error message
    echo -e "\nError: Migration failed\n"
    # exit with an error code
    exit 1
fi