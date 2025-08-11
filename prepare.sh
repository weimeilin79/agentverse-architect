#!/bin/bash

# This script prepares the entire Google Cloud environment for The Summoner's Concord workshop.
# It provisions Cloud SQL, a fake API on Cloud Run, and sets all necessary permissions.
# It relies on environment variables set by 'set_env.sh'.


# --- 3. Define Prerequisite Directory ---


# --- 1. Create Cloud SQL Instance (The Librarium) ---

gcloud sql instances describe $INSTANCE_NAME --project=$PROJECT_ID >/dev/null 2>&1

if [ $? -eq 0 ]; then
  echo "    Instance '$DB_INSTANCE_NAME' already exists. Skipping creation."
else
    gcloud sql instances create ${DB_INSTANCE_NAME} \
        --database-version=POSTGRES_16 \
        --region=${REGION} \
        --tier=db-g1-small \
        --root-password="${DB_PASSWORD}" \
        --edition=enterprise > /dev/null 2>&1 &
    # Capture the Process ID (PID) of the background job
    SQL_PID=$!
    echo "    Creation of '$DB_INSTANCE_NAME' started in the background (PID: $SQL_PID)."
fi
echo ""
