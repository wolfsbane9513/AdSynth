"""Ad script endpoints for AI Ad Generator API.
Provides operations for generating and managing ad scripts.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from src.database.models import User
from src.database.operations import (
    create_ad_script, get_campaign_ad_scripts,
    get_ad_script, update_ad_script, delete_ad_script,
    get_campaign
)
from src.generation import openai_generator, claude_generator, groq_generator
from src.scraping.reddit import get_relevant_posts
from src.api.schemas import AdScriptCreate, AdScriptResponse
from src.api.dependencies import get_db, get_current_user

router = APIRouter(prefix="/api/ad-scripts", tags=["ad-scripts"])

@router.post("/generate", response_model=AdScriptResponse)
async def generate_ad_script(
    ad_request: AdScriptCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate a new ad script using specified LLM provider."""
    # Verify campaign ownership
    campaign = get_campaign(db, ad_request.campaign_id)
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    if campaign.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this campaign"
        )
    
    # Get relevant Reddit posts
    reddit_posts = get_relevant_posts(
        product_name=campaign.product_name,
        niche=campaign.niche,
        limit=5
    )
    
    # Generate ad content based on provider
    if ad_request.provider.lower() == "openai":
        generator = openai_generator
    elif ad_request.provider.lower() == "claude":
        generator = claude_generator
    elif ad_request.provider.lower() == "groq":
        generator = groq_generator
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid provider specified"
        )
    
    content = generator.generate_ad(
        product_name=campaign.product_name,
        product_description=campaign.product_description,
        target_audience=campaign.target_audience,
        key_use_cases=campaign.key_use_cases,
        campaign_goal=campaign.campaign_goal,
        reddit_posts=reddit_posts
    )
    
    # Create ad script in database
    db_ad_script = create_ad_script(
        db,
        campaign_id=ad_request.campaign_id,
        content=content,
        provider=ad_request.provider,
        model=ad_request.model,
        reddit_references=reddit_posts
    )
    return AdScriptResponse.from_orm(db_ad_script)

@router.get("/campaign/{campaign_id}", response_model=List[AdScriptResponse])
async def get_campaign_scripts(
    campaign_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all ad scripts for a campaign."""
    campaign = get_campaign(db, campaign_id)
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    if campaign.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this campaign"
        )
    
    ad_scripts = get_campaign_ad_scripts(db, campaign_id)
    return [AdScriptResponse.from_orm(script) for script in ad_scripts]

@router.put("/{ad_script_id}", response_model=AdScriptResponse)
async def update_ad_script_content(
    ad_script_id: int,
    content_update: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update ad script content."""
    ad_script = get_ad_script(db, ad_script_id)
    if not ad_script:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ad script not found"
        )
    
    campaign = get_campaign(db, ad_script.campaign_id)
    if campaign.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this ad script"
        )
    
    updated_script = update_ad_script(db, ad_script_id, content_update["content"])
    return AdScriptResponse.from_orm(updated_script)

@router.delete("/{ad_script_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ad_script_by_id(
    ad_script_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an ad script."""
    ad_script = get_ad_script(db, ad_script_id)
    if not ad_script:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ad script not found"
        )
    
    campaign = get_campaign(db, ad_script.campaign_id)
    if campaign.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this ad script"
        )
    
    delete_ad_script(db, ad_script_id)