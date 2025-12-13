#!/usr/bin/env python3
"""
Script to create a resource with a created_at timestamp and associate a tag with it.
Usage: python create_resource.py
"""

import asyncio
from datetime import datetime
from database import connect_to_mongo, close_mongo_connection
from models.user import User
from models.tag import Tag
from models.resource import Resource
from utils.auth import hash_password


async def create_resource_with_tag():
    """Create a resource with a tag and created_at timestamp"""
    
    # Connect to database
    await connect_to_mongo()
    print("Connected to database")
    
    try:
        # Find or create a user
        user = await User.find_one(User.email == "test@example.com")
        if not user:
            print("Creating test user...")
            user = User(
                first_name="Test",
                last_name="User",
                email="test@example.com",
                password=hash_password("testpassword123")
            )
            await user.insert()
            print(f"Created user: {user.email}")
        else:
            print(f"Using existing user: {user.email}")
        
        # Create or find a tag
        tag_name = "Python"
        tag = await Tag.find_one(Tag.name == tag_name)
        if not tag:
            print(f"Creating tag: {tag_name}")
            tag = Tag(name=tag_name)
            await tag.insert()
            print(f"Created tag: {tag.name}")
        else:
            print(f"Using existing tag: {tag.name}")
        
        # Create a resource with created_at timestamp
        resource_title = "Python Best Practices"
        resource = Resource(
            title=resource_title,
            description="A comprehensive guide to Python best practices and coding standards.",
            type="article",
            user=user,
            tags=[tag],
            url="https://docs.python.org/3/tutorial/",
            created_at=datetime.utcnow()  # Explicitly set created_at timestamp
        )
        
        await resource.insert()
        await resource.fetch_all_links()
        
        print(f"\n✅ Successfully created resource:")
        print(f"   Title: {resource.title}")
        print(f"   Type: {resource.type}")
        print(f"   Created at: {resource.created_at}")
        print(f"   Tag: {tag.name}")
        print(f"   User: {user.first_name} {user.last_name}")
        print(f"   Resource ID: {resource.id}")
        
    except Exception as e:
        print(f"❌ Error creating resource: {e}")
        raise
    finally:
        await close_mongo_connection()
        print("\nDatabase connection closed")


if __name__ == "__main__":
    asyncio.run(create_resource_with_tag())

