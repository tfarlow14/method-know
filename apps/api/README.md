# Knowledge Hub API

FastAPI application deployed to AWS Lambda with DynamoDB backend.

## Architecture

- **Framework**: FastAPI
- **Runtime**: AWS Lambda (Python 3.11)
- **Database**: DynamoDB
- **Deployment**: AWS SAM (Serverless Application Model)

## Local Development

### Prerequisites

- Python 3.11+
- AWS CLI configured with credentials (for DynamoDB access)
- Or use [DynamoDB Local](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/DynamoDBLocal.html) for local testing

### Setup

1. Install dependencies:
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

2. Set environment variables:
```bash
export TABLE_PREFIX=knowledge-hub-api
export CORS_ORIGINS=http://localhost:5173,http://localhost:4173
export JWT_SECRET_KEY=your-secret-key-here
```

3. Run the development server:
```bash
./dev.sh
# Or manually:
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### Using DynamoDB Local

If you want to test locally without AWS credentials:

1. Download and run [DynamoDB Local](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/DynamoDBLocal.html)
2. Set AWS endpoint:
```bash
export AWS_ENDPOINT_URL=http://localhost:8000
```
3. Update `services/dynamodb.py` to use the local endpoint:
```python
dynamodb = boto3.resource('dynamodb', endpoint_url=os.getenv('AWS_ENDPOINT_URL'))
dynamodb_client = boto3.client('dynamodb', endpoint_url=os.getenv('AWS_ENDPOINT_URL'))
```

## Deployment to AWS Lambda

### Prerequisites

- AWS CLI installed and configured
- AWS SAM CLI installed (`brew install aws-sam-cli` or see [SAM docs](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html))
- Appropriate AWS permissions for Lambda, API Gateway, and DynamoDB

### Deploy Steps

1. **Build the application:**
```bash
sam build
```

2. **Deploy to AWS:**
```bash
sam deploy
```

Or deploy with custom parameters:
```bash
sam deploy --parameter-overrides \
  CORSOrigins="https://yourdomain.com" \
  JWTSecretKey="your-production-secret-key"
```

3. **Get the API URL:**
After deployment, SAM will output the API Gateway URL. You can also find it in:
- AWS Console → API Gateway
- Or run: `aws cloudformation describe-stacks --stack-name knowledge-hub-api --query 'Stacks[0].Outputs'`

### Configuration

Edit `samconfig.toml` to customize:
- Stack name
- AWS region
- CORS origins
- JWT secret key

## Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `TABLE_PREFIX` | Prefix for table names (e.g., "knowledge-hub-api" creates "knowledge-hub-api-users") | Yes | - |
| `CORS_ORIGINS` | Comma-separated list of allowed origins | Yes | - |
| `JWT_SECRET_KEY` | Secret key for JWT token signing | Yes | - |
| `AWS_ENDPOINT_URL` | DynamoDB endpoint (for local development) | No | - |

## DynamoDB Tables

The application uses three DynamoDB tables:

1. **Users Table** (`{stack-name}-users`)
   - Partition Key: `user_id`
   - GSI: `email-index` on `email`

2. **Tags Table** (`{stack-name}-tags`)
   - Partition Key: `tag_id`

3. **Resources Table** (`{stack-name}-resources`)
   - Partition Key: `resource_id`
   - GSI: `user_id-index` on `user_id`

All tables use **PAY_PER_REQUEST** billing mode.

## API Endpoints

- `POST /users` - Create user (signup)
- `POST /users/login` - Login
- `GET /users` - List users (authenticated)
- `GET /users/me` - Get current user (authenticated)
- `GET /users/{user_id}` - Get user by ID
- `PUT /users/{user_id}` - Update user (authenticated)
- `DELETE /users/{user_id}` - Delete user (authenticated)

- `POST /tags` - Create tag (authenticated)
- `GET /tags` - List all tags

- `POST /resources` - Create resource (authenticated)
- `GET /resources` - List all resources (authenticated)
- `GET /resources/user/{user_id}` - Get resources by user (authenticated)
- `PUT /resources/{resource_id}` - Update resource (authenticated)
- `DELETE /resources/{resource_id}` - Delete resource (authenticated)

## Testing Locally with SAM

You can test the Lambda function locally:

```bash
sam local start-api
```

This will start a local API Gateway that mimics the Lambda environment.

## Project Structure

```
apps/api/
├── main.py              # FastAPI app and Lambda handler
├── models/              # Pydantic models
├── routers/             # API route handlers
├── services/            # DynamoDB service layer
├── utils/               # Utilities (auth, etc.)
├── template.yaml        # SAM template
├── samconfig.toml       # SAM configuration
├── build.sh             # Build script
└── requirements.txt     # Python dependencies
```

## Notes

- The Lambda handler is defined in `main.py` as `handler = Mangum(app)`
- DynamoDB client is initialized in `services/dynamodb.py` and reused across invocations
- No connection management needed - boto3 clients are stateless
- API Gateway has a 30-second timeout limit

