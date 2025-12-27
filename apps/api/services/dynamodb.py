import os
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
import boto3
from botocore.exceptions import ClientError

# Detect environment
IS_LAMBDA = os.getenv('AWS_LAMBDA_FUNCTION_NAME') is not None

# Lazy initialization
_dynamodb_resource = None
_dynamodb_client = None

def get_dynamodb_resource():
    """Get DynamoDB resource - works in Lambda and local dev."""
    global _dynamodb_resource
    if _dynamodb_resource is None:
        endpoint_url = os.getenv('AWS_ENDPOINT_URL')
        region_name = os.getenv('AWS_REGION') or os.getenv('AWS_DEFAULT_REGION')
        
        if IS_LAMBDA:
            # Lambda: IAM role provides credentials automatically, region from environment
            _dynamodb_resource = boto3.resource(
                'dynamodb',
                endpoint_url=endpoint_url,
                region_name=region_name
            ) if endpoint_url or region_name else boto3.resource('dynamodb')
        else:
            # Local: Use AWS profile from environment variable (AWS Toolkit/SSO)
            profile = os.getenv('AWS_PROFILE')
            if profile:
                session = boto3.Session(profile_name=profile, region_name=region_name)
                _dynamodb_resource = session.resource('dynamodb', endpoint_url=endpoint_url) if endpoint_url else session.resource('dynamodb')
            else:
                # No profile specified - use default boto3 credential chain
                _dynamodb_resource = boto3.resource(
                    'dynamodb',
                    endpoint_url=endpoint_url,
                    region_name=region_name
                ) if endpoint_url or region_name else boto3.resource('dynamodb')
    
    return _dynamodb_resource

def get_dynamodb_client():
    """Get DynamoDB client - works in Lambda and local dev."""
    global _dynamodb_client
    if _dynamodb_client is None:
        endpoint_url = os.getenv('AWS_ENDPOINT_URL')
        region_name = os.getenv('AWS_REGION') or os.getenv('AWS_DEFAULT_REGION')
        
        if IS_LAMBDA:
            _dynamodb_client = boto3.client(
                'dynamodb',
                endpoint_url=endpoint_url,
                region_name=region_name
            ) if endpoint_url or region_name else boto3.client('dynamodb')
        else:
            # Local: Use AWS profile from environment variable (AWS Toolkit/SSO)
            profile = os.getenv('AWS_PROFILE')
            if profile:
                session = boto3.Session(profile_name=profile, region_name=region_name)
                _dynamodb_client = session.client('dynamodb', endpoint_url=endpoint_url) if endpoint_url else session.client('dynamodb')
            else:
                # No profile specified - use default boto3 credential chain
                _dynamodb_client = boto3.client(
                    'dynamodb',
                    endpoint_url=endpoint_url,
                    region_name=region_name
                ) if endpoint_url or region_name else boto3.client('dynamodb')
    
    return _dynamodb_client

# Table names - use TABLE_PREFIX to construct table names
TABLE_PREFIX = os.getenv('TABLE_PREFIX')
if not TABLE_PREFIX:
    raise ValueError("TABLE_PREFIX environment variable is required")

# Construct table names from prefix (e.g., "knowledge-hub-api" -> "knowledge-hub-api-users")
USERS_TABLE_NAME = f"{TABLE_PREFIX}-users"
TAGS_TABLE_NAME = f"{TABLE_PREFIX}-tags"
RESOURCES_TABLE_NAME = f"{TABLE_PREFIX}-resources"

# Helper functions to get tables
def get_users_table():
    return get_dynamodb_resource().Table(USERS_TABLE_NAME)

def get_tags_table():
    return get_dynamodb_resource().Table(TAGS_TABLE_NAME)

def get_resources_table():
    return get_dynamodb_resource().Table(RESOURCES_TABLE_NAME)


# Helper functions for DynamoDB item conversion
def serialize_dynamodb_item(item: Dict[str, Any]) -> Dict[str, Any]:
    """Convert Python types to DynamoDB-compatible types."""
    result = {}
    for key, value in item.items():
        if value is None:
            continue
        elif isinstance(value, str):
            result[key] = value
        elif isinstance(value, bool):
            result[key] = value
        elif isinstance(value, int):
            result[key] = value
        elif isinstance(value, float):
            result[key] = value
        elif isinstance(value, list):
            result[key] = value
        elif isinstance(value, datetime):
            result[key] = value.isoformat()
        else:
            result[key] = str(value)
    return result


