"""Campaign endpoints for AI Ad Generator API.
Provides CRUD operations for managing ad campaigns.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from src.database.models import User, Campaign
from src.database.operations import (
    create_campaign, get_campaign,
    update_campaign, delete_campaign
)
from src.api.schemas import CampaignCreate, CampaignResponse
from src.api.dependencies import get_db, get_current_user

router = APIRouter(prefix="/api/campaigns", tags=["campaigns"])

@router.post("/", response_model=CampaignResponse)
async def create_new_campaign(
    campaign: CampaignCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new ad campaign."""
    db_campaign = create_campaign(db, current_user.id, campaign.dict())
    return CampaignResponse.from_orm(db_campaign)

@router.get("/{campaign_id}", response_model=CampaignResponse)
async def get_campaign_by_id(
    campaign_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get campaign details by ID."""
    db_campaign = get_campaign(db, campaign_id)
    if not db_campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    if db_campaign.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this campaign"
        )
    return CampaignResponse.from_orm(db_campaign)

@router.put("/{campaign_id}", response_model=CampaignResponse)
async def update_campaign_by_id(
    campaign_id: int,
    campaign_update: CampaignCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update campaign details."""
    db_campaign = get_campaign(db, campaign_id)
    if not db_campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    if db_campaign.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this campaign"
        )
    updated_campaign = update_campaign(db, campaign_id, campaign_update.dict())
    return CampaignResponse.from_orm(updated_campaign)

@router.delete("/{campaign_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_campaign_by_id(
    campaign_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a campaign."""
    db_campaign = get_campaign(db, campaign_id)
    if not db_campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    if db_campaign.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this campaign"
        )
    delete_campaign(db, campaign_id)

@router.get("/", response_model=List[CampaignResponse])
async def get_user_campaigns(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all campaigns for the authenticated user."""
    campaigns = db.query(Campaign).filter(Campaign.user_id == current_user.id).all()
    return [CampaignResponse.from_orm(campaign) for campaign in campaigns]