#!/bin/bash

# --- Function for error handling ---
handle_error() {
  # Added more context to the error message
  echo -e "\n\n*******************************************************"
  echo "Error: $1"
  echo "*******************************************************"
  exit 1
}

# --- Part 1: Create and Set Google Cloud Project ID ---
PROJECT_FILE="$HOME/project_id.txt"
CODELAB_PROJECT_PREFIX="agentverse-summoner"

echo "--- Creating and Setting Google Cloud Project ID ---"

# --- Dynamic Length Calculation ---
PREFIX_LEN=${#CODELAB_PROJECT_PREFIX}
if (( PREFIX_LEN > 25 )); then
  handle_error "The project prefix '$CODELAB_PROJECT_PREFIX' is too long (${PREFIX_LEN} chars). Maximum allowed is 25."
fi
MAX_SUFFIX_LEN=$(( 30 - PREFIX_LEN - 1 ))
echo "Project prefix '${CODELAB_PROJECT_PREFIX}' is ${PREFIX_LEN} chars. Suffix will be ${MAX_SUFFIX_LEN} chars."

# Loop until a project is successfully created.
while true; do
  RANDOM_SUFFIX=$(LC_ALL=C tr -dc 'a-z0-9' < /dev/urandom | head -c "$MAX_SUFFIX_LEN")
  SUGGESTED_PROJECT_ID="${CODELAB_PROJECT_PREFIX}-${RANDOM_SUFFIX}"

  read -p "Enter your project ID or press Enter to use the default: " -e -i "$SUGGESTED_PROJECT_ID" FINAL_PROJECT_ID

  if [[ -z "$FINAL_PROJECT_ID" ]]; then
      echo "Project ID cannot be empty. Please try again."
      continue
  fi

  echo "Attempting to create project with ID: $FINAL_PROJECT_ID"
  ERROR_OUTPUT=$(gcloud projects create "$FINAL_PROJECT_ID" --quiet 2>&1)
  CREATE_STATUS=$?

  if [[ $CREATE_STATUS -eq 0 ]]; then
    echo "Successfully created project: $FINAL_PROJECT_ID"
    gcloud config set project "$FINAL_PROJECT_ID" || handle_error "Failed to set active project to $FINAL_PROJECT_ID."
    echo "Set active gcloud project to $FINAL_PROJECT_ID."
    echo "$FINAL_PROJECT_ID" > "$PROJECT_FILE" || handle_error "Failed to save the project ID to $PROJECT_FILE."
    echo "Successfully saved project ID to $PROJECT_FILE."

    echo -e "\n--- Installing Python dependencies ---"
    pip install --upgrade --user google-cloud-billing || handle_error "Failed to install Python libraries."

    echo -e "\n--- Running the Billing Enablement Script ---"
    # Improved error message on failure
    python3 billing-enablement.py || handle_error "The billing enablement script failed. See the output above for details."
    break
  else
    echo "Could not create project '$FINAL_PROJECT_ID'."
    echo "Reason from gcloud: $ERROR_OUTPUT"
    echo -e "This ID might already be taken, or you may not have project creation permissions.\nPlease try a different project ID.\n"
  fi
done

echo -e "\n--- Full Setup Complete ---"
exit 0