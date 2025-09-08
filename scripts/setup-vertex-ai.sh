#!/bin/bash

echo "Setting up Google Cloud Vertex AI for TherapyBot..."

# Check if gcloud CLI is installed
if ! command -v gcloud &> /dev/null; then
    echo "Error: Google Cloud CLI is not installed."
    echo "Please install it from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Check if project ID is provided
if [ -z "$1" ]; then
    echo "Usage: $0 <PROJECT_ID>"
    echo "Example: $0 my-therapybot-project"
    exit 1
fi

PROJECT_ID=$1
SERVICE_ACCOUNT_NAME="therapybot-vertex-ai"
KEY_FILE="./secrets/gcp-credentials.json"

echo "Project ID: $PROJECT_ID"
echo "Service Account: $SERVICE_ACCOUNT_NAME"

# Set the project
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "Enabling required APIs..."
gcloud services enable aiplatform.googleapis.com
gcloud services enable compute.googleapis.com

# Create service account
echo "Creating service account..."
gcloud iam service-accounts create $SERVICE_ACCOUNT_NAME \
    --description="Service account for TherapyBot Vertex AI" \
    --display-name="TherapyBot Vertex AI"

# Grant necessary roles
echo "Granting roles..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/aiplatform.user"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/ml.developer"

# Create and download key
echo "Creating service account key..."
gcloud iam service-accounts keys create $KEY_FILE \
    --iam-account="$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com"

# Update .env file
echo "Updating .env file..."
sed -i "s/GCP_PROJECT_ID=.*/GCP_PROJECT_ID=$PROJECT_ID/" .env

echo ""
echo "✅ Vertex AI setup complete!"
echo ""
echo "Next steps:"
echo "1. Update your .env file with the correct PROJECT_ID"
echo "2. Run: docker compose up -d --build"
echo "3. Test the AI responses in the chat interface"
echo ""
echo "Service account key saved to: $KEY_FILE"
echo "⚠️  Keep this file secure and never commit it to version control!"