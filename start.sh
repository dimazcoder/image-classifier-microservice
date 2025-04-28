#!/bin/bash

# List the contents of /app to verify files are present
echo "Listing contents of /app:"

# Create .env file from DEPLOY_ENV environment variable
echo "$DEPLOY_ENV" > /app/.env

# Check if .env file is created and its content
echo "Created /app/.env file with the following content:"

# Start the application
uvicorn app.main:app --host 0.0.0.0 --port 7776 --reload