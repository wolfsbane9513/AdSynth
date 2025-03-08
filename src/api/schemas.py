"""Pydantic models for request/response validation.
Defines schemas for users, campaigns, and ad scripts.
"""

from pydantic import BaseModel, EmailStr, validator
from typing import List, Optional
from datetime import datetime
import json

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
    id: int
    
    class Config:
        from_attributes = True

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
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Ad script schemas
class AdScriptBase(BaseModel):
    provider: str
    model: str
    reddit_references: Optional[List[dict]] = None

    @validator('reddit_references', pre=True)
    def parse_reddit_references(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return None
        return v

class AdScriptCreate(AdScriptBase):
    campaign_id: int

class AdScriptResponse(AdScriptBase):
    id: int
    campaign_id: int
    content: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# Token schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None