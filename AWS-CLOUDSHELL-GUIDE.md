# AWS CloudShell Setup Guide for Geoglypha Website

This is a simplified guide for setting up your infrastructure using AWS CloudShell. No local installation required!

## What is AWS CloudShell?

AWS CloudShell is a browser-based shell that comes pre-installed with AWS CLI and is automatically authenticated with your AWS account. Perfect for quick setups!

## Step-by-Step Instructions

### Step 1: Open AWS CloudShell

1. Log into your AWS Console
2. Click the **CloudShell icon** (>_) in the top navigation bar
3. Wait for CloudShell to initialize (takes ~10 seconds)

### Step 2: Create S3 Bucket

Replace `geoglypha-website` with your desired bucket name (must be globally unique):

```bash
# For us-east-1 region
aws s3api create-bucket --bucket geoglypha-website

# For other regions (example: us-west-2)
aws s3api create-bucket --bucket geoglypha-website --region us-west-2 --create-bucket-configuration LocationConstraint=us-west-2
```

**Verify it worked**:
```bash
aws s3 ls | grep geoglypha-website
```

### Step 3: Enable Static Website Hosting

```bash
aws s3 website s3://geoglypha-website/ --index-document index.html --error-document 404.html
```

**Verify it worked**:
```bash
aws s3api get-bucket-website --bucket geoglypha-website
```

You should see output showing `index.html` and `404.html` configuration.

### Step 4: Configure Public Access

First, disable block public access:

```bash
aws s3api put-public-access-block \
  --bucket geoglypha-website \
  --public-access-block-configuration "BlockPublicAcls=false,IgnorePublicAcls=false,BlockPublicPolicy=false,RestrictPublicBuckets=false"
```

Now create the bucket policy file:

```bash
cat > bucket-policy.json << 'EOF'
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
EOF
```

**Important**: If your bucket name is different, edit the file:
```bash
nano bucket-policy.json
# Change "geoglypha-website" to your bucket name
# Press Ctrl+X, then Y, then Enter to save
```

Apply the bucket policy:

```bash
aws s3api put-bucket-policy --bucket geoglypha-website --policy file://bucket-policy.json
```

**Verify it worked**:
```bash
aws s3api get-bucket-policy --bucket geoglypha-website
```

### Step 5: Create CloudFront Configuration File

This is the most complex step. We'll create a JSON configuration file for CloudFront.

**Important**: You need to customize this file with your bucket name and region!

```bash
cat > cloudfront-config.json << 'EOF'
{
  "CallerReference": "geoglypha-TIMESTAMP",
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

Now **EDIT THE FILE** to customize it:

```bash
nano cloudfront-config.json
```

**Required Changes**:
1. Line 2: Change `geoglypha-TIMESTAMP` to something unique like `geoglypha-20241208-1430`
2. Line 9: Change `S3-geoglypha-website` to `S3-YOUR-BUCKET-NAME`
3. Line 10: Change the DomainName:
   - Format: `YOUR-BUCKET-NAME.s3-website-YOUR-REGION.amazonaws.com`
   - Example for us-east-1: `mybucket.s3-website-us-east-1.amazonaws.com`
   - Example for us-west-2: `mybucket.s3-website-us-west-2.amazonaws.com`
4. Line 20: Change `S3-geoglypha-website` to match line 9
5. Line 52: Change `S3-geoglypha-website` to match line 9
6. Line 82: Change `S3-geoglypha-website` to match line 9

**To save in nano**: Press `Ctrl+X`, then `Y`, then `Enter`

**Verify your JSON is valid**:
```bash
python3 -m json.tool cloudfront-config.json
```

If you see formatted JSON output, it's valid! If you see an error, there's a syntax problem.

### Step 6: Create CloudFront Distribution

```bash
aws cloudfront create-distribution --distribution-config file://cloudfront-config.json > cloudfront-output.json
```

This takes a few seconds. If successful, you'll see JSON output.

**Extract important information**:

```bash
# Get Distribution ID
cat cloudfront-output.json | grep '"Id"' | head -1

