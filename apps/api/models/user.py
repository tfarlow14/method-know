from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict

class UserModel(BaseModel):
    """Pydantic model for user creation/updates"""
    first_name: str
    last_name: str
    email: EmailStr
    password: str  # Note: In production, this should be hashed

class User(BaseModel):
    """User model for DynamoDB"""
    user_id: str
    first_name: str
    last_name: str
    email: EmailStr
    password: str  # Hashed password
    
    @classmethod
    def from_dynamodb_item(cls, item: dict) -> "User":
        """Create User from DynamoDB item."""
        return cls(
            user_id=item.get('user_id', ''),
            first_name=item.get('first_name', ''),
            last_name=item.get('last_name', ''),
            email=item.get('email', ''),
            password=item.get('password', '')
        )
    
    def to_dynamodb_item(self) -> dict:
        """Convert User to DynamoDB item."""
        return {
            'user_id': self.user_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'password': self.password
        }
    
    @property
    def id(self) -> str:
        """Alias for user_id for compatibility."""
        return self.user_id

class UserResponse(BaseModel):
    """User model without password for responses"""
    id: str
    first_name: str
    last_name: str
    email: EmailStr

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )

class UserCollection(BaseModel):
    users: list[UserResponse]
