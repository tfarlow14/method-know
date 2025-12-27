#!/usr/bin/env python3
"""
Script to create DynamoDB tables for local development.
Run this once to set up your local DynamoDB tables.
"""

import os
import boto3
from botocore.exceptions import ClientError

# Load environment variables
if os.path.exists('.env.local'):
    with open('.env.local') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()

# Get configuration
table_prefix = os.getenv('TABLE_PREFIX')
if not table_prefix:
    print("Error: TABLE_PREFIX environment variable is required")
    print("Set it in .env.local or export it before running this script")
    exit(1)

region = os.getenv('AWS_REGION', 'us-east-1')
profile = os.getenv('AWS_PROFILE')

# Create DynamoDB client
if profile:
    session = boto3.Session(profile_name=profile, region_name=region)
    dynamodb = session.client('dynamodb')
else:
    dynamodb = boto3.client('dynamodb', region_name=region)

def create_users_table():
    """Create the users table with email-index GSI."""
    table_name = f"{table_prefix}-users"
    
    try:
        response = dynamodb.create_table(
            TableName=table_name,
            AttributeDefinitions=[
                {'AttributeName': 'user_id', 'AttributeType': 'S'},
                {'AttributeName': 'email', 'AttributeType': 'S'}
            ],
            KeySchema=[
                {'AttributeName': 'user_id', 'KeyType': 'HASH'}
            ],
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'email-index',
                    'KeySchema': [
                        {'AttributeName': 'email', 'KeyType': 'HASH'}
                    ],
                    'Projection': {
                        'ProjectionType': 'ALL'
                    }
                }
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        print(f"✅ Created table: {table_name}")
        return response
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceInUseException':
            print(f"⚠️  Table {table_name} already exists")
        else:
            print(f"❌ Error creating {table_name}: {e}")
            raise

def create_tags_table():
    """Create the tags table."""
    table_name = f"{table_prefix}-tags"
    
    try:
        response = dynamodb.create_table(
            TableName=table_name,
            AttributeDefinitions=[
                {'AttributeName': 'tag_id', 'AttributeType': 'S'}
            ],
            KeySchema=[
                {'AttributeName': 'tag_id', 'KeyType': 'HASH'}
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        print(f"✅ Created table: {table_name}")
        return response
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceInUseException':
            print(f"⚠️  Table {table_name} already exists")
        else:
            print(f"❌ Error creating {table_name}: {e}")
            raise

def create_resources_table():
    """Create the resources table with user_id-index GSI."""
    table_name = f"{table_prefix}-resources"
    
    try:
        response = dynamodb.create_table(
            TableName=table_name,
            AttributeDefinitions=[
                {'AttributeName': 'resource_id', 'AttributeType': 'S'},
                {'AttributeName': 'user_id', 'AttributeType': 'S'}
            ],
            KeySchema=[
                {'AttributeName': 'resource_id', 'KeyType': 'HASH'}
            ],
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'user_id-index',
                    'KeySchema': [
                        {'AttributeName': 'user_id', 'KeyType': 'HASH'}
                    ],
                    'Projection': {
                        'ProjectionType': 'ALL'
                    }
                }
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        print(f"✅ Created table: {table_name}")
        return response
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceInUseException':
            print(f"⚠️  Table {table_name} already exists")
        else:
            print(f"❌ Error creating {table_name}: {e}")
            raise

if __name__ == '__main__':
    print(f"Creating DynamoDB tables with prefix: {table_prefix}")
    print(f"Region: {region}")
    print(f"Profile: {profile or 'default'}")
    print()
    
    try:
        create_users_table()
        create_tags_table()
        create_resources_table()
        print()
        print("✅ All tables created successfully!")
    except Exception as e:
        print(f"\n❌ Failed to create tables: {e}")
        exit(1)

