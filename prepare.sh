#!/bin/bash

# This script prepares the entire Google Cloud environment for The Summoner's Concord workshop.
# It provisions Cloud SQL, a fake API on Cloud Run, and sets all necessary permissions.
# It relies on environment variables set by 'set_env.sh'.


# --- 2. Generate Dynamic Secrets ---
# The database password is created dynamically each time for security.
export DB_PASSWORD=1234qwer

# --- 3. Define Prerequisite Directory ---
export PREREQ_DIR="prerequisite"

# --- 4. Create Cloud SQL Instance (The Librarium) ---
echo "--> Checking for Cloud SQL instance '${DB_INSTANCE_NAME}'..."
if ! gcloud sql instances describe ${DB_INSTANCE_NAME} &> /dev/null; then
    echo "Creating Cloud SQL PostgreSQL instance '${DB_INSTANCE_NAME}'..."
    gcloud sql instances create ${DB_INSTANCE_NAME} \
        --database-version=POSTGRES_15 \
        --region=${REGION} \
        --tier=db-g1-small \
        --root-password="${DB_PASSWORD}"
    echo "Instance created. This can take a few minutes to be ready..."
else
    echo "Cloud SQL instance '${DB_INSTANCE_NAME}' already exists."
fi

# --- 5. Create Database and User inside the Instance ---
echo "--> Creating database '${DB_NAME}' and user '${DB_USER}'..."
gcloud sql databases create ${DB_NAME} --instance=${DB_INSTANCE_NAME} || echo "Database '${DB_NAME}' may already exist. Continuing."
gcloud sql users create ${DB_USER} --instance=${DB_INSTANCE_NAME} --password="${DB_PASSWORD}" || echo "User '${DB_USER}' may already exist. Setting password."
gcloud sql users set-password ${DB_USER} --instance=${DB_INSTANCE_NAME} --password="${DB_PASSWORD}"


# --- 6. Create and Activate Python Virtual Environment ---
echo "--> Preparing Python virtual environment..."
if [ ! -d "env" ]; then
    echo "Creating virtual environment 'env'..."
    python -m venv env
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

# --- 8. Deploy Fake API Server (The Nexus) ---
echo "--> Deploying the 'Nexus of Whispers' fake API to Cloud Run..."
gcloud builds submit "${PREREQ_DIR}/fake_api/" \
    --config "${PREREQ_DIR}/fake_api/cloudbuild.yaml" \
    --substitutions=_REGION="${REGION}",_REPO_NAME="${REPO_NAME}",_SERVICE_NAME="${FAKE_API_SERVICE_NAME}"

FAKE_API_URL=$(gcloud run services describe ${FAKE_API_SERVICE_NAME} --platform=managed --region=${REGION} --format='value(status.url)')

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
echo "Database Password:        ${DB_PASSWORD}  
echo
echo "Your Nexus of Whispers (Fake API) is live:"
echo "------------------------------------------"
echo "API Base URL:             ${FAKE_API_URL}"
echo
echo "Save these details. You will need them to configure your MCP servers."
echo "========================================================================"