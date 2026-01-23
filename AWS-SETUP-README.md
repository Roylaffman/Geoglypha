# AWS Infrastructure Setup - Quick Start

This directory contains scripts and configuration for deploying the Geoglypha website to AWS.

## Quick Start

### 1. Prerequisites

- Install [AWS CLI](https://aws.amazon.com/cli/)
- Configure AWS credentials: `aws configure`
- Ensure you have appropriate IAM permissions for S3 and CloudFront

### 2. Set Up Infrastructure

```powershell
# Test what will be created (dry run)
.\aws-setup.ps1 -DryRun

# Create the infrastructure
.\aws-setup.ps1
```

This creates:
- ✓ S3 bucket for static website hosting
- ✓ Bucket policy for public read access
- ✓ CloudFront distribution with caching rules
- ✓ Custom error page configuration

### 3. Wait for CloudFront Deployment

CloudFront takes **15-20 minutes** to deploy. Check status:

```powershell
# Get distribution ID from cloudfront-distribution-info.json
aws cloudfront get-distribution --id YOUR_DISTRIBUTION_ID --query 'Distribution.Status'
```

### 4. Deploy Website Files

Once CloudFront is deployed, upload your files:

```powershell
.\deploy-to-aws.ps1
```

## Files Created

After running `aws-setup.ps1`:

- **cloudfront-distribution-info.json** - Contains your CloudFront distribution ID and domain
- **aws-config.template.json** - Configuration template for deployment settings

## Infrastructure Details

### S3 Bucket Configuration
- **Name**: geoglypha-website (customizable)
- **Region**: us-east-1 (customizable)
- **Website Hosting**: Enabled
- **Index Document**: index.html
- **Error Document**: 404.html
- **Public Access**: Enabled for website content

### CloudFront Distribution
- **HTTPS**: Enabled (redirects HTTP to HTTPS)
- **Compression**: Enabled (Gzip)
- **Cache Behaviors**:
  - HTML files: 1 hour default, 1 day max
  - Assets (/assets/*): 1 week default, 1 year max
  - Data files (/data/*): 1 hour default, 1 day max
- **Error Pages**: Custom 404.html for 403 and 404 errors

## Customization

### Change Bucket Name or Region

```powershell
.\aws-setup.ps1 -BucketName "my-custom-name" -Region "us-west-2"
```

### Use Different AWS Profile

```powershell
.\aws-setup.ps1 -Profile "my-profile"
```

## Verification

### Test S3 Website Endpoint

```
http://geoglypha-website.s3-website-us-east-1.amazonaws.com
```

### Test CloudFront URL

```
https://[your-distribution-id].cloudfront.net
```

(Get your CloudFront domain from `cloudfront-distribution-info.json`)

## Cost Estimate

For a small website with moderate traffic (~10GB/month):
- **Monthly Cost**: ~$1-2 USD
- **Free Tier**: First 12 months include 50GB CloudFront transfer

See `aws-infrastructure-guide.md` for detailed cost breakdown.

## Troubleshooting

### Bucket Name Already Exists
S3 bucket names must be globally unique. Choose a different name:
```powershell
.\aws-setup.ps1 -BucketName "geoglypha-website-yourname"
```

### Access Denied Errors
Ensure your AWS credentials have these permissions:
- s3:CreateBucket
- s3:PutBucketPolicy
- s3:PutBucketWebsite
- cloudfront:CreateDistribution

### CloudFront Not Working
Wait 15-20 minutes for deployment to complete. Check status:
```powershell
aws cloudfront list-distributions --query 'DistributionList.Items[0].Status'
```

## Next Steps

1. ✓ Run `aws-setup.ps1` to create infrastructure
2. ⏳ Wait for CloudFront deployment (15-20 min)
3. 📤 Run deployment script to upload files
4. 🧪 Test website via CloudFront URL
5. 🌐 (Optional) Configure custom domain with Route 53

## Documentation

- **aws-infrastructure-guide.md** - Comprehensive setup guide
- **deployment_guide.md** - File deployment instructions
- **AWS CLI Docs** - https://docs.aws.amazon.com/cli/

## Support

For issues or questions:
1. Check the troubleshooting section in `aws-infrastructure-guide.md`
2. Review AWS CloudWatch logs
3. Verify IAM permissions in AWS Console
