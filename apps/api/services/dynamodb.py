import os
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
import boto3
from botocore.exceptions import ClientError

# Initialize DynamoDB client (reused across Lambda invocations)
# Support local DynamoDB for development via AWS_ENDPOINT_URL environment variable
endpoint_url = os.getenv('AWS_ENDPOINT_URL')
if endpoint_url:
    dynamodb = boto3.resource('dynamodb', endpoint_url=endpoint_url)
    dynamodb_client = boto3.client('dynamodb', endpoint_url=endpoint_url)
else:
    dynamodb = boto3.resource('dynamodb')
    dynamodb_client = boto3.client('dynamodb')

# Table names from environment variables
USERS_TABLE_NAME = os.getenv('USERS_TABLE_NAME', 'users')
TAGS_TABLE_NAME = os.getenv('TAGS_TABLE_NAME', 'tags')
RESOURCES_TABLE_NAME = os.getenv('RESOURCES_TABLE_NAME', 'resources')

# Get table resources
users_table = dynamodb.Table(USERS_TABLE_NAME)
tags_table = dynamodb.Table(TAGS_TABLE_NAME)
resources_table = dynamodb.Table(RESOURCES_TABLE_NAME)


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
        if isinstance(value, str) and key.endswith('_at') or key == 'created_at':
            try:
                result[key] = datetime.fromisoformat(value.replace('Z', '+00:00'))
            except:
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
        users_table.put_item(Item=item)
        return item
    except ClientError as e:
        raise Exception(f"Error creating user: {str(e)}")


async def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    """Get a user by user_id."""
    try:
        response = users_table.get_item(Key={'user_id': user_id})
        if 'Item' in response:
            return deserialize_dynamodb_item(response['Item'])
        return None
    except ClientError as e:
        raise Exception(f"Error getting user: {str(e)}")


async def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """Get a user by email using GSI."""
    try:
        response = users_table.query(
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
        response = users_table.update_item(
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
        users_table.delete_item(Key={'user_id': user_id})
    except ClientError as e:
        raise Exception(f"Error deleting user: {str(e)}")


async def list_users() -> List[Dict[str, Any]]:
    """List all users."""
    try:
        response = users_table.scan()
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
        tags_table.put_item(Item=item)
        return item
    except ClientError as e:
        raise Exception(f"Error creating tag: {str(e)}")


async def get_tag_by_id(tag_id: str) -> Optional[Dict[str, Any]]:
    """Get a tag by tag_id."""
    try:
        response = tags_table.get_item(Key={'tag_id': tag_id})
        if 'Item' in response:
            return deserialize_dynamodb_item(response['Item'])
        return None
    except ClientError as e:
        raise Exception(f"Error getting tag: {str(e)}")


async def list_tags() -> List[Dict[str, Any]]:
    """List all tags."""
    try:
        response = tags_table.scan()
        return [deserialize_dynamodb_item(item) for item in response['Items']]
    except ClientError as e:
        raise Exception(f"Error listing tags: {str(e)}")


async def get_tags_by_ids(tag_ids: List[str]) -> List[Dict[str, Any]]:
    """Get multiple tags by their IDs."""
    if not tag_ids:
        return []
    
    try:
        # Use batch_get_item for efficiency
        response = dynamodb_client.batch_get_item(
            RequestItems={
                TAGS_TABLE_NAME: {
                    'Keys': [{'tag_id': tag_id} for tag_id in tag_ids]
                }
            }
        )
        items = response.get('Responses', {}).get(TAGS_TABLE_NAME, [])
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
        resources_table.put_item(Item=item)
        return item
    except ClientError as e:
        raise Exception(f"Error creating resource: {str(e)}")


async def get_resource_by_id(resource_id: str) -> Optional[Dict[str, Any]]:
    """Get a resource by resource_id."""
    try:
        response = resources_table.get_item(Key={'resource_id': resource_id})
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
        response = resources_table.update_item(
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
        resources_table.delete_item(Key={'resource_id': resource_id})
    except ClientError as e:
        raise Exception(f"Error deleting resource: {str(e)}")


async def list_resources() -> List[Dict[str, Any]]:
    """List all resources."""
    try:
        response = resources_table.scan()
        return [deserialize_dynamodb_item(item) for item in response['Items']]
    except ClientError as e:
        raise Exception(f"Error listing resources: {str(e)}")


async def get_resources_by_user_id(user_id: str) -> List[Dict[str, Any]]:
    """Get all resources for a specific user using GSI."""
    try:
        response = resources_table.query(
            IndexName='user_id-index',
            KeyConditionExpression='user_id = :user_id',
            ExpressionAttributeValues={':user_id': user_id}
        )
        return [deserialize_dynamodb_item(item) for item in response['Items']]
    except ClientError as e:
        raise Exception(f"Error getting resources by user_id: {str(e)}")

