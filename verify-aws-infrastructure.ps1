# AWS Infrastructure Verification Script
# Checks the status of S3 bucket and CloudFront distribution

param(
    [Parameter(Mandatory=$false)]
    [string]$BucketName = "geoglypha-website",
    
    [Parameter(Mandatory=$false)]
    [string]$Profile = "default"
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

Write-Info "Verifying AWS Infrastructure for Geoglypha Website"
Write-Info "================================================`n"

# Check AWS CLI
try {
    $null = aws --version
    Write-Success "AWS CLI is installed"
}
catch {
    Write-Error "AWS CLI is not installed or not in PATH"
    exit 1
}

# Check S3 Bucket
Write-Info "`nChecking S3 Bucket: $BucketName"
Write-Host "----------------------------------------"

try {
    $bucketExists = aws s3api head-bucket --bucket $BucketName --profile $Profile 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Bucket exists: $BucketName"
        
        # Check website configuration
        $websiteConfig = aws s3api get-bucket-website --bucket $BucketName --profile $Profile 2>&1 | ConvertFrom-Json
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Static website hosting is enabled"
            Write-Info "  Index document: $($websiteConfig.IndexDocument.Suffix)"
            Write-Info "  Error document: $($websiteConfig.ErrorDocument.Key)"
        }
        else {
            Write-Warning "Static website hosting is not enabled"
        }
        
        # Check bucket policy
        $policyExists = aws s3api get-bucket-policy --bucket $BucketName --profile $Profile 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Bucket policy is configured"
        }
        else {
            Write-Warning "Bucket policy is not configured"
        }
        
        # Get bucket region
        $location = aws s3api get-bucket-location --bucket $BucketName --profile $Profile 2>&1 | ConvertFrom-Json
        $region = if ($location.LocationConstraint) { $location.LocationConstraint } else { "us-east-1" }
        Write-Info "  Region: $region"
        
        # Construct website endpoint
        $websiteEndpoint = "$BucketName.s3-website-$region.amazonaws.com"
        Write-Info "  Website endpoint: http://$websiteEndpoint"
        
        # Check if files exist
        $fileCount = (aws s3 ls s3://$BucketName/ --profile $Profile 2>&1 | Measure-Object).Count
        Write-Info "  Files in bucket: $fileCount"
        
        if ($fileCount -eq 0) {
            Write-Warning "  No files uploaded yet - run deployment script"
        }
    }
    else {
        Write-Error "Bucket does not exist: $BucketName"
        Write-Info "Run aws-setup.ps1 to create the infrastructure"
    }
}
catch {
    Write-Error "Error checking S3 bucket: $_"
}

# Check CloudFront Distribution
Write-Info "`nChecking CloudFront Distribution"
Write-Host "----------------------------------------"

if (Test-Path "cloudfront-distribution-info.json") {
    try {
        $distInfo = Get-Content "cloudfront-distribution-info.json" | ConvertFrom-Json
        $distributionId = $distInfo.DistributionId
        
        Write-Success "Distribution info file found"
        Write-Info "  Distribution ID: $distributionId"
        Write-Info "  Domain Name: $($distInfo.DomainName)"
        Write-Info "  Created: $($distInfo.CreatedAt)"
        
        # Get distribution status
        $distribution = aws cloudfront get-distribution --id $distributionId --profile $Profile 2>&1 | ConvertFrom-Json
        
        if ($LASTEXITCODE -eq 0) {
            $status = $distribution.Distribution.Status
            $enabled = $distribution.Distribution.DistributionConfig.Enabled
            
            Write-Info "  Status: $status"
            Write-Info "  Enabled: $enabled"
            
            if ($status -eq "Deployed") {
                Write-Success "CloudFront distribution is deployed and ready"
                Write-Info "  Access your site at: https://$($distInfo.DomainName)"
            }
            elseif ($status -eq "InProgress") {
                Write-Warning "CloudFront distribution is still deploying"
                Write-Info "  This typically takes 15-20 minutes"
                Write-Info "  Check back in a few minutes"
            }
            else {
                Write-Warning "CloudFront distribution status: $status"
            }
            
            # Check cache behaviors
            $cacheBehaviors = $distribution.Distribution.DistributionConfig.CacheBehaviors.Items
            if ($cacheBehaviors) {
                Write-Info "  Cache behaviors configured: $($cacheBehaviors.Count)"
            }
        }
        else {
            Write-Error "Could not retrieve distribution information"
        }
    }
    catch {
        Write-Error "Error checking CloudFront distribution: $_"
    }
}
else {
    Write-Warning "CloudFront distribution info file not found"
    Write-Info "Run aws-setup.ps1 to create the infrastructure"
}

# Summary
Write-Info "`nInfrastructure Status Summary"
Write-Host "========================================"

$s3Ready = $false
$cfReady = $false

try {
    $bucketCheck = aws s3api head-bucket --bucket $BucketName --profile $Profile 2>&1
    $s3Ready = ($LASTEXITCODE -eq 0)
}
catch {
    $s3Ready = $false
}

if (Test-Path "cloudfront-distribution-info.json") {
    try {
        $distInfo = Get-Content "cloudfront-distribution-info.json" | ConvertFrom-Json
        $distribution = aws cloudfront get-distribution --id $distInfo.DistributionId --profile $Profile 2>&1 | ConvertFrom-Json
        $cfReady = ($LASTEXITCODE -eq 0 -and $distribution.Distribution.Status -eq "Deployed")
    }
    catch {
        $cfReady = $false
    }
}

if ($s3Ready) {
    Write-Success "S3 Bucket: Ready"
}
else {
    Write-Error "S3 Bucket: Not Ready"
}

if ($cfReady) {
    Write-Success "CloudFront: Ready"
}
else {
    Write-Warning "CloudFront: Not Ready or Still Deploying"
}

Write-Info "`nNext Steps:"
if (-not $s3Ready) {
    Write-Info "1. Run aws-setup.ps1 to create infrastructure"
}
elseif (-not $cfReady) {
    Write-Info "1. Wait for CloudFront deployment to complete (15-20 minutes)"
    Write-Info "2. Run this script again to check status"
}
else {
    Write-Info "1. Run deploy-to-aws.ps1 to upload website files"
    Write-Info "2. Test your website via CloudFront URL"
}

Write-Host ""