def deserialize_dynamodb_item(item: Dict[str, Any]) -> Dict[str, Any]:
    """Convert DynamoDB item to Python dict."""
    result = {}
    for key, value in item.items():
        # Parse datetime fields (created_at, updated_at, etc.)
        if isinstance(value, str) and (key.endswith('_at') or key == 'created_at'):
            try:
                # Handle ISO format strings with or without timezone
                if value.endswith('Z'):
                    result[key] = datetime.fromisoformat(value.replace('Z', '+00:00'))
                else:
                    result[key] = datetime.fromisoformat(value)
            except (ValueError, AttributeError, TypeError):
                # If parsing fails, keep as string
                result[key] = value
        else:
            result[key] = value
    return result


# User operations
async def create_user(user_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a new user in DynamoDB."""
    user_id = str(uuid.uuid4())
    item = {
        'user_id': user_id,
        'first_name': user_data['first_name'],
        'last_name': user_data['last_name'],
        'email': user_data['email'],
        'password': user_data['password'],
    }
    item = serialize_dynamodb_item(item)
    
    try:
        get_users_table().put_item(Item=item)
        return item
    except ClientError as e:
        raise Exception(f"Error creating user: {str(e)}")


async def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    """Get a user by user_id."""
    try:
        response = get_users_table().get_item(Key={'user_id': user_id})
        if 'Item' in response:
            return deserialize_dynamodb_item(response['Item'])
        return None
    except ClientError as e:
        raise Exception(f"Error getting user: {str(e)}")


async def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """Get a user by email using GSI."""
    try:
        response = get_users_table().query(
            IndexName='email-index',
            KeyConditionExpression='email = :email',
            ExpressionAttributeValues={':email': email}
        )
        if response['Items']:
            return deserialize_dynamodb_item(response['Items'][0])
        return None
    except ClientError as e:
        raise Exception(f"Error getting user by email: {str(e)}")


async def update_user(user_id: str, user_data: Dict[str, Any]) -> Dict[str, Any]:
    """Update a user in DynamoDB."""
    update_expression_parts = []
    expression_attribute_values = {}
    expression_attribute_names = {}
    
    for key, value in user_data.items():
        if key != 'user_id' and value is not None:
            update_expression_parts.append(f"#{key} = :{key}")
            expression_attribute_names[f"#{key}"] = key
            expression_attribute_values[f":{key}"] = value
    
    if not update_expression_parts:
        return await get_user_by_id(user_id)
    
    update_expression = "SET " + ", ".join(update_expression_parts)
    
    try:
        response = get_users_table().update_item(
            Key={'user_id': user_id},
            UpdateExpression=update_expression,
            ExpressionAttributeNames=expression_attribute_names,
            ExpressionAttributeValues=serialize_dynamodb_item(expression_attribute_values),
            ReturnValues='ALL_NEW'
        )
        return deserialize_dynamodb_item(response['Attributes'])
    except ClientError as e:
        raise Exception(f"Error updating user: {str(e)}")


async def delete_user(user_id: str) -> None:
    """Delete a user from DynamoDB."""
    try:
        get_users_table().delete_item(Key={'user_id': user_id})
    except ClientError as e:
        raise Exception(f"Error deleting user: {str(e)}")


async def list_users() -> List[Dict[str, Any]]:
    """List all users."""
    try:
        response = get_users_table().scan()
        return [deserialize_dynamodb_item(item) for item in response['Items']]
    except ClientError as e:
        raise Exception(f"Error listing users: {str(e)}")


# Tag operations
async def create_tag(tag_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a new tag in DynamoDB."""
    tag_id = str(uuid.uuid4())
    item = {
        'tag_id': tag_id,
        'name': tag_data['name'],
    }
    item = serialize_dynamodb_item(item)
    
    try:
        get_tags_table().put_item(Item=item)
        return item
    except ClientError as e:
        raise Exception(f"Error creating tag: {str(e)}")


async def get_tag_by_id(tag_id: str) -> Optional[Dict[str, Any]]:
    """Get a tag by tag_id."""
    try:
        response = get_tags_table().get_item(Key={'tag_id': tag_id})
        if 'Item' in response:
            return deserialize_dynamodb_item(response['Item'])
        return None
    except ClientError as e:
        raise Exception(f"Error getting tag: {str(e)}")


async def list_tags() -> List[Dict[str, Any]]:
    """List all tags."""
    try:
        response = get_tags_table().scan()
        return [deserialize_dynamodb_item(item) for item in response['Items']]
    except ClientError as e:
        raise Exception(f"Error listing tags: {str(e)}")


async def get_tags_by_ids(tag_ids: List[str]) -> List[Dict[str, Any]]:
    """Get multiple tags by their IDs."""
    if not tag_ids:
        return []
    
    try:
        # Use individual get_item calls for simplicity
        # For small batches, this is fine. For larger batches, consider using
        # the low-level client with proper DynamoDB format conversion
        table = get_tags_table()
        items = []
        
        for tag_id in tag_ids:
            response = table.get_item(Key={'tag_id': tag_id})
            if 'Item' in response:
                items.append(response['Item'])
        
        return [deserialize_dynamodb_item(item) for item in items]
    except ClientError as e:
        raise Exception(f"Error getting tags by IDs: {str(e)}")


# Resource operations
async def create_resource(resource_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a new resource in DynamoDB."""
    resource_id = str(uuid.uuid4())
    item = {
        'resource_id': resource_id,
        'title': resource_data['title'],
        'description': resource_data['description'],
        'type': resource_data['type'],
        'user_id': resource_data['user_id'],
        'tag_ids': resource_data.get('tag_ids', []),
        'created_at': datetime.utcnow().isoformat(),
    }
    
    # Add optional fields based on type
    if 'url' in resource_data:
        item['url'] = resource_data['url']
    if 'code' in resource_data:
        item['code'] = resource_data['code']
    if 'author' in resource_data:
        item['author'] = resource_data['author']
    
    item = serialize_dynamodb_item(item)
    
    try:
        get_resources_table().put_item(Item=item)
        return item
    except ClientError as e:
        raise Exception(f"Error creating resource: {str(e)}")


async def get_resource_by_id(resource_id: str) -> Optional[Dict[str, Any]]:
    """Get a resource by resource_id."""
    try:
        response = get_resources_table().get_item(Key={'resource_id': resource_id})
        if 'Item' in response:
            return deserialize_dynamodb_item(response['Item'])
        return None
    except ClientError as e:
        raise Exception(f"Error getting resource: {str(e)}")


async def update_resource(resource_id: str, resource_data: Dict[str, Any]) -> Dict[str, Any]:
    """Update a resource in DynamoDB."""
    update_expression_parts = []
    expression_attribute_values = {}
    expression_attribute_names = {}
    
    for key, value in resource_data.items():
        if key != 'resource_id' and value is not None:
            update_expression_parts.append(f"#{key} = :{key}")
            expression_attribute_names[f"#{key}"] = key
            if isinstance(value, list):
                expression_attribute_values[f":{key}"] = value
            else:
                expression_attribute_values[f":{key}"] = value
    
    if not update_expression_parts:
        return await get_resource_by_id(resource_id)
    
    update_expression = "SET " + ", ".join(update_expression_parts)
    
    try:
        response = get_resources_table().update_item(
            Key={'resource_id': resource_id},
            UpdateExpression=update_expression,
            ExpressionAttributeNames=expression_attribute_names,
            ExpressionAttributeValues=serialize_dynamodb_item(expression_attribute_values),
            ReturnValues='ALL_NEW'
        )
        return deserialize_dynamodb_item(response['Attributes'])
    except ClientError as e:
        raise Exception(f"Error updating resource: {str(e)}")


async def delete_resource(resource_id: str) -> None:
    """Delete a resource from DynamoDB."""
    try:
        get_resources_table().delete_item(Key={'resource_id': resource_id})
    except ClientError as e:
        raise Exception(f"Error deleting resource: {str(e)}")


async def list_resources() -> List[Dict[str, Any]]:
    """List all resources."""
    try:
        response = get_resources_table().scan()
        return [deserialize_dynamodb_item(item) for item in response['Items']]
    except ClientError as e:
        raise Exception(f"Error listing resources: {str(e)}")


async def get_resources_by_user_id(user_id: str) -> List[Dict[str, Any]]:
    """Get all resources for a specific user using GSI."""
    try:
        response = get_resources_table().query(
            IndexName='user_id-index',
            KeyConditionExpression='user_id = :user_id',
            ExpressionAttributeValues={':user_id': user_id}
        )
        return [deserialize_dynamodb_item(item) for item in response['Items']]
    except ClientError as e:
        raise Exception(f"Error getting resources by user_id: {str(e)}")

