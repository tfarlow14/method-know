from fastapi import APIRouter, HTTPException, Body, status, Depends
from pydantic import BaseModel, EmailStr
from models.user import UserModel, User, UserResponse, UserCollection
from utils.auth import hash_password, verify_password, create_access_token, get_current_user
from services import dynamodb

router = APIRouter(prefix="/users", tags=["users"])

class LoginRequest(BaseModel):
	email: EmailStr
	password: str

class LoginResponse(BaseModel):
	user: UserResponse
	token: str

@router.post("/login", response_model=LoginResponse)
async def login(credentials: LoginRequest = Body(...)):
	# Find user by email using DynamoDB GSI
	user_item = await dynamodb.get_user_by_email(credentials.email)
	if not user_item:
		raise HTTPException(status_code=401, detail="Invalid email or password")
	
	user = User.from_dynamodb_item(user_item)
	
	# Verify password
	if not verify_password(credentials.password, user.password):
		raise HTTPException(status_code=401, detail="Invalid email or password")
	
	# Generate JWT token
	token = create_access_token(user.user_id)
	
	# Return user data and token
	user_response = UserResponse(
		id=user.user_id,
		first_name=user.first_name,
		last_name=user.last_name,
		email=user.email
	)
	return LoginResponse(
		user=user_response,
		token=token
	)

class SignupResponse(BaseModel):
	user: UserResponse
	token: str

@router.post("", response_model=SignupResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserModel = Body(...)):
    # Check if email already exists using DynamoDB GSI
    existing_user_item = await dynamodb.get_user_by_email(user.email)
    if existing_user_item:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user with hashed password
    user_data = {
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': user.email,
        'password': hash_password(user.password)
    }
    user_item = await dynamodb.create_user(user_data)
    new_user = User.from_dynamodb_item(user_item)
    
    # Generate JWT token for the new user
    token = create_access_token(new_user.user_id)
    
    user_response = UserResponse(
        id=new_user.user_id,
        first_name=new_user.first_name,
        last_name=new_user.last_name,
        email=new_user.email
    )
    return SignupResponse(
        user=user_response,
        token=token
    )

@router.get("", response_model=UserCollection)
async def list_users(current_user: User = Depends(get_current_user)):
    """List all users (requires authentication)"""
    user_items = await dynamodb.list_users()
    # Convert to UserResponse to exclude passwords
    user_responses = [
        UserResponse(
            id=item['user_id'],
            first_name=item['first_name'],
            last_name=item['last_name'],
            email=item['email']
        )
        for item in user_items
    ]
    return UserCollection(users=user_responses)

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current authenticated user's information"""
    return UserResponse(
        id=current_user.user_id,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        email=current_user.email
    )

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: str):
    user_item = await dynamodb.get_user_by_id(user_id)
    if not user_item:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserResponse(
        id=user_item['user_id'],
        first_name=user_item['first_name'],
        last_name=user_item['last_name'],
        email=user_item['email']
    )

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str, 
    user: UserModel = Body(...),
    current_user: User = Depends(get_current_user)
):
    """Update user (requires authentication, can only update own profile)"""
    existing_user_item = await dynamodb.get_user_by_id(user_id)
    if not existing_user_item:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if email is being changed to an existing email
    if user.email != existing_user_item['email']:
        email_exists = await dynamodb.get_user_by_email(user.email)
        if email_exists:
            raise HTTPException(status_code=400, detail="Email already registered")
    
    # Update user fields
    update_data = {
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': user.email,
        'password': hash_password(user.password)
    }
    updated_user_item = await dynamodb.update_user(user_id, update_data)
    
    return UserResponse(
        id=updated_user_item['user_id'],
        first_name=updated_user_item['first_name'],
        last_name=updated_user_item['last_name'],
        email=updated_user_item['email']
    )

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete user (requires authentication)"""
    user_item = await dynamodb.get_user_by_id(user_id)
    if not user_item:
        raise HTTPException(status_code=404, detail="User not found")
    
    await dynamodb.delete_user(user_id)
    return None
