#!/bin/bash

# --- Pre-flight Check: Ensure Environment is Set ---
echo "--> Verifying required environment variables..."
if [ -z "${DB_INSTANCE_NAME}" ] || [ -z "${PROJECT_ID}" ] || [ -z "${REGION}" ]; then
    echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
    echo "!!! ERROR: Required environment variables are not set."
    echo "!!! The script cannot continue without knowing the Cloud SQL instance,"
    echo "!!! project ID, and region."
    echo "!!!"
    echo "!!! Please run 'source ./set_env.sh' to set them and try again."
    echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
    exit 1
else
    echo "Environment variables look good. Proceeding..."
fi


export PREREQ_DIR="prerequisite"

# --- 5. Create Database and User inside the Instance ---
echo "--> Creating database '${DB_NAME}' and user '${DB_USER}'..."
# The '|| echo' construct handles cases where the database or user already exists, preventing the script from stopping.
gcloud sql databases create ${DB_NAME} --instance=${DB_INSTANCE_NAME} --project=${PROJECT_ID} || echo "Database '${DB_NAME}' may already exist. Continuing."
gcloud sql users create ${DB_USER} --instance=${DB_INSTANCE_NAME} --password="${DB_PASSWORD}" --project=${PROJECT_ID} || echo "User '${DB_USER}' may already exist. Continuing."
# This command ensures the password is set, even if the user already existed.
gcloud sql users set-password ${DB_USER} --instance=${DB_INSTANCE_NAME} --password="${DB_PASSWORD}" --project=${PROJECT_ID}


# --- 6. Create and Activate Python Virtual Environment ---
echo "--> Preparing Python virtual environment..."
if [ ! -d "env" ]; then
    echo "Creating virtual environment 'env'..."
    python3 -m venv env
else
    echo "Virtual environment 'env' already exists."
fi

echo "Activating virtual environment..."
source env/bin/activate


# --- 7. Populate Database with Lore ---
echo "--> Installing Python dependencies for DB setup..."
pip install -r "${PREREQ_DIR}/requirements-setup.txt" --quiet

echo "--> Running Python script to populate the Librarium..."
# Pass required env vars to the Python script
(export GCP_PROJECT_ID=$PROJECT_ID; export GCP_REGION=$REGION; cd "${PREREQ_DIR}" && python db_setup.py)


# --- Final Output ---
echo
echo "========================================================================"
echo "✅ Summoner's Environment Preparation Complete!"
echo "========================================================================"
echo
echo "Your Librarium of Knowledge (Cloud SQL DB) is ready:"
echo "----------------------------------------------------"
echo "Instance Connection Name: ${PROJECT_ID}:${REGION}:${DB_INSTANCE_NAME}"
echo "Database Name:            ${DB_NAME}"
echo "Database User:            ${DB_USER}"
echo "Database Password:        ${DB_PASSWORD}"
echo
echo "Your Nexus of Whispers (Fake API) is live:"
echo "------------------------------------------"
echo "API Base URL:             ${FAKE_API_URL}"
echo
echo "Save these details. You will need them to configure your MCP servers."
echo "========================================================================"