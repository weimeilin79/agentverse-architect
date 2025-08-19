#!/bin/bash

# This script prepares the entire Google Cloud environment for The Summoner's Concord workshop.
# It provisions Cloud SQL, a fake API on Cloud Run, and sets all necessary permissions.
# It relies on environment variables set by 'set_env.sh'.

export PREREQ_DIR="prerequisite"

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


# --- 2. Deploy Fake API Server (The Nexus) ---
echo "--> Deploying the 'Nexus of Whispers' fake API to Cloud Run..."
gcloud builds submit "${PREREQ_DIR}/fake_api/" \
    --project=${PROJECT_ID} \
    --config "${PREREQ_DIR}/fake_api/cloudbuild.yaml" \
    --substitutions=_REGION="${REGION}",_REPO_NAME="${REPO_NAME}",_SERVICE_NAME="${FAKE_API_SERVICE_NAME}"

# Retrieve the URL after deployment. Redirect error to /dev/null if service is not found yet.
FAKE_API_URL=$(gcloud run services describe ${FAKE_API_SERVICE_NAME} --platform=managed --region=${REGION} --format='value(status.url)' --project=${PROJECT_ID} 2>/dev/null || true)


echo ""
echo "------------------------------------------------------------"
echo "✅ Environment preparation complete!"
echo ""
echo "Nexus of Whispers API URL: ${FAKE_API_URL}"
echo "Librarium (Cloud SQL) Instance: ${DB_INSTANCE_NAME}"
echo "------------------------------------------------------------"