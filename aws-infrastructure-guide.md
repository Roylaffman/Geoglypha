# AWS Infrastructure Setup Guide

This guide explains how to set up the AWS infrastructure for the Geoglypha website, including S3 bucket configuration and CloudFront distribution.

## Prerequisites

### Option A: Using AWS CloudShell (Easiest - No Installation Required)

1. **AWS Account**: You need an active AWS account
2. **Access CloudShell**: 
   - Log into AWS Console
   - Click the CloudShell icon (>_) in the top navigation bar
   - CloudShell opens with AWS CLI pre-installed and authenticated
   - No credential configuration needed!

### Option B: Using Local AWS CLI

1. **AWS Account**: You need an active AWS account
2. **AWS CLI**: Install the AWS Command Line Interface
   - Download from: https://aws.amazon.com/cli/
   - Verify installation: `aws --version`

3. **AWS Credentials**: Configure your AWS credentials
   ```powershell
   aws configure
   ```
   You'll need:
   - AWS Access Key ID 8596-1633-8968
   - AWS Secret Access Key
   - Default region (e.g., `us-east-1`)
   - Default output format (e.g., `json`)

## Quick Start with AWS CloudShell

If you're using AWS CloudShell, follow these steps:

1. **Open CloudShell** in AWS Console (click the >_ icon)
2. **Run commands directly** - no authentication needed
3. **Create files** using `cat`, `nano`, or `vi` editors
4. **All commands in this guide work in CloudShell** (use bash syntax, not PowerShell)

## Infrastructure Components

### 1. S3 Bucket
- **Purpose**: Store static website files (HTML, CSS, JavaScript, images)
- **Configuration**: Static website hosting enabled
- **Access**: Public read access for website content
- **Bucket Name**: `geoglypha-website` (customizable)

### 2. CloudFront Distribution
- **Purpose**: Content Delivery Network (CDN) for fast global access
- **Features**:
  - HTTPS support (redirects HTTP to HTTPS)
  - Gzip compression enabled
  - Custom cache behaviors for different content types
  - Custom error pages (404, 403)

### 3. Cache Behaviors

| Path Pattern | Min TTL | Default TTL | Max TTL | Purpose |
|--------------|---------|-------------|---------|---------|
| Default (HTML) | 0 | 1 hour | 1 day | Frequently updated content |
| /assets/* | 1 day | 1 week | 1 year | Static assets (CSS, JS, images) |
| /data/* | 1 hour | 1 hour | 1 day | GeoJSON and data files |

## Setup Instructions

### Option 1: Automated Setup (Recommended)

Run the PowerShell setup script:

```powershell
# Dry run to see what would be created
.\aws-setup.ps1 -DryRun

# Create infrastructure with default settings
.\aws-setup.ps1

# Create with custom bucket name and region
.\aws-setup.ps1 -BucketName "my-custom-bucket" -Region "us-west-2"

# Use a specific AWS profile
.\aws-setup.ps1 -Profile "my-aws-profile"
```

The script will:
1. Create the S3 bucket
2. Enable static website hosting
3. Configure public read access
4. Create CloudFront distribution
5. Save distribution info to `cloudfront-distribution-info.json`

### Option 2: Manual Setup

**Note**: These commands work in AWS CloudShell, PowerShell, or any terminal with AWS CLI installed. Replace `geoglypha-website` with your desired bucket name (must be globally unique).

#### Step 1: Create S3 Bucket

```bash
# Create bucket (us-east-1)
aws s3api create-bucket --bucket geoglypha-website

# Create bucket (other regions) - add LocationConstraint
aws s3api create-bucket --bucket geoglypha-website --region us-west-2 --create-bucket-configuration LocationConstraint=us-west-2
```

**Verify bucket creation**:
```bash
aws s3 ls | grep geoglypha-website
```

#### Step 2: Enable Static Website Hosting

```bash
aws s3 website s3://geoglypha-website/ --index-document index.html --error-document 404.html
```

**Verify website configuration**:
```bash
aws s3api get-bucket-website --bucket geoglypha-website
```

#### Step 3: Configure Public Access

```powershell
# Disable block public access
aws s3api put-public-access-block --bucket geoglypha-website --public-access-block-configuration "BlockPublicAcls=false,IgnorePublicAcls=false,BlockPublicPolicy=false,RestrictPublicBuckets=false"

# Create bucket policy file (bucket-policy.json)
# Then apply it:
aws s3api put-bucket-policy --bucket geoglypha-website --policy file://bucket-policy.json
```

**bucket-policy.json**:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::geoglypha-website/*"
    }
  ]
}
```

#### Step 4: Create CloudFront Distribution

**Important**: Replace `geoglypha-website` with your actual bucket name and `us-east-1` with your bucket's region in the commands below.

##### Step 4a: Create the CloudFront Configuration File

In AWS CloudShell or your terminal, create the `cloudfront-config.json` file:

```bash
# Create the config file using a text editor
cat > cloudfront-config.json << 'EOF'
{
  "CallerReference": "geoglypha-2024-12-08",
  "Comment": "Geoglypha Website CDN Distribution",
  "Enabled": true,
  "Origins": {
    "Quantity": 1,
    "Items": [
      {
        "Id": "S3-geoglypha-website",
        "DomainName": "geoglypha-website.s3-website-us-east-1.amazonaws.com",
        "CustomOriginConfig": {
          "HTTPPort": 80,
          "HTTPSPort": 443,
          "OriginProtocolPolicy": "http-only"
        }
      }
    ]
  },
  "DefaultRootObject": "index.html",
  "DefaultCacheBehavior": {
    "TargetOriginId": "S3-geoglypha-website",
    "ViewerProtocolPolicy": "redirect-to-https",
    "AllowedMethods": {
      "Quantity": 2,
      "Items": ["GET", "HEAD"],
      "CachedMethods": {
        "Quantity": 2,
        "Items": ["GET", "HEAD"]
      }
    },
    "Compress": true,
    "MinTTL": 0,
    "DefaultTTL": 3600,
    "MaxTTL": 86400,
    "ForwardedValues": {
      "QueryString": false,
      "Cookies": {
        "Forward": "none"
      }
    },
    "TrustedSigners": {
      "Enabled": false,
      "Quantity": 0
    }
  },
  "CacheBehaviors": {
    "Quantity": 2,
    "Items": [
      {
        "PathPattern": "/assets/*",
        "TargetOriginId": "S3-geoglypha-website",
        "ViewerProtocolPolicy": "redirect-to-https",
        "AllowedMethods": {
          "Quantity": 2,
          "Items": ["GET", "HEAD"],
          "CachedMethods": {
            "Quantity": 2,
            "Items": ["GET", "HEAD"]
          }
        },
        "Compress": true,
        "MinTTL": 86400,
        "DefaultTTL": 604800,
        "MaxTTL": 31536000,
        "ForwardedValues": {
          "QueryString": false,
          "Cookies": {
            "Forward": "none"
          }
        },
        "TrustedSigners": {
          "Enabled": false,
          "Quantity": 0
        }
      },
      {
        "PathPattern": "/data/*",
        "TargetOriginId": "S3-geoglypha-website",
        "ViewerProtocolPolicy": "redirect-to-https",
        "AllowedMethods": {
          "Quantity": 2,
          "Items": ["GET", "HEAD"],
          "CachedMethods": {
            "Quantity": 2,
            "Items": ["GET", "HEAD"]
          }
        },
        "Compress": true,
        "MinTTL": 3600,
        "DefaultTTL": 3600,
        "MaxTTL": 86400,
        "ForwardedValues": {
          "QueryString": false,
          "Cookies": {
            "Forward": "none"
          }
        },
        "TrustedSigners": {
          "Enabled": false,
          "Quantity": 0
        }
      }
    ]
  },
  "CustomErrorResponses": {
    "Quantity": 2,
    "Items": [
      {
        "ErrorCode": 404,
        "ResponsePagePath": "/404.html",
        "ResponseCode": "404",
        "ErrorCachingMinTTL": 300
      },
      {
        "ErrorCode": 403,
        "ResponsePagePath": "/404.html",
        "ResponseCode": "404",
        "ErrorCachingMinTTL": 300
      }
    ]
  },
  "PriceClass": "PriceClass_All"
}
EOF
```

**Important Configuration Notes**:
- Replace `geoglypha-2024-12-08` with a unique timestamp (e.g., `geoglypha-2024-12-08-1430`)
- Replace `geoglypha-website` in the `Id` and `DomainName` fields with your bucket name
- Replace `us-east-1` in the `DomainName` with your bucket's region
- The S3 website endpoint format is: `BUCKET-NAME.s3-website-REGION.amazonaws.com`

##### Step 4b: Verify the Configuration File

```bash
# Check that the file was created correctly
cat cloudfront-config.json

# Validate JSON syntax (optional)
python3 -m json.tool cloudfront-config.json
```

##### Step 4c: Create the CloudFront Distribution

```bash
# Create the distribution
aws cloudfront create-distribution --distribution-config file://cloudfront-config.json

# Save the output to a file for reference
aws cloudfront create-distribution --distribution-config file://cloudfront-config.json > cloudfront-output.json
```

The command will return JSON output containing:
- **Distribution ID**: Save this for future reference
- **Domain Name**: Your CloudFront URL (e.g., `d1234567890.cloudfront.net`)
- **Status**: Will be "InProgress" initially

##### Step 4d: Extract Important Information

```bash
# Get the Distribution ID from the output
cat cloudfront-output.json | grep '"Id"' | head -1

# Get the Domain Name
cat cloudfront-output.json | grep '"DomainName"' | head -1
```

## Using AWS CloudShell

If you're using AWS CloudShell, here are some helpful tips:

### Creating Files in CloudShell

AWS CloudShell provides a Linux environment with common tools:

```bash
# Method 1: Using cat with heredoc (recommended)
cat > cloudfront-config.json << 'EOF'
{
  "your": "json content here"
}
EOF

# Method 2: Using nano editor
nano cloudfront-config.json
# Paste your JSON, then press Ctrl+X, Y, Enter to save

# Method 3: Using vi editor
vi cloudfront-config.json
# Press 'i' to enter insert mode, paste JSON
# Press Esc, then type :wq and press Enter to save
```

### Checking Your Work in CloudShell

```bash
# List files in current directory
ls -la

# View file contents
cat cloudfront-config.json

# Check if JSON is valid
python3 -m json.tool cloudfront-config.json

# Get your bucket's website endpoint
aws s3api get-bucket-website --bucket geoglypha-website
```

### Common CloudShell Issues

**Issue**: File not found error
```bash
# Make sure you're in the right directory
pwd
ls -la
```

**Issue**: JSON syntax error
```bash
# Validate your JSON
python3 -m json.tool cloudfront-config.json
# This will show you where the syntax error is
```

**Issue**: Need to edit the file
```bash
# Use nano (easiest for beginners)
nano cloudfront-config.json
```

## Verification

### Check S3 Bucket

```powershell
# List buckets
aws s3 ls

# Check bucket website configuration
aws s3api get-bucket-website --bucket geoglypha-website

# Check bucket policy
aws s3api get-bucket-policy --bucket geoglypha-website
```

### Check CloudFront Distribution

```powershell
# List distributions
aws cloudfront list-distributions

# Get specific distribution
aws cloudfront get-distribution --id YOUR_DISTRIBUTION_ID

# Check distribution status
aws cloudfront get-distribution --id YOUR_DISTRIBUTION_ID --query 'Distribution.Status'
```

## Important Notes

### CloudFront Deployment Time
- CloudFront distributions take **15-20 minutes** to deploy
- Status will show "InProgress" during deployment
- Wait for status to change to "Deployed" before testing

### S3 Website Endpoint
The S3 website endpoint follows this format:
- **us-east-1**: `http://bucket-name.s3-website-us-east-1.amazonaws.com`
- **Other regions**: `http://bucket-name.s3-website-region.amazonaws.com`

### CloudFront Domain
- CloudFront provides a domain like: `d1234567890.cloudfront.net`
- This domain is saved in `cloudfront-distribution-info.json`
- You can configure a custom domain later using Route 53

## Cost Estimates

### S3 Costs
- **Storage**: $0.023 per GB/month (first 50 TB)
- **Requests**: $0.0004 per 1,000 GET requests
- **Data Transfer**: First 1 GB/month free, then $0.09 per GB

### CloudFront Costs
- **Data Transfer**: First 1 TB/month: $0.085 per GB
- **Requests**: $0.0075 per 10,000 HTTP requests
- **Free Tier**: 50 GB data transfer out, 2,000,000 HTTP requests/month (12 months)

### Estimated Monthly Cost
For a small website with moderate traffic:
- **Storage (1 GB)**: ~$0.02
- **Data Transfer (10 GB)**: ~$0.85
- **Requests (100,000)**: ~$0.08
- **Total**: ~$1.00/month

## Troubleshooting

### Issue: Bucket Already Exists
**Error**: `BucketAlreadyExists` or `BucketAlreadyOwnedByYou`

**Solution**: Choose a different bucket name (must be globally unique)

### Issue: Access Denied
**Error**: `AccessDenied` when applying bucket policy

**Solution**: 
1. Check your IAM permissions
2. Ensure you have `s3:PutBucketPolicy` permission
3. Verify block public access settings are disabled

### Issue: CloudFront Creation Fails
**Error**: Various CloudFront errors

**Solution**:
1. Verify S3 bucket exists and is accessible
2. Check CloudFront configuration JSON syntax
3. Ensure you have CloudFront permissions in IAM

### Issue: 403 Forbidden on Website
**Error**: 403 error when accessing S3 website endpoint

**Solution**:
1. Verify bucket policy is applied correctly
2. Check that files have been uploaded
3. Ensure `index.html` exists in bucket root

## Next Steps

After infrastructure setup:

1. **Upload Website Files**: Use the deployment script to upload files
   ```powershell
   .\deploy-to-aws.ps1
   ```

2. **Test S3 Endpoint**: Access the S3 website endpoint directly
   ```
   http://geoglypha-website.s3-website-us-east-1.amazonaws.com
   ```

3. **Test CloudFront**: Access via CloudFront domain (after deployment completes)
   ```
   https://d1234567890.cloudfront.net
   ```

4. **Configure Custom Domain** (Optional): Set up Route 53 and SSL certificate

## Security Best Practices

1. **Enable S3 Versioning**: Protect against accidental deletions
   ```powershell
   aws s3api put-bucket-versioning --bucket geoglypha-website --versioning-configuration Status=Enabled
   ```

2. **Enable S3 Logging**: Track access to your bucket
   ```powershell
   aws s3api put-bucket-logging --bucket geoglypha-website --bucket-logging-status file://logging-config.json
   ```

3. **Use CloudFront Access Logs**: Monitor CDN usage
   - Configure in CloudFront distribution settings

4. **Set Up CloudWatch Alarms**: Monitor costs and usage
   - Create billing alarms in AWS Console

## Additional Resources

- [AWS S3 Static Website Hosting](https://docs.aws.amazon.com/AmazonS3/latest/userguide/WebsiteHosting.html)
- [CloudFront Developer Guide](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/)
- [AWS CLI Reference](https://docs.aws.amazon.com/cli/latest/)
- [AWS Free Tier](https://aws.amazon.com/free/)
