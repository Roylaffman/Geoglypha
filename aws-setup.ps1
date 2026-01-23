# AWS Infrastructure Setup Script for Geoglypha Website
# This script creates S3 bucket and CloudFront distribution for static website hosting

param(
    [Parameter(Mandatory=$false)]
    [string]$BucketName = "geoglypha-website",
    
    [Parameter(Mandatory=$false)]
    [string]$Region = "us-east-1",
    
    [Parameter(Mandatory=$false)]
    [string]$Profile = "default",
    
    [switch]$DryRun
)

# Color output functions
function Write-Success {
    param([string]$Message)
    Write-Host "✓ $Message" -ForegroundColor Green
}

function Write-Info {
    param([string]$Message)
    Write-Host "ℹ $Message" -ForegroundColor Cyan
}

function Write-Warning {
    param([string]$Message)
    Write-Host "⚠ $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "✗ $Message" -ForegroundColor Red
}

# Check if AWS CLI is installed
function Test-AwsCli {
    try {
        $null = aws --version
        return $true
    }
    catch {
        return $false
    }
}

# Main setup function
function Setup-AwsInfrastructure {
    Write-Info "Starting AWS infrastructure setup for Geoglypha website..."
    Write-Info "Bucket Name: $BucketName"
    Write-Info "Region: $Region"
    Write-Info "Profile: $Profile"
    
    if ($DryRun) {
        Write-Warning "DRY RUN MODE - No changes will be made"
    }
    
    # Check AWS CLI
    if (-not (Test-AwsCli)) {
        Write-Error "AWS CLI is not installed or not in PATH"
        Write-Info "Please install AWS CLI from: https://aws.amazon.com/cli/"
        exit 1
    }
    
    Write-Success "AWS CLI is installed"
    
    # Step 1: Create S3 bucket
    Write-Info "`nStep 1: Creating S3 bucket..."
    
    if (-not $DryRun) {
        try {
            # Check if bucket already exists
            $bucketExists = aws s3api head-bucket --bucket $BucketName --profile $Profile 2>&1
            
            if ($LASTEXITCODE -eq 0) {
                Write-Warning "Bucket '$BucketName' already exists"
            }
            else {
                # Create bucket
                if ($Region -eq "us-east-1") {
                    aws s3api create-bucket --bucket $BucketName --profile $Profile
                }
                else {
                    aws s3api create-bucket --bucket $BucketName --region $Region --create-bucket-configuration LocationConstraint=$Region --profile $Profile
                }
                
                if ($LASTEXITCODE -eq 0) {
                    Write-Success "S3 bucket created: $BucketName"
                }
                else {
                    Write-Error "Failed to create S3 bucket"
                    exit 1
                }
            }
        }
        catch {
            Write-Error "Error creating bucket: $_"
            exit 1
        }
    }
    else {
        Write-Info "Would create S3 bucket: $BucketName in region $Region"
    }
    
    # Step 2: Configure static website hosting
    Write-Info "`nStep 2: Configuring static website hosting..."
    
    if (-not $DryRun) {
        try {
            aws s3 website s3://$BucketName/ --index-document index.html --error-document 404.html --profile $Profile
            
            if ($LASTEXITCODE -eq 0) {
                Write-Success "Static website hosting enabled"
            }
            else {
                Write-Error "Failed to enable static website hosting"
                exit 1
            }
        }
        catch {
            Write-Error "Error configuring website hosting: $_"
            exit 1
        }
    }
    else {
        Write-Info "Would enable static website hosting with index.html and 404.html"
    }
    
    # Step 3: Apply bucket policy for public read access
    Write-Info "`nStep 3: Applying bucket policy for public read access..."
    
    $bucketPolicy = @"
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::$BucketName/*"
    }
  ]
}
"@
    
    # Save policy to temporary file
    $policyFile = "bucket-policy.json"
    $bucketPolicy | Out-File -FilePath $policyFile -Encoding utf8
    
    if (-not $DryRun) {
        try {
            # Disable block public access
            aws s3api put-public-access-block --bucket $BucketName --public-access-block-configuration "BlockPublicAcls=false,IgnorePublicAcls=false,BlockPublicPolicy=false,RestrictPublicBuckets=false" --profile $Profile
            
            # Apply bucket policy
            aws s3api put-bucket-policy --bucket $BucketName --policy file://$policyFile --profile $Profile
            
            if ($LASTEXITCODE -eq 0) {
                Write-Success "Bucket policy applied for public read access"
            }
            else {
                Write-Error "Failed to apply bucket policy"
                exit 1
            }
        }
        catch {
            Write-Error "Error applying bucket policy: $_"
            exit 1
        }
    }
    else {
        Write-Info "Would apply public read bucket policy"
        Write-Info "Policy content:"
        Write-Host $bucketPolicy -ForegroundColor Gray
    }
    
    # Step 4: Create CloudFront distribution
    Write-Info "`nStep 4: Creating CloudFront distribution..."
    
    $websiteEndpoint = "$BucketName.s3-website-$Region.amazonaws.com"
    
    $cloudFrontConfig = @"
{
  "CallerReference": "geoglypha-$(Get-Date -Format 'yyyyMMddHHmmss')",
  "Comment": "Geoglypha Website CDN Distribution",
  "Enabled": true,
  "Origins": {
    "Quantity": 1,
    "Items": [
      {
        "Id": "S3-$BucketName",
        "DomainName": "$websiteEndpoint",
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
    "TargetOriginId": "S3-$BucketName",
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
        "TargetOriginId": "S3-$BucketName",
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
        "TargetOriginId": "S3-$BucketName",
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
"@
    
    # Save CloudFront config to file
    $cfConfigFile = "cloudfront-config.json"
    $cloudFrontConfig | Out-File -FilePath $cfConfigFile -Encoding utf8
    
    if (-not $DryRun) {
        try {
            Write-Info "Creating CloudFront distribution (this may take several minutes)..."
            $result = aws cloudfront create-distribution --distribution-config file://$cfConfigFile --profile $Profile
            
            if ($LASTEXITCODE -eq 0) {
                $distribution = $result | ConvertFrom-Json
                $distributionId = $distribution.Distribution.Id
                $domainName = $distribution.Distribution.DomainName
                
                Write-Success "CloudFront distribution created!"
                Write-Info "Distribution ID: $distributionId"
                Write-Info "Domain Name: $domainName"
                Write-Info "Status: Deploying (this will take 15-20 minutes)"
                
                # Save distribution info
                $distInfo = @{
                    DistributionId = $distributionId
                    DomainName = $domainName
                    BucketName = $BucketName
                    Region = $Region
                    CreatedAt = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
                } | ConvertTo-Json
                
                $distInfo | Out-File -FilePath "cloudfront-distribution-info.json" -Encoding utf8
                Write-Success "Distribution info saved to cloudfront-distribution-info.json"
            }
            else {
                Write-Error "Failed to create CloudFront distribution"
                exit 1
            }
        }
        catch {
            Write-Error "Error creating CloudFront distribution: $_"
            exit 1
        }
    }
    else {
        Write-Info "Would create CloudFront distribution with:"
        Write-Info "  - Origin: $websiteEndpoint"
        Write-Info "  - HTTPS redirect enabled"
        Write-Info "  - Compression enabled"
        Write-Info "  - Cache behaviors for /assets/* and /data/*"
        Write-Info "  - Custom error pages (404, 403)"
    }
    
    # Cleanup temporary files
    if (Test-Path $policyFile) {
        Remove-Item $policyFile -Force
    }
    if (Test-Path $cfConfigFile) {
        Remove-Item $cfConfigFile -Force
    }
    
    Write-Success "`n✓ AWS infrastructure setup complete!"
    Write-Info "`nNext steps:"
    Write-Info "1. Wait for CloudFront distribution to deploy (15-20 minutes)"
    Write-Info "2. Upload website files using the deployment script"
    Write-Info "3. Test the website via CloudFront URL"
    
    if (-not $DryRun) {
        Write-Info "`nS3 Website Endpoint: http://$websiteEndpoint"
        if (Test-Path "cloudfront-distribution-info.json") {
            $distInfo = Get-Content "cloudfront-distribution-info.json" | ConvertFrom-Json
            Write-Info "CloudFront URL: https://$($distInfo.DomainName)"
        }
    }
}

# Run the setup
Setup-AwsInfrastructure