# Get CloudFront Domain Name
cat cloudfront-output.json | grep '"DomainName"' | head -1
```

**Save these values!** You'll need them later.

### Step 7: Check CloudFront Status

```bash
# Replace DISTRIBUTION_ID with your actual ID from step 6
aws cloudfront get-distribution --id DISTRIBUTION_ID --query 'Distribution.Status'
```

Status will be:
- `"InProgress"` - Still deploying (wait 15-20 minutes)
- `"Deployed"` - Ready to use!

## What's Your S3 Website Endpoint?

Your S3 website endpoint format depends on your region:

- **us-east-1**: `http://YOUR-BUCKET-NAME.s3-website-us-east-1.amazonaws.com`
- **us-west-2**: `http://YOUR-BUCKET-NAME.s3-website-us-west-2.amazonaws.com`
- **eu-west-1**: `http://YOUR-BUCKET-NAME.s3-website-eu-west-1.amazonaws.com`

Replace `YOUR-BUCKET-NAME` with your actual bucket name.

## Common Issues and Solutions

### Issue: "BucketAlreadyExists" Error

**Problem**: Bucket names must be globally unique across all AWS accounts.

**Solution**: Choose a different name:
```bash
aws s3api create-bucket --bucket geoglypha-website-yourname-2024
```

### Issue: "AccessDenied" When Applying Bucket Policy

**Problem**: Block public access is still enabled.

**Solution**: Run the public access block command again:
```bash
aws s3api put-public-access-block \
  --bucket geoglypha-website \
  --public-access-block-configuration "BlockPublicAcls=false,IgnorePublicAcls=false,BlockPublicPolicy=false,RestrictPublicBuckets=false"
```

### Issue: "ValidationError" When Creating CloudFront

**Problem**: JSON syntax error in cloudfront-config.json

**Solution**: Validate your JSON:
```bash
python3 -m json.tool cloudfront-config.json
```

Look for the line number in the error message and fix the syntax.

### Issue: Can't Edit Files in CloudShell

**Nano Editor Basics**:
- `Ctrl+X` - Exit
- `Ctrl+O` - Save (Write Out)
- `Ctrl+K` - Cut line
- `Ctrl+U` - Paste line
- Arrow keys to navigate

**Vi Editor Basics** (if you prefer vi):
- Press `i` to enter Insert mode
- Press `Esc` to exit Insert mode
- Type `:wq` and press Enter to save and quit
- Type `:q!` and press Enter to quit without saving

## Next Steps

After CloudFront is deployed (15-20 minutes):

1. **Upload your website files** to S3:
   ```bash
   aws s3 sync /path/to/your/website s3://geoglypha-website/
   ```

2. **Test S3 endpoint**:
   ```
   http://geoglypha-website.s3-website-us-east-1.amazonaws.com
   ```

3. **Test CloudFront URL**:
   ```
   https://YOUR-DISTRIBUTION-ID.cloudfront.net
   ```

4. **(Optional) Set up custom domain** using Route 53

## Helpful CloudShell Commands

```bash
# List all your S3 buckets
aws s3 ls

# List files in your bucket
aws s3 ls s3://geoglypha-website/

# Check CloudFront distributions
aws cloudfront list-distributions --query 'DistributionList.Items[*].[Id,DomainName,Status]' --output table

# View file contents
cat filename.json

# Check current directory
pwd

# List files in current directory
ls -la

# Delete a file
rm filename.json
```

## Cost Reminder

- **S3**: ~$0.02/month for 1GB storage
- **CloudFront**: First 50GB/month free for 12 months
- **Estimated total**: ~$1-2/month for a small website

## Need Help?

If you get stuck:
1. Check the error message carefully
2. Verify your bucket name and region are correct
3. Make sure JSON files have valid syntax
4. Ensure you've completed all previous steps

Good luck with your deployment! 🚀
