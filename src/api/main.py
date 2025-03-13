"""FastAPI application for AI Ad Generator.
Provides REST API endpoints for user management, campaigns, and ad generation.
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from datetime import datetime

from src.database.supabase_operations import (
    create_user, get_user_by_email, get_user_by_username
)
from src.api.schemas import (
    UserCreate, UserLogin, UserResponse,
    CampaignCreate, CampaignResponse,
    AdScriptCreate, AdScriptResponse,
    Token
)
from src.api.dependencies import get_supabase, get_current_user
from src.api.campaigns import router as campaigns_router
from src.api.ad_scripts import router as ad_scripts_router
from supabase import Client

# Initialize FastAPI app
app = FastAPI(
    title="AI Ad Generator API",
    description="REST API for generating AI-powered ad content",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(campaigns_router)
app.include_router(ad_scripts_router)

@app.post("/api/register", response_model=UserResponse)
async def register_user(
    user: UserCreate,
    supabase: Client = Depends(get_supabase)
):
    """Register a new user."""
    # Check if username or email already exists
    if get_user_by_username(user.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    if get_user_by_email(user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    try:
        # Create user in Supabase Auth with auto-confirm
        auth_response = supabase.auth.sign_up({
            "email": user.email,
            "password": user.password,
            "options": {
                "data": {
                    "username": user.username
                },
                "email_confirm": True  # Auto-confirm email
            }
        })
        
        if not auth_response.user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create user"
            )
        
        # Create user in our users table with the Supabase Auth user ID
        db_user = create_user(
            username=user.username,
            email=user.email,
            password=user.password,
            user_id=auth_response.user.id  # Pass the Supabase Auth user ID
        )
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create user record"
            )
        
        # Auto sign in after registration
        auth_response = supabase.auth.sign_in_with_password({
            "email": user.email,
            "password": user.password
        })
        
        return UserResponse(
            id=auth_response.user.id,
            username=user.username,
            email=user.email,
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
    except Exception as e:
        print(f"Registration error: {str(e)}")  # Debug log
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@app.post("/api/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    supabase: Client = Depends(get_supabase)
):
    """Login endpoint that returns JWT tokens."""
    try:
        print(f"Attempting login for email: {form_data.username}")  # Debug log
        
        # Try to sign in with regular client
        auth_response = supabase.auth.sign_in_with_password({
            "email": form_data.username,
            "password": form_data.password
        })
        
        print(f"Auth response: {auth_response}")  # Debug log
        
        if not auth_response.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Return both access and refresh tokens
        return {
            "access_token": auth_response.session.access_token,
            "refresh_token": auth_response.session.refresh_token,
            "token_type": "bearer"
        }
            
    except Exception as e:
        print(f"Login error: {str(e)}")  # Debug log
        # Check if the error is from Supabase
        if hasattr(e, 'json'):
            error_details = e.json()
            print(f"Supabase error details: {error_details}")  # Debug log
            
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

# Health check endpoint
@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.utcnow()}