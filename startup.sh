#!/bin/bash

# Add our app path to our path so that python imports work correctly
export PATH="${PATH}:/app"

# Initialize the DB if it doesn't exist yet
if [ ! -d "/app/instance/db.sqlite" ]; then
	python -m flask init-db
fi

# Start the bot
gunicorn --bind=0.0.0.0:8000 -w ${WORKERS:-1} 'tlapbot:create_app()'
