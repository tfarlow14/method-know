from fastapi import APIRouter, HTTPException, Body, status, Depends
from pydantic import BaseModel, EmailStr
from models.user import UserModel, User, UserResponse, UserCollection
from utils.auth import hash_password, verify_password, create_access_token, get_current_user

router = APIRouter(prefix="/users", tags=["users"])

class LoginRequest(BaseModel):
	email: EmailStr
	password: str

class LoginResponse(BaseModel):
	user: UserResponse
	token: str

@router.post("/login", response_model=LoginResponse)
async def login(credentials: LoginRequest = Body(...)):
	# Find user by email using Beanie
	user = await User.find_one(User.email == credentials.email)
	if not user:
		raise HTTPException(status_code=401, detail="Invalid email or password")
	
	# Verify password
	if not verify_password(credentials.password, user.password):
		raise HTTPException(status_code=401, detail="Invalid email or password")
	
	# Generate JWT token
	token = create_access_token(str(user.id))
	
	# Return user data and token
	user_response = UserResponse(
		id=str(user.id),
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
    # Check if email already exists using Beanie
    existing_user = await User.find_one(User.email == user.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user with hashed password
    new_user = User(
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        password=hash_password(user.password)
    )
    await new_user.insert()
    
    # Generate JWT token for the new user
    token = create_access_token(str(new_user.id))
    
    user_response = UserResponse(
        id=str(new_user.id),
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
    users = await User.find_all().to_list()
    # Convert to UserResponse to exclude passwords
    user_responses = [
        UserResponse(
            id=str(user.id),
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email
        )
        for user in users
    ]
    return UserCollection(users=user_responses)

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current authenticated user's information"""
    return UserResponse(
        id=str(current_user.id),
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        email=current_user.email
    )

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: str):
    user = await User.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserResponse(
        id=str(user.id),
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email
    )

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str, 
    user: UserModel = Body(...),
    current_user: User = Depends(get_current_user)
):
    """Update user (requires authentication, can only update own profile)"""
    existing_user = await User.get(user_id)
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if email is being changed to an existing email
    if user.email != existing_user.email:
        email_exists = await User.find_one(User.email == user.email)
        if email_exists:
            raise HTTPException(status_code=400, detail="Email already registered")
    
    # Update user fields
    existing_user.first_name = user.first_name
    existing_user.last_name = user.last_name
    existing_user.email = user.email
    # Hash password if it's being updated
    existing_user.password = hash_password(user.password)
    
    await existing_user.save()
    
    return UserResponse(
        id=str(existing_user.id),
        first_name=existing_user.first_name,
        last_name=existing_user.last_name,
        email=existing_user.email
    )

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete user (requires authentication)"""
    user = await User.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    await user.delete()
    return None
