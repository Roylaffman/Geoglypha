# Google Cloud Deployment Guide for KML/KMZ to GeoJSON Converter

This guide explains how to deploy the KML/KMZ to GeoJSON converter application to Google Cloud Platform using Google App Engine and Google Cloud Storage.

## Prerequisites

- Google Cloud SDK CLI installed and configured
- A Google Cloud Platform account with billing enabled
- Basic knowledge of command-line operations

## 1. Setting Up Google Cloud Storage

Google Cloud Storage will be used to temporarily store uploaded KML/KMZ files during processing.

### 1.1 Create a Storage Bucket

1. Open your terminal and run:
   ```bash
   gcloud storage buckets create gs://YOUR_BUCKET_NAME --location=us-central1 --default-storage-class=STANDARD
   ```
   Replace `YOUR_BUCKET_NAME` with a globally unique name for your bucket.

2. Set appropriate permissions for your bucket:
   ```bash
   gcloud storage buckets add-iam-policy-binding gs://YOUR_BUCKET_NAME --member=serviceAccount:YOUR_PROJECT_ID@appspot.gserviceaccount.com --role=roles/storage.objectAdmin
   ```
   Replace `YOUR_PROJECT_ID` with your Google Cloud project ID.

### 1.2 Update the Application Configuration

1. Open the `app.yaml` file and update the `BUCKET_NAME` environment variable with your bucket name:
   ```yaml
   env_variables:
     BUCKET_NAME: "YOUR_BUCKET_NAME"
   ```

## 2. Preparing the Application for Deployment

### 2.1 Install Required Dependencies

1. Create a `requirements.txt` file with all the necessary dependencies:
   ```
   Flask==3.1.0
   gunicorn==21.2.0
   pykml==0.2.0
   lxml==5.3.2
   geojson==3.2.0
   python-magic==0.4.27
   google-cloud-storage==2.13.0
   ```

2. Update the application to use Google Cloud Storage instead of local storage:
   - Modify the `app.py` file to use Google Cloud Storage for temporary file storage
   - Update file paths to work with Google Cloud Storage

## 3. Modifying the Application for Google Cloud

### 3.1 Update the Flask Application

The Flask application needs to be modified to work with Google Cloud Storage. Here's what you need to change:

1. Import the Google Cloud Storage client:
   ```python
   from google.cloud import storage
   ```

2. Initialize the storage client:
   ```python
   storage_client = storage.Client()
   bucket_name = os.environ.get('BUCKET_NAME')
   bucket = storage_client.bucket(bucket_name)
   ```

3. Update file upload handling to use Google Cloud Storage:
   - Instead of saving files locally, upload them to your bucket
   - Download files from the bucket for processing
   - Delete files from the bucket after processing

## 4. Deploying to Google App Engine

### 4.1 Test Locally

Before deploying, test your application locally:

```bash
export BUCKET_NAME=YOUR_BUCKET_NAME
python app.py
```

### 4.2 Deploy to App Engine

1. Make sure you're in the project directory containing `app.yaml`:
   ```bash
   cd /path/to/kml_to_geojson
   ```

2. Deploy the application:
   ```bash
   gcloud app deploy
   ```

3. When prompted, select a region close to your users.

4. Wait for the deployment to complete. This may take a few minutes.

5. Once deployed, access your application:
   ```bash
   gcloud app browse
   ```
   This will open your default browser to your application's URL.

## 5. Monitoring and Maintenance

### 5.1 View Logs

To view application logs:
```bash
gcloud app logs tail
```

### 5.2 Monitor Resource Usage

Monitor your application's resource usage in the Google Cloud Console:
1. Go to the Google Cloud Console (https://console.cloud.google.com/)
2. Navigate to App Engine > Dashboard
3. View metrics such as requests, latency, and instance hours

### 5.3 Set Up Budget Alerts

To avoid unexpected charges:
1. Go to Billing > Budgets & alerts
2. Create a budget with email alerts

## 6. Troubleshooting

### Common Issues and Solutions

1. **File Upload Issues**:
   - Check that your bucket permissions are correctly set
   - Verify that the App Engine service account has access to the bucket

2. **Application Crashes**:
   - Check the logs using `gcloud app logs tail`
   - Ensure all dependencies are correctly listed in `requirements.txt`

3. **Slow Performance**:
   - Consider increasing the instance class in `app.yaml`
   - Optimize file processing code

## 7. Additional Resources

- [Google App Engine Documentation](https://cloud.google.com/appengine/docs)
- [Google Cloud Storage Documentation](https://cloud.google.com/storage/docs)
- [Flask on App Engine Documentation](https://cloud.google.com/appengine/docs/standard/python3/building-app)

## 8. Cost Management

App Engine and Cloud Storage both incur costs based on usage. To manage costs:

1. Use the smallest instance class that meets your needs
2. Set up automatic scaling to reduce instances during low traffic
3. Configure lifecycle rules on your storage bucket to delete old files
4. Set up budget alerts to notify you of unexpected spending

## 9. Security Considerations

1. Always validate and sanitize user inputs
2. Set appropriate CORS policies for your bucket
3. Use HTTPS for all communications
4. Regularly update dependencies to patch security vulnerabilities
5. Consider implementing rate limiting to prevent abuse

## 10. Next Steps

After successful deployment, consider:

1. Setting up a custom domain for your application
2. Implementing user authentication if needed
3. Adding analytics to track usage patterns
4. Creating a CI/CD pipeline for automated deployments
