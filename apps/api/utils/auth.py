import hashlib
import bcrypt
import jwt
import os
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from models.user import User

# JWT secret key - in production, use environment variable
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

# HTTP Bearer token scheme
security = HTTPBearer()

def hash_password(password: str) -> str:
    """Hash a password using SHA256 + bcrypt to handle any password length."""
    # First hash with SHA256 to handle any length password
    sha256_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
    # Then hash with bcrypt for security
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(sha256_hash.encode('utf-8'), salt).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    # Hash with SHA256 first to match hashing behavior
    sha256_hash = hashlib.sha256(plain_password.encode('utf-8')).hexdigest()
    return bcrypt.checkpw(sha256_hash.encode('utf-8'), hashed_password.encode('utf-8'))

def create_access_token(user_id: str) -> str:
    """Create a JWT access token for a user."""
    now = datetime.utcnow()
    expiration = now + timedelta(hours=JWT_EXPIRATION_HOURS)
    payload = {
        "sub": user_id,  # subject (user ID)
        "exp": int(expiration.timestamp()),  # expiration time as Unix timestamp
        "iat": int(now.timestamp())  # issued at as Unix timestamp (for auditing, not verified)
    }
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    # Ensure token is a string (PyJWT 2.0+ returns string, older versions return bytes)
    if isinstance(token, bytes):
        return token.decode('utf-8')
    return token

def verify_token(token: str) -> dict:
    """Verify and decode a JWT token."""
    if not token or not token.strip():
        raise ValueError("Token is empty or invalid")
    
    # Trim whitespace from token
    token = token.strip()
    
    try:
        # Disable iat (issued at) verification to avoid clock skew issues
        # The exp (expiration) claim is what matters for security
        # iat is mainly for auditing/logging and isn't critical for token validation
        payload = jwt.decode(
            token, 
            JWT_SECRET_KEY, 
            algorithms=[JWT_ALGORITHM],
            options={
                "verify_signature": True, 
                "verify_exp": True, 
                "verify_iat": False  # Disable iat verification to avoid clock skew issues
            }
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError("Token has expired")
    except jwt.DecodeError as e:
        raise ValueError(f"Token decode error: {str(e)}")
    except jwt.InvalidTokenError as e:
        raise ValueError(f"Invalid token: {str(e)}")

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """
    Dependency to get the current authenticated user from JWT token.
    Use this in route handlers that require authentication.
    
    Example:
        @router.get("/protected")
        async def protected_route(current_user: User = Depends(get_current_user)):
            return {"user_id": str(current_user.id)}
    """
    from services import dynamodb
    
    token = credentials.credentials
    try:
        payload = verify_token(token)
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload: missing user ID"
            )
        
        user_item = await dynamodb.get_user_by_id(user_id)
        if not user_item:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"User not found for ID: {user_id}"
            )
        
        return User.from_dynamodb_item(user_item)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {str(e)}"
        )

async def get_current_user_optional(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer(auto_error=False))
) -> User | None:
    """
    Optional dependency to get the current authenticated user.
    Returns None if no token is provided (doesn't raise an error).
    Use this for routes that work with or without authentication.
    """
    if not credentials:
        return None
    
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None
