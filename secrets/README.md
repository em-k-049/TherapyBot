# Google Cloud Credentials

Place your Google Cloud service account JSON file here as `gcp-credentials.json`.

## Setup Instructions:

1. **Create a Google Cloud Project**:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one
   - Note the Project ID

2. **Enable Vertex AI API**:
   - Go to APIs & Services > Library
   - Search for "Vertex AI API"
   - Click Enable

3. **Create Service Account**:
   - Go to IAM & Admin > Service Accounts
   - Click "Create Service Account"
   - Name: `therapybot-vertex-ai`
   - Grant roles:
     - `Vertex AI User`
     - `AI Platform Developer`

4. **Download Credentials**:
   - Click on the service account
   - Go to Keys tab
   - Click "Add Key" > "Create new key"
   - Choose JSON format
   - Save as `gcp-credentials.json` in this directory

5. **Update Environment Variables**:
   ```bash
   GCP_PROJECT_ID=your-actual-project-id
   GCP_REGION=us-central1
   ```

## Security Notes:
- Never commit `gcp-credentials.json` to version control
- This directory is already in `.gitignore`
- Use different credentials for development/production