"""Campaign endpoints for AI Ad Generator API.
Provides CRUD operations for managing ad campaigns.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict
from supabase import Client
from pydantic import BaseModel

from src.database.supabase_operations import (
    create_campaign, get_campaign,
    update_campaign, delete_campaign
)
from src.api.schemas import CampaignCreate, CampaignResponse
from src.api.dependencies import get_supabase, get_current_user

router = APIRouter(prefix="/api/campaigns", tags=["campaigns"])

# Add response model for delete operation
class DeleteResponse(BaseModel):
    success: bool
    message: str
    id: str

@router.post("/", response_model=CampaignResponse)
async def create_new_campaign(
    campaign: CampaignCreate,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    """Create a new ad campaign."""
    # Create campaign with authenticated user's ID
    db_campaign = create_campaign(current_user["id"], campaign.dict())
    if not db_campaign:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create campaign"
        )
    return CampaignResponse(**db_campaign)

@router.get("/{campaign_id}", response_model=CampaignResponse)
async def get_campaign_by_id(
    campaign_id: str,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    """Get campaign details by ID."""
    # Validate campaign_id format
    if campaign_id == "NaN" or not campaign_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid campaign ID"
        )
    
    try:
        db_campaign = get_campaign(campaign_id)
        if not db_campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )
        if db_campaign["user_id"] != current_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this campaign"
            )
        return CampaignResponse(**db_campaign)
    except Exception as e:
        if "invalid input syntax for type uuid" in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid campaign ID format. Expected a UUID."
            )
        raise

@router.put("/{campaign_id}", response_model=CampaignResponse)
async def update_campaign_by_id(
    campaign_id: str,
    campaign_update: CampaignCreate,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    """Update campaign details."""
    db_campaign = get_campaign(campaign_id)
    if not db_campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    if db_campaign["user_id"] != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this campaign"
        )
    updated_campaign = update_campaign(campaign_id, campaign_update.dict())
    return CampaignResponse(**updated_campaign)

@router.delete("/{campaign_id}", response_model=DeleteResponse)
async def delete_campaign_by_id(
    campaign_id: str,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    """Delete a campaign and its associated ad scripts.
    
    Args:
        campaign_id (str): The UUID of the campaign to delete
        current_user (dict): The authenticated user
        supabase (Client): Supabase client
        
    Returns:
        DeleteResponse: Success message with campaign ID
        
    Raises:
        HTTPException: If campaign not found, user not authorized, or deletion fails
    """
    try:
        # Validate campaign exists and user owns it
        db_campaign = get_campaign(campaign_id)
        if not db_campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )
        if db_campaign["user_id"] != current_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this campaign"
            )
        
        # Attempt to delete the campaign
        if not delete_campaign(campaign_id):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete campaign"
            )
        
        # Return success response
        return DeleteResponse(
            success=True,
            message=f"Campaign {campaign_id} successfully deleted",
            id=campaign_id
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid campaign ID format: {str(e)}"
        )
    except HTTPException:
        raise  # Re-raise HTTP exceptions as is
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting campaign: {str(e)}"
        )

@router.get("/", response_model=List[CampaignResponse])
async def get_user_campaigns(
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    """Get all campaigns for the authenticated user."""
    result = supabase.table('campaigns').select('*').eq('user_id', current_user["id"]).execute()
    return [CampaignResponse(**campaign) for campaign in result.data]