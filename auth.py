from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
import bcrypt  # Import bcrypt directly for version check
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from database import get_db
import os
from dotenv import load_dotenv

load_dotenv()

# Security configuration
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Print bcrypt version for debugging
print(f"Using bcrypt version: {bcrypt.__version__}")

# Use a more specific CryptContext configuration
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12  # Adjust rounds for security/performance balance
)

# Use HTTPBearer for token handling
security = HTTPBearer(auto_error=False)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        # First try with passlib's built-in verification
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        print(f"Password verification error with passlib: {str(e)}")
        # Fallback to direct bcrypt comparison if passlib fails
        try:
            # Ensure proper encoding
            if isinstance(plain_password, str):
                plain_password = plain_password.encode('utf-8')
            
            if isinstance(hashed_password, str):
                hashed_password = hashed_password.encode('utf-8')
            
            return bcrypt.checkpw(plain_password, hashed_password)
        except Exception as e2:
            print(f"Bcrypt direct verification error: {str(e2)}")
            return False

def get_password_hash(password: str) -> str:
    try:
        return pwd_context.hash(password)
    except Exception as e:
        print(f"Password hashing error with passlib: {str(e)}")
        # Fallback to direct bcrypt hashing if passlib fails
        try:
            # Ensure proper encoding
            if isinstance(password, str):
                password = password.encode('utf-8')
                
            salt = bcrypt.gensalt(rounds=12)
            hashed = bcrypt.hashpw(password, salt)
            return hashed.decode('utf-8')
        except Exception as e2:
            print(f"Bcrypt direct hashing error: {str(e2)}")
            raise

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Import here to avoid circular imports
from models import User as DBUser

async def get_current_user(
    auth_credentials: HTTPAuthorizationCredentials = Depends(security),
    request: Request = None,
    db: Session = Depends(get_db)
):
    """
    Validate the JWT token and return the current user.
    This function is used by the /api/auth/me endpoint.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Try to get token from HTTPBearer first
    token = None
    if auth_credentials:
        token = auth_credentials.credentials
        print(f"Token from HTTPBearer: {token[:10]}..." if token else "No token from HTTPBearer")
    
    # If no token from HTTPBearer, try to get from request header directly
    if not token and request:
        auth_header = request.headers.get("Authorization")
        print(f"Auth header from request: {auth_header}")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header[7:]  # Remove 'Bearer ' prefix
            print(f"Token from request header: {token[:10]}...")
    
    if not token:
        print("No token found")
        raise credentials_exception

    try:
        # Decode the JWT token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Extract the user ID from the token
        user_id: str = payload.get("sub")
        if user_id is None:
            print("Token does not contain user ID")
            raise credentials_exception

        print(f"Token decoded, user_id: {user_id}")
        
        # Get the user from the database
        user = db.query(DBUser).filter(DBUser.id == user_id).first()
        if user is None:
            print(f"User not found for id: {user_id}")
            raise credentials_exception

        print(f"User found: {user.email}")
        return user
        
    except JWTError as e:
        print(f"JWT Error: {str(e)}")
        raise credentials_exception
    except Exception as e:
        print(f"Unexpected error in get_current_user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing authentication: {str(e)}",
        )

async def get_current_active_user(current_user: DBUser = Depends(get_current_user)):
    """
    Check if the current user is active.
    This is a dependency that can be used by endpoints that require an active user.
    """
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive")
    return current_user
