"""Dependencies for FastAPI application.
Provides Supabase client and authentication dependencies.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Optional
from postgrest.exceptions import APIError
import jwt

from src.database.supabase_config import get_supabase_client
from supabase import Client

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/token")

def get_supabase() -> Client:
    """Get Supabase client."""
    return get_supabase_client()

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    supabase: Client = Depends(get_supabase)
) -> dict:
    """Get current authenticated user from Supabase JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Set the access token for the client
        supabase.postgrest.auth(token)
        
        # Get user data from the token
        decoded = jwt.decode(token, options={"verify_signature": False})
        user_id = decoded.get('sub')
        
        if not user_id:
            raise credentials_exception
            
        # Return user data
        return {
            "id": user_id,
            "email": decoded.get('email'),
            "username": decoded.get('username')
        }
        
    except (jwt.InvalidTokenError, APIError):
        raise credentials_exception