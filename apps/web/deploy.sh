#!/bin/bash

# Deployment script for Svelte web app to AWS
# This script builds the app, deploys infrastructure, and uploads files to S3

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=========================================="
echo "Deploying Knowledge Hub Web App to AWS"
echo "=========================================="

# Step 1: Build the application
echo ""
echo "Step 1: Building the application..."
./build.sh

# Step 2: Deploy infrastructure with SAM
echo ""
echo "Step 2: Deploying infrastructure (S3 + CloudFront)..."
sam build
sam deploy

# Step 3: Get stack outputs
echo ""
echo "Step 3: Getting stack outputs..."
STACK_NAME="knowledge-hub-web"
BUCKET_NAME=$(aws cloudformation describe-stacks \
    --stack-name "$STACK_NAME" \
    --query 'Stacks[0].Outputs[?OutputKey==`S3BucketName`].OutputValue' \
    --output text \
    --region us-east-1)

if [ -z "$BUCKET_NAME" ]; then
    echo "Error: Could not retrieve S3 bucket name from stack outputs"
    exit 1
fi

CLOUDFRONT_URL=$(aws cloudformation describe-stacks \
    --stack-name "$STACK_NAME" \
    --query 'Stacks[0].Outputs[?OutputKey==`CloudFrontUrl`].OutputValue' \
    --output text \
    --region us-east-1)

CLOUDFRONT_DIST_ID=$(aws cloudformation describe-stacks \
    --stack-name "$STACK_NAME" \
    --query 'Stacks[0].Outputs[?OutputKey==`CloudFrontDistributionId`].OutputValue' \
    --output text \
    --region us-east-1)

echo "S3 Bucket: $BUCKET_NAME"
echo "CloudFront URL: https://$CLOUDFRONT_URL"
echo "CloudFront Distribution ID: $CLOUDFRONT_DIST_ID"

# Step 4: Sync files to S3
echo ""
echo "Step 4: Uploading files to S3..."

# Sync all files to S3
aws s3 sync dist/ "s3://$BUCKET_NAME/" \
    --delete \
    --region us-east-1

# Update cache headers for HTML files (no-cache for SPA routing)
echo "Setting cache headers for HTML files..."
find dist -name "*.html" -type f | while read -r html_file; do
    filename=$(basename "$html_file")
    aws s3 cp "s3://$BUCKET_NAME/$filename" "s3://$BUCKET_NAME/$filename" \
        --cache-control "public, max-age=0, must-revalidate" \
        --content-type "text/html" \
        --metadata-directive REPLACE \
        --region us-east-1 > /dev/null 2>&1 || true
done

# Step 5: Invalidate CloudFront cache
echo ""
echo "Step 5: Invalidating CloudFront cache..."
aws cloudfront create-invalidation \
    --distribution-id "$CLOUDFRONT_DIST_ID" \
    --paths "/*" \
    --region us-east-1 > /dev/null

echo ""
echo "=========================================="
echo "Deployment complete!"
echo "=========================================="
echo ""
echo "Your app is available at: https://$CLOUDFRONT_URL"
echo ""
echo "Note: CloudFront distribution may take 15-20 minutes to fully propagate."
echo ""
echo "Next steps:"
echo "1. Update API CORS configuration to include: https://$CLOUDFRONT_URL"
echo "2. Redeploy the API with updated CORS origins"
echo ""

