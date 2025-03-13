"""Supabase database operations for AI Ad Generator."""

from typing import List, Optional, Dict
from datetime import datetime
import json
from passlib.hash import bcrypt
from supabase import Client

from src.database.supabase_config import get_supabase_client

def create_user(username: str, email: str, password: str, user_id: str = None) -> Dict:
    """Create a new user.
    
    Args:
        username (str): Unique username
        email (str): Unique email address
        password (str): User's password
        user_id (str): Optional Supabase Auth user ID
        
    Returns:
        Dict: Created user data
    """
    supabase = get_supabase_client()
    password_hash = bcrypt.hash(password)
    
    user_data = {
        'id': user_id,  # Use the Supabase Auth user ID
        'username': username,
        'email': email,
        'password_hash': password_hash,
        'is_active': True,
        'created_at': datetime.utcnow().isoformat(),
        'updated_at': datetime.utcnow().isoformat()
    }
    
    result = supabase.table('users').insert(user_data).execute()
    return result.data[0] if result.data else None

def get_user_by_email(email: str) -> Optional[Dict]:
    """Get user by email.
    
    Args:
        email (str): Email to search for
        
    Returns:
        Optional[Dict]: User data if found, None otherwise
    """
    supabase = get_supabase_client()
    result = supabase.table('users').select('*').eq('email', email).execute()
    return result.data[0] if result.data else None

def get_user_by_id(user_id: int) -> Optional[Dict]:
    """Get user by ID.
    
    Args:
        user_id (int): User ID
        
    Returns:
        Optional[Dict]: User data if found, None otherwise
    """
    supabase = get_supabase_client()
    result = supabase.table('users').select('*').eq('id', user_id).execute()
    return result.data[0] if result.data else None

def get_user_by_username(username: str) -> Optional[Dict]:
    """Get user by username.
    
    Args:
        username (str): Username to search for
        
    Returns:
        Optional[Dict]: User data if found, None otherwise
    """
    supabase = get_supabase_client()
    result = supabase.table('users').select('*').eq('username', username).execute()
    return result.data[0] if result.data else None

def update_user(user_id: int, user_data: Dict) -> Optional[Dict]:
    """Update existing user.
    
    Args:
        user_id (int): User ID
        user_data (Dict): Updated user data
        
    Returns:
        Optional[Dict]: Updated user data if found, None otherwise
    """
    supabase = get_supabase_client()
    
    if 'password' in user_data:
        user_data['password_hash'] = bcrypt.hash(user_data.pop('password'))
    
    user_data['updated_at'] = datetime.utcnow().isoformat()
    result = supabase.table('users').update(user_data).eq('id', user_id).execute()
    return result.data[0] if result.data else None

def create_campaign(user_id: str, campaign_data: Dict) -> Dict:
    """Create a new campaign.
    
    Args:
        user_id (str): User ID (UUID)
        campaign_data (Dict): Campaign data including product info
        
    Returns:
        Dict: Created campaign data
    """
    supabase = get_supabase_client()
    
    # Create a new dict with only the fields we want to insert
    campaign_insert = {
        'user_id': user_id,
        'product_name': campaign_data.get('product_name'),
        'product_description': campaign_data.get('product_description'),
        'target_audience': campaign_data.get('target_audience'),
        'key_use_cases': campaign_data.get('key_use_cases'),
        'campaign_goal': campaign_data.get('campaign_goal'),
        'niche': campaign_data.get('niche'),
        'created_at': datetime.utcnow().isoformat(),
        'updated_at': datetime.utcnow().isoformat()
    }
    
    result = supabase.table('campaigns').insert(campaign_insert).execute()
    return result.data[0] if result.data else None

def get_campaign(campaign_id: int) -> Optional[Dict]:
    """Get campaign by ID.
    
    Args:
        campaign_id (int): Campaign ID
        
    Returns:
        Optional[Dict]: Campaign data if found, None otherwise
    """
    supabase = get_supabase_client()
    result = supabase.table('campaigns').select('*').eq('id', campaign_id).execute()
    return result.data[0] if result.data else None

def update_campaign(campaign_id: int, campaign_data: Dict) -> Optional[Dict]:
    """Update existing campaign.
    
    Args:
        campaign_id (int): Campaign ID
        campaign_data (Dict): Updated campaign data
        
    Returns:
        Optional[Dict]: Updated campaign data if found, None otherwise
    """
    supabase = get_supabase_client()
    
    campaign_data['updated_at'] = datetime.utcnow().isoformat()
    result = supabase.table('campaigns').update(campaign_data).eq('id', campaign_id).execute()
    return result.data[0] if result.data else None

def delete_campaign(campaign_id: int) -> bool:
    """Delete campaign by ID.
    
    Args:
        campaign_id (int): Campaign ID
        
    Returns:
        bool: True if deleted, False if not found
    """
    supabase = get_supabase_client()
    
    # Due to cascade delete in Supabase, this will automatically delete associated ad_scripts
    result = supabase.table('campaigns').delete().eq('id', campaign_id).execute()
    return bool(result.data)

def create_ad_script(campaign_id: str, content: str,
                    provider: str, model: str, platform: str = None,
                    reddit_references: List[Dict] = None) -> Dict:
    """Create a new ad script.
    
    Args:
        campaign_id (str): Associated campaign ID (UUID)
        content (str): Generated ad script content
        provider (str): LLM provider used (openai, claude, groq)
        model (str): Specific model used
        platform (str, optional): Target platform
        reddit_references (List[Dict], optional): Referenced Reddit posts data
        
    Returns:
        Dict: Created ad script data
    """
    supabase = get_supabase_client()
    
    ad_script_data = {
        'campaign_id': campaign_id,
        'content': content,
        'provider': provider,
        'model': model,
        'platform': platform,
        'reddit_references': reddit_references,
        'created_at': datetime.utcnow().isoformat()
    }
    
    result = supabase.table('ad_scripts').insert(ad_script_data).execute()
    return result.data[0] if result.data else None

def get_campaign_ad_scripts(campaign_id: str) -> List[Dict]:
    """Get all ad scripts for a campaign.
    
    Args:
        campaign_id (str): Campaign ID (UUID)
        
    Returns:
        List[Dict]: List of ad scripts for the campaign
    """
    supabase = get_supabase_client()
    result = supabase.table('ad_scripts').select('*').eq('campaign_id', campaign_id).execute()
    return result.data

def get_ad_script(ad_script_id: str) -> Optional[Dict]:
    """Get ad script by ID.
    
    Args:
        ad_script_id (str): Ad script ID (UUID)
        
    Returns:
        Optional[Dict]: Ad script data if found, None otherwise
    """
    supabase = get_supabase_client()
    result = supabase.table('ad_scripts').select('*').eq('id', ad_script_id).execute()
    return result.data[0] if result.data else None

def delete_ad_script_by_id(supabase: Client, ad_script_id: str) -> bool:
    """Delete ad script by ID.
    
    Args:
        supabase (Client): Supabase client instance
        ad_script_id (str): Ad script ID (UUID)
        
    Returns:
        bool: True if deleted, False if not found
    """
    try:
        result = supabase.table('ad_scripts').delete().eq('id', ad_script_id).execute()
        return bool(result.data)
    except Exception as e:
        print(f"Error deleting ad script: {str(e)}")
        return False 