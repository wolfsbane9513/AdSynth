"""Database operations for AI Ad Generator.
Provides CRUD operations for users, campaigns and ad scripts.
"""

from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from datetime import datetime
import json

from src.database.models import User, Campaign, AdScript
from src.config import supabase_client

def create_user(session: Session, username: str, email: str, password: str) -> User:
    """Create a new user.
    
    Args:
        session (Session): SQLAlchemy session
        username (str): Unique username
        email (str): Unique email address
        password (str): User's password
        
    Returns:
        User: Created user instance
    """
    user = User(username=username, email=email)
    user.set_password(password)
    session.add(user)
    session.commit()
    return user

def get_user_by_id(session: Session, user_id: int) -> Optional[User]:
    """Get user by ID.
    
    Args:
        session (Session): SQLAlchemy session
        user_id (int): User ID
        
    Returns:
        Optional[User]: User instance if found, None otherwise
    """
    return session.query(User).filter(User.id == user_id).first()

def get_user_by_username(session: Session, username: str) -> Optional[User]:
    """Get user by username.
    
    Args:
        session (Session): SQLAlchemy session
        username (str): Username to search for
        
    Returns:
        Optional[User]: User instance if found, None otherwise
    """
    return session.query(User).filter(User.username == username).first()

def get_user_by_email(session: Session, email: str) -> Optional[User]:
    """Get user by email.
    
    Args:
        session (Session): SQLAlchemy session
        email (str): Email to search for
        
    Returns:
        Optional[User]: User instance if found, None otherwise
    """
    return session.query(User).filter(User.email == email).first()

def update_user(session: Session, user_id: int, user_data: Dict) -> Optional[User]:
    """Update existing user.
    
    Args:
        session (Session): SQLAlchemy session
        user_id (int): User ID
        user_data (Dict): Updated user data
        
    Returns:
        Optional[User]: Updated user instance if found, None otherwise
    """
    user = get_user_by_id(session, user_id)
    if user:
        if 'password' in user_data:
            user.set_password(user_data.pop('password'))
        for key, value in user_data.items():
            setattr(user, key, value)
        session.commit()
    return user

def delete_user(session: Session, user_id: int) -> bool:
    """Delete user by ID.
    
    Args:
        session (Session): SQLAlchemy session
        user_id (int): User ID
        
    Returns:
        bool: True if deleted, False if not found
    """
    user = get_user_by_id(session, user_id)
    if user:
        session.delete(user)
        session.commit()
        return True
    return False

def create_campaign(session: Session, user_id: int, campaign_data: Dict) -> Campaign:
    """Create a new campaign.
    
    Args:
        session (Session): SQLAlchemy session
        user_id (int): ID of the user creating the campaign
        campaign_data (Dict): Campaign data including product info
        
    Returns:
        Campaign: Created campaign instance
    """
    campaign_data['user_id'] = user_id
    campaign = Campaign(**campaign_data)
    session.add(campaign)
    session.commit()
    return campaign

def get_campaign(session: Session, campaign_id: int) -> Optional[Campaign]:
    """Get campaign by ID.
    
    Args:
        session (Session): SQLAlchemy session
        campaign_id (int): Campaign ID
        
    Returns:
        Optional[Campaign]: Campaign instance if found, None otherwise
    """
    return session.query(Campaign).filter(Campaign.id == campaign_id).first()

def update_campaign(session: Session, campaign_id: int, campaign_data: Dict) -> Optional[Campaign]:
    """Update existing campaign.
    
    Args:
        session (Session): SQLAlchemy session
        campaign_id (int): Campaign ID
        campaign_data (Dict): Updated campaign data
        
    Returns:
        Optional[Campaign]: Updated campaign instance if found, None otherwise
    """
    campaign = get_campaign(session, campaign_id)
    if campaign:
        for key, value in campaign_data.items():
            setattr(campaign, key, value)
        session.commit()
    return campaign

def delete_campaign(session: Session, campaign_id: int) -> bool:
    """Delete campaign by ID and all associated ad scripts.
    
    Args:
        session (Session): SQLAlchemy session
        campaign_id (int): Campaign ID
        
    Returns:
        bool: True if deleted, False if not found
    """
    max_retries = 5
    retry_delay = 0.5  # seconds
    
    for attempt in range(max_retries):
        try:
            # Get campaign first to check existence
            campaign = get_campaign(session, campaign_id)
            if not campaign:
                return False
                
            # Delete associated ad scripts one by one to avoid locks
            ad_scripts = session.query(AdScript).filter(AdScript.campaign_id == campaign_id).all()
            for ad_script in ad_scripts:
                session.delete(ad_script)
                try:
                    session.flush()
                except:
                    session.rollback()
                    continue
            
            # Delete the campaign
            session.delete(campaign)
            session.commit()
            return True
                
        except Exception as e:
            session.rollback()
            if attempt < max_retries - 1:
                import time
                time.sleep(retry_delay * (attempt + 1))  # Exponential backoff
                continue
            raise
    
    return False

def create_ad_script(session: Session, campaign_id: int, content: str,
                     provider: str, model: str, reddit_references: List[Dict]) -> AdScript:
    """Create a new ad script.
    
    Args:
        session (Session): SQLAlchemy session
        campaign_id (int): Associated campaign ID
        content (str): Generated ad script content
        provider (str): LLM provider used (openai, claude, groq)
        model (str): Specific model used
        reddit_references (List[Dict]): Referenced Reddit posts data
        
    Returns:
        AdScript: Created ad script instance
    """
    ad_script = AdScript(
        campaign_id=campaign_id,
        content=content,
        provider=provider,
        model=model,
        reddit_references=json.dumps(reddit_references)
    )
    session.add(ad_script)
    session.commit()
    return ad_script

def get_campaign_ad_scripts(session: Session, campaign_id: int) -> List[AdScript]:
    """Get all ad scripts for a campaign.
    
    Args:
        session (Session): SQLAlchemy session
        campaign_id (int): Campaign ID
        
    Returns:
        List[AdScript]: List of ad scripts for the campaign
    """
    return session.query(AdScript).filter(AdScript.campaign_id == campaign_id).all()

def get_ad_script(session: Session, ad_script_id: int) -> Optional[AdScript]:
    """Get ad script by ID.
    
    Args:
        session (Session): SQLAlchemy session
        ad_script_id (int): Ad script ID
        
    Returns:
        Optional[AdScript]: Ad script instance if found, None otherwise
    """
    return session.query(AdScript).filter(AdScript.id == ad_script_id).first()

def delete_ad_script(session: Session, ad_script_id: int) -> bool:
    """Delete ad script by ID.
    
    Args:
        session (Session): SQLAlchemy session
        ad_script_id (int): Ad script ID
        
    Returns:
        bool: True if deleted, False if not found
    """
    ad_script = get_ad_script(session, ad_script_id)
    if ad_script:
        session.delete(ad_script)
        session.commit()
        return True
    return False

def update_ad_script(session: Session, ad_script_id: int, content: str) -> Optional[AdScript]:
    """Update existing ad script content.
    
    Args:
        session (Session): SQLAlchemy session
        ad_script_id (int): Ad script ID
        content (str): Updated ad script content
        
    Returns:
        Optional[AdScript]: Updated ad script instance if found, None otherwise
    """
    ad_script = get_ad_script(session, ad_script_id)
    if ad_script:
        ad_script.content = content
        session.commit()
    return ad_script

def create_user(username: str, email: str, password: str) -> dict:
    user = supabase_client.from_('users').insert({
        'username': username,
        'email': email,
        'password_hash': password
    }).execute()
    return user.data[0]

def get_user_by_id(user_id: int) -> Optional[dict]:
    result = supabase_client.from_('users').select('*').eq('id', user_id).execute()
    return result.data[0] if result.data else None

def get_user_by_username(session: Session, username: str) -> Optional[User]:
    """Get user by username.
    
    Args:
        session (Session): SQLAlchemy session
        username (str): Username to search for
        
    Returns:
        Optional[User]: User instance if found, None otherwise
    """
    return session.query(User).filter(User.username == username).first()

def get_user_by_email(session: Session, email: str) -> Optional[User]:
    """Get user by email.
    
    Args:
        session (Session): SQLAlchemy session
        email (str): Email to search for
        
    Returns:
        Optional[User]: User instance if found, None otherwise
    """
    return session.query(User).filter(User.email == email).first()

def update_user(session: Session, user_id: int, user_data: Dict) -> Optional[User]:
    """Update existing user.
    
    Args:
        session (Session): SQLAlchemy session
        user_id (int): User ID
        user_data (Dict): Updated user data
        
    Returns:
        Optional[User]: Updated user instance if found, None otherwise
    """
    user = get_user_by_id(session, user_id)
    if user:
        if 'password' in user_data:
            user.set_password(user_data.pop('password'))
        for key, value in user_data.items():
            setattr(user, key, value)
        session.commit()
    return user

def delete_user(session: Session, user_id: int) -> bool:
    """Delete user by ID.
    
    Args:
        session (Session): SQLAlchemy session
        user_id (int): User ID
        
    Returns:
        bool: True if deleted, False if not found
    """
    user = get_user_by_id(session, user_id)
    if user:
        session.delete(user)
        session.commit()
        return True
    return False

def create_campaign(session: Session, user_id: int, campaign_data: Dict) -> Campaign:
    """Create a new campaign.
    
    Args:
        session (Session): SQLAlchemy session
        user_id (int): ID of the user creating the campaign
        campaign_data (Dict): Campaign data including product info
        
    Returns:
        Campaign: Created campaign instance
    """
    campaign_data['user_id'] = user_id
    campaign = Campaign(**campaign_data)
    session.add(campaign)
    session.commit()
    return campaign

def get_campaign(session: Session, campaign_id: int) -> Optional[Campaign]:
    """Get campaign by ID.
    
    Args:
        session (Session): SQLAlchemy session
        campaign_id (int): Campaign ID
        
    Returns:
        Optional[Campaign]: Campaign instance if found, None otherwise
    """
    return session.query(Campaign).filter(Campaign.id == campaign_id).first()

def update_campaign(session: Session, campaign_id: int, campaign_data: Dict) -> Optional[Campaign]:
    """Update existing campaign.
    
    Args:
        session (Session): SQLAlchemy session
        campaign_id (int): Campaign ID
        campaign_data (Dict): Updated campaign data
        
    Returns:
        Optional[Campaign]: Updated campaign instance if found, None otherwise
    """
    campaign = get_campaign(session, campaign_id)
    if campaign:
        for key, value in campaign_data.items():
            setattr(campaign, key, value)
        session.commit()
    return campaign

def delete_campaign(session: Session, campaign_id: int) -> bool:
    """Delete campaign by ID and all associated ad scripts.
    
    Args:
        session (Session): SQLAlchemy session
        campaign_id (int): Campaign ID
        
    Returns:
        bool: True if deleted, False if not found
    """
    max_retries = 5
    retry_delay = 0.5  # seconds
    
    for attempt in range(max_retries):
        try:
            # Get campaign first to check existence
            campaign = get_campaign(session, campaign_id)
            if not campaign:
                return False
                
            # Delete associated ad scripts one by one to avoid locks
            ad_scripts = session.query(AdScript).filter(AdScript.campaign_id == campaign_id).all()
            for ad_script in ad_scripts:
                session.delete(ad_script)
                try:
                    session.flush()
                except:
                    session.rollback()
                    continue
            
            # Delete the campaign
            session.delete(campaign)
            session.commit()
            return True
                
        except Exception as e:
            session.rollback()
            if attempt < max_retries - 1:
                import time
                time.sleep(retry_delay * (attempt + 1))  # Exponential backoff
                continue
            raise
    
    return False

def create_ad_script(session: Session, campaign_id: int, content: str,
                     provider: str, model: str, reddit_references: List[Dict]) -> AdScript:
    """Create a new ad script.
    
    Args:
        session (Session): SQLAlchemy session
        campaign_id (int): Associated campaign ID
        content (str): Generated ad script content
        provider (str): LLM provider used (openai, claude, groq)
        model (str): Specific model used
        reddit_references (List[Dict]): Referenced Reddit posts data
        
    Returns:
        AdScript: Created ad script instance
    """
    ad_script = AdScript(
        campaign_id=campaign_id,
        content=content,
        provider=provider,
        model=model,
        reddit_references=json.dumps(reddit_references)
    )
    session.add(ad_script)
    session.commit()
    return ad_script

def get_campaign_ad_scripts(session: Session, campaign_id: int) -> List[AdScript]:
    """Get all ad scripts for a campaign.
    
    Args:
        session (Session): SQLAlchemy session
        campaign_id (int): Campaign ID
        
    Returns:
        List[AdScript]: List of ad scripts for the campaign
    """
    return session.query(AdScript).filter(AdScript.campaign_id == campaign_id).all()

def get_ad_script(session: Session, ad_script_id: int) -> Optional[AdScript]:
    """Get ad script by ID.
    
    Args:
        session (Session): SQLAlchemy session
        ad_script_id (int): Ad script ID
        
    Returns:
        Optional[AdScript]: Ad script instance if found, None otherwise
    """
    return session.query(AdScript).filter(AdScript.id == ad_script_id).first()

def delete_ad_script(session: Session, ad_script_id: int) -> bool:
    """Delete ad script by ID.
    
    Args:
        session (Session): SQLAlchemy session
        ad_script_id (int): Ad script ID
        
    Returns:
        bool: True if deleted, False if not found
    """
    ad_script = get_ad_script(session, ad_script_id)
    if ad_script:
        session.delete(ad_script)
        session.commit()
        return True
    return False

def update_ad_script(session: Session, ad_script_id: int, content: str) -> Optional[AdScript]:
    """Update existing ad script content.
    
    Args:
        session (Session): SQLAlchemy session
        ad_script_id (int): Ad script ID
        content (str): Updated ad script content
        
    Returns:
        Optional[AdScript]: Updated ad script instance if found, None otherwise
    """
    ad_script = get_ad_script(session, ad_script_id)
    if ad_script:
        ad_script.content = content
        session.commit()
    return ad_script