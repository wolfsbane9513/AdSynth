"""Ad script endpoints for AI Ad Generator API.
Provides operations for generating and managing ad scripts.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict
from supabase import Client
from uuid import UUID
from pydantic import BaseModel

from src.database.supabase_operations import (
    create_ad_script, get_campaign_ad_scripts,
    get_ad_script, get_campaign, delete_ad_script_by_id
)
from src.generation import openai_generator, claude_generator, groq_generator
from src.scraping.reddit import get_relevant_posts
from src.api.schemas import AdScriptCreate, AdScriptResponse
from src.api.dependencies import get_supabase, get_current_user
from src.multi_agent.orchestrator import AdGeneratorOrchestrator

router = APIRouter(prefix="/api/ad-scripts", tags=["ad-scripts"])

def serialize_uuid(obj):
    """Helper function to serialize UUID objects to strings."""
    if isinstance(obj, UUID):
        return str(obj)
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

# Add request model for content update
class AdScriptContentUpdate(BaseModel):
    content: str

# Add response model for delete operation
class DeleteResponse(BaseModel):
    success: bool
    message: str
    id: str

@router.post("/generate", response_model=AdScriptResponse)
async def generate_ad_script(
    ad_request: AdScriptCreate,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    """Generate a new ad script using specified LLM provider."""
    # Verify campaign ownership
    campaign = get_campaign(ad_request.campaign_id)
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    if campaign["user_id"] != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this campaign"
        )
    
    # Initialize Reddit client and orchestrator
    from src.scraping.reddit import init_reddit_client
    reddit_client = init_reddit_client()
    
    # Initialize the orchestrator with specified provider
    orchestrator = AdGeneratorOrchestrator(
        reddit_client=reddit_client,
        llm_provider=ad_request.provider.lower(),
        model_name=ad_request.model,
        debug=False
    )
    
    # Prepare product info for the orchestrator
    product_info = {
        "product_name": campaign["product_name"],
        "product_description": campaign["product_description"],
        "target_audience": campaign["target_audience"],
        "use_cases": campaign["key_use_cases"],
        "campaign_goal": campaign["campaign_goal"],
        "niche": campaign["niche"],
        "keywords": ""  # Set empty string as default since keywords field doesn't exist
    }
    
    # Generate ad using multi-agent approach
    try:
        # Ensure platform has a default value
        platform = ad_request.platform or "general"
        
        results = orchestrator.generate_ad(
            product_info=product_info,
            platform=platform,
            skip_reddit=ad_request.skip_reddit,
            generate_runbook=ad_request.runbook,
            save_intermediates=True
        )
        
        # Convert any UUID objects to strings in the results
        import json
        results_json = json.loads(json.dumps(results, default=serialize_uuid))
        
        # Create new ad script record
        ad_script = create_ad_script(
            campaign_id=str(ad_request.campaign_id),  # Convert UUID to string
            content=results_json["final_ad_script"],
            provider=ad_request.provider,
            model=ad_request.model or "default",
            platform=ad_request.platform,
            reddit_references=results_json.get("reddit_references", [])
        )
        
        # Prepare response
        response = AdScriptResponse(**ad_script)
        
        # Add runbook content if it was generated
        if ad_request.runbook and results_json.get("runbook", {}).get("generated", False):
            with open(results_json["runbook"]["path"], "r", encoding="utf-8") as f:
                response.runbook_content = f.read()
        
        return response
        
    except Exception as e:
        # Log the error and return appropriate error response
        print(f"Error during ad generation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ad generation failed: {str(e)}"
        )

@router.get("/campaign/{campaign_id}", response_model=List[AdScriptResponse])
async def get_campaign_scripts(
    campaign_id: str,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    """Get all ad scripts for a campaign."""
    # Validate campaign_id format
    if campaign_id == "NaN" or not campaign_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid campaign ID"
        )
    
    try:
        # Verify campaign ownership
        campaign = get_campaign(campaign_id)
        if not campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )
        if campaign["user_id"] != current_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this campaign"
            )
        
        # Get ad scripts
        scripts = get_campaign_ad_scripts(campaign_id)
        return [AdScriptResponse(**script) for script in scripts]
    except Exception as e:
        if "invalid input syntax for type uuid" in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid campaign ID format. Expected a UUID."
            )
        raise

@router.put("/{ad_script_id}", response_model=AdScriptResponse)
async def update_ad_script_content(
    ad_script_id: UUID,  # Changed from int to UUID
    content_update: AdScriptContentUpdate,  # Use Pydantic model
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    """Update ad script content.
    
    Args:
        ad_script_id (UUID): The ID of the ad script to update
        content_update (AdScriptContentUpdate): The new content
        current_user (dict): The authenticated user
        supabase (Client): Supabase client
        
    Returns:
        AdScriptResponse: The updated ad script
        
    Raises:
        HTTPException: If script not found or user not authorized
    """
    try:
        # Get the ad script
        ad_script = get_ad_script(str(ad_script_id))  # Convert UUID to string
        if not ad_script:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ad script not found"
            )
        
        # Check ownership through campaign
        campaign = get_campaign(ad_script["campaign_id"])
        if not campaign or campaign["user_id"] != current_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to modify this ad script"
            )
        
        # Update the ad script content
        result = supabase.table('ad_scripts').update({
            "content": content_update.content  # Access content through Pydantic model
        }).eq('id', str(ad_script_id)).execute()  # Convert UUID to string
        
        updated_script = result.data[0] if result.data else None
        
        if not updated_script:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update ad script"
            )
        
        return AdScriptResponse(**updated_script)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid UUID format: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating ad script: {str(e)}"
        )

@router.delete("/{ad_script_id}", response_model=DeleteResponse)
async def delete_ad_script_endpoint(  # Renamed to avoid naming conflict
    ad_script_id: UUID,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    """Delete an ad script.
    
    Args:
        ad_script_id (UUID): The UUID of the ad script to delete
        current_user (dict): The authenticated user
        supabase (Client): Supabase client
        
    Returns:
        DeleteResponse: Success message with ad script ID
        
    Raises:
        HTTPException: If ad script not found, user not authorized, or deletion fails
    """
    try:
        print(f"Attempting to delete ad script with ID: {ad_script_id}")
        
        # Get ad script to verify ownership
        ad_script = get_ad_script(str(ad_script_id))
        print(f"Found ad script: {ad_script}")
        
        if not ad_script:
            print(f"Ad script not found with ID: {ad_script_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ad script not found"
            )
            
        # Get campaign to verify ownership
        campaign = get_campaign(ad_script["campaign_id"])
        print(f"Found campaign: {campaign}")
        
        if not campaign or campaign["user_id"] != current_user["id"]:
            print(f"Authorization failed. Campaign user_id: {campaign['user_id']}, Current user: {current_user['id']}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this ad script"
            )
            
        # Delete the ad script
        script_id_str = str(ad_script_id)
        delete_result = delete_ad_script_by_id(supabase, script_id_str)
        print(f"Delete operation result: {delete_result}")
        
        if not delete_result:
            print("Delete operation returned False")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete ad script"
            )
            
        # Return success response
        return DeleteResponse(
            success=True,
            message=f"Ad script {ad_script_id} successfully deleted",
            id=script_id_str
        )
        
    except ValueError as e:
        print(f"ValueError occurred: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid ad script ID format: {str(e)}"
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"Unexpected error occurred: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting ad script: {str(e)}"
        )