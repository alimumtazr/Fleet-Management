from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
import bcrypt  # Import bcrypt directly for version check
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from database import SessionLocal
# Removed User import to avoid circular imports
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
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        # Handle potential encoding issues
        if isinstance(plain_password, str):
            plain_password = plain_password.encode('utf-8')
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        print(f"Password verification error: {str(e)}")
        # Fallback to direct bcrypt comparison if passlib fails
        try:
            return bcrypt.checkpw(
                plain_password if isinstance(plain_password, bytes) else plain_password.encode('utf-8'),
                hashed_password.encode('utf-8') if isinstance(hashed_password, str) else hashed_password
            )
        except Exception as e2:
            print(f"Bcrypt direct verification error: {str(e2)}")
            return False

def get_password_hash(password: str) -> str:
    try:
        # Handle potential encoding issues
        if isinstance(password, str):
            password = password.encode('utf-8')
        return pwd_context.hash(password)
    except Exception as e:
        print(f"Password hashing error: {str(e)}")
        # Fallback to direct bcrypt hashing if passlib fails
        try:
            salt = bcrypt.gensalt(rounds=12)
            hashed = bcrypt.hashpw(
                password if isinstance(password, bytes) else password.encode('utf-8'),
                salt
            )
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

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(SessionLocal)):
    """
    Validate the JWT token and return the current user.
    This function is used by the /api/auth/me endpoint.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # If no token is provided, return 401 Unauthorized
    if token is None:
        print("No token provided")
        raise credentials_exception

    try:
        # Print token for debugging (only first few characters for security)
        print(f"Decoding token: {token[:10]}...")

        # Decode the JWT token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # Extract the user ID from the token
        user_id: str = payload.get("sub")
        if user_id is None:
            print("Token does not contain user ID")
            raise credentials_exception

        print(f"Token decoded, user_id: {user_id}")

        # Check token expiration
        exp = payload.get("exp")
        if exp is None:
            print("Token does not contain expiration")
            raise credentials_exception

        # Convert exp to datetime for comparison
        exp_datetime = datetime.fromtimestamp(exp, tz=timezone.utc)
        if datetime.now(timezone.utc) >= exp_datetime:
            print("Token has expired")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
                headers={"WWW-Authenticate": "Bearer"},
            )

    except JWTError as e:
        print(f"JWT Error: {str(e)}")
        raise credentials_exception

    # Import here to avoid circular imports
    from main import DBUser

    # Get the user from the database
    try:
        user = db.query(DBUser).filter(DBUser.id == user_id).first()
        if user is None:
            print(f"User not found for id: {user_id}")
            raise credentials_exception

        print(f"User found: {user.email}")
        return user
    except Exception as e:
        print(f"Database error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error",
        )

def get_current_active_user(current_user = Depends(get_current_user)):
    """
    Check if the current user is active.
    This function is used by endpoints that require an active user.
    """
    try:
        if not current_user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is inactive"
            )
        return current_user
    except AttributeError:
        # This can happen if current_user is not a valid user object
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )