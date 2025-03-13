"""Pydantic models for request/response validation.
Defines schemas for users, campaigns, and ad scripts.
"""

from pydantic import BaseModel, EmailStr, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID

# User schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(UserBase):
    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

# Campaign schemas
class CampaignBase(BaseModel):
    product_name: str
    product_description: str
    target_audience: str
    key_use_cases: str
    campaign_goal: str
    niche: str

class CampaignCreate(CampaignBase):
    pass

class CampaignResponse(CampaignBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

# Ad script schemas
class AdScriptBase(BaseModel):
    campaign_id: UUID
    provider: str
    model: Optional[str] = None
    platform: Optional[str] = None
    skip_reddit: bool = False
    runbook: bool = False

class AdScriptCreate(AdScriptBase):
    pass

class AdScriptResponse(BaseModel):
    id: UUID
    campaign_id: UUID
    content: str
    provider: str
    model: str
    platform: Optional[str] = None
    reddit_references: Optional[List[Dict[str, Any]]] = None
    runbook_content: Optional[str] = None
    created_at: datetime

# Token schemas
class Token(BaseModel):
    """Token response model."""
    access_token: str
    refresh_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None