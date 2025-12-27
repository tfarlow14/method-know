# Knowledge Hub Web App

Svelte-based frontend application for the Knowledge Hub platform.

## Development

### Prerequisites

- Node.js 18+ and pnpm (or npm/yarn)
- AWS CLI configured with credentials (for deployment)

### Setup

1. Install dependencies:
```bash
pnpm install
```

2. Start the development server:
```bash
pnpm dev
```

The app will be available at `http://localhost:5173`

### Environment Variables

The app uses environment variables prefixed with `VITE_` for build-time configuration:

- `VITE_API_URL`: API Gateway endpoint URL (defaults to `http://localhost:8000` for local development)

Create a `.env` file in the `apps/web` directory to set these variables:

```bash
VITE_API_URL=https://your-api-gateway-url.execute-api.us-east-1.amazonaws.com/Prod/
```

## Building

To create a production build:

```bash
pnpm build
```

Or use the build script:

```bash
./build.sh
```

The production build will be output to the `dist/` directory.

You can preview the production build locally:

```bash
pnpm preview
```

## Deployment to AWS

### Prerequisites

- AWS CLI installed and configured
- AWS SAM CLI installed (`brew install aws-sam-cli` or see [SAM docs](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html))
- Appropriate AWS permissions for S3, CloudFront, and CloudFormation
- API Gateway endpoint URL (from the `knowledge-hub-api` stack)

### Deployment Steps

1. **Get your API Gateway URL:**

   First, get the API URL from your deployed API stack:

   ```bash
   aws cloudformation describe-stacks \
     --stack-name knowledge-hub-api \
     --query 'Stacks[0].Outputs[?OutputKey==`ApiUrl`].OutputValue' \
     --output text \
     --region us-east-1
   ```

2. **Set the API URL environment variable:**

   ```bash
   export VITE_API_URL=https://your-api-gateway-url.execute-api.us-east-1.amazonaws.com/Prod/
   ```

3. **Deploy the web app:**

   ```bash
   ./deploy.sh
   ```

   This script will:
   - Build the Svelte app with the configured API URL
   - Deploy the infrastructure (S3 bucket + CloudFront distribution) using SAM
   - Upload the built files to S3
   - Invalidate the CloudFront cache

4. **Get your CloudFront URL:**

   After deployment, the script will output your CloudFront URL. You can also retrieve it:

   ```bash
   aws cloudformation describe-stacks \
     --stack-name knowledge-hub-web \
     --query 'Stacks[0].Outputs[?OutputKey==`CloudFrontUrl`].OutputValue' \
     --output text \
     --region us-east-1
   ```

5. **Update API CORS configuration:**

   After getting your CloudFront URL, update the API CORS configuration to allow requests from your CloudFront domain:

   ```bash
   # Get the CloudFront URL (from step 4)
   CLOUDFRONT_URL="https://d1234567890.cloudfront.net"
   
   # Get existing CORS origins (if any)
   EXISTING_ORIGINS="http://localhost:5173,http://localhost:4173"
   
   # Deploy API with updated CORS origins
   cd ../api
   sam deploy --parameter-overrides \
     CORSOrigins="$EXISTING_ORIGINS,$CLOUDFRONT_URL" \
     JWTSecretKey="your-production-secret-key"
   ```

### Manual Deployment Steps

If you prefer to deploy manually:

1. **Build the app:**
   ```bash
   ./build.sh
   ```

2. **Build and deploy infrastructure:**
   ```bash
   sam build
   sam deploy
   ```

3. **Get S3 bucket name:**
   ```bash
   BUCKET_NAME=$(aws cloudformation describe-stacks \
     --stack-name knowledge-hub-web \
     --query 'Stacks[0].Outputs[?OutputKey==`S3BucketName`].OutputValue' \
     --output text \
     --region us-east-1)
   ```

4. **Sync files to S3:**
   ```bash
   aws s3 sync dist/ "s3://$BUCKET_NAME/" --delete --region us-east-1
   ```

5. **Invalidate CloudFront cache:**
   ```bash
   DIST_ID=$(aws cloudformation describe-stacks \
     --stack-name knowledge-hub-web \
     --query 'Stacks[0].Outputs[?OutputKey==`CloudFrontDistributionId`].OutputValue' \
     --output text \
     --region us-east-1)
   
   aws cloudfront create-invalidation \
     --distribution-id "$DIST_ID" \
     --paths "/*" \
     --region us-east-1
   ```

### Configuration

Edit `samconfig.toml` to customize:
- Stack name (default: `knowledge-hub-web`)
- AWS region (default: `us-east-1`)

### Architecture

The deployment uses:
- **S3**: Static website hosting for the built Svelte app
- **CloudFront**: CDN distribution for global content delivery and HTTPS
- **Origin Access Identity (OAI)**: Secure access to S3 bucket through CloudFront

### Important Notes

- CloudFront distribution takes 15-20 minutes to fully propagate after creation
- SPA routing is handled by CloudFront error page configuration (404 → index.html)
- The API URL must be set at build time via the `VITE_API_URL` environment variable
- After deploying the web app, you must update the API CORS configuration to include the CloudFront URL
- Files are cached with appropriate cache-control headers (HTML files have shorter cache, assets have longer cache)

### Troubleshooting

**Build fails:**
- Ensure `VITE_API_URL` is set if you need a custom API URL
- Check that all dependencies are installed (`pnpm install`)

**Deployment fails:**
- Verify AWS credentials are configured (`aws configure`)
- Check that you have permissions for S3, CloudFront, and CloudFormation
- Ensure SAM CLI is installed and up to date

**CORS errors after deployment:**
- Make sure you've updated the API CORS configuration to include your CloudFront URL
- Verify the CloudFront URL format (should include `https://`)

**CloudFront shows old content:**
- CloudFront caches content. Wait for cache invalidation to complete (usually a few minutes)
- You can manually invalidate the cache using the AWS CLI (see manual deployment steps)
