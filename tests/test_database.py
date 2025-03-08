"""Test script for database operations.
Validates database initialization and CRUD operations for users, campaigns and ad scripts.
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.models import Base, init_db
from src.database.operations import (
    create_user, get_user_by_id, get_user_by_username, get_user_by_email, update_user, delete_user,
    create_campaign, get_campaign, update_campaign, delete_campaign,
    create_ad_script, get_campaign_ad_scripts, get_ad_script, delete_ad_script
)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Test database URL (using SQLite)
DATABASE_URL = "sqlite:///test_adsynth.db"

def main():
    # Initialize database
    print("Initializing test database...")
    
    # Create database engine and drop all tables if they exist
    engine = create_engine(DATABASE_URL)
    Base.metadata.drop_all(engine)
    
    # Create all tables fresh
    Base.metadata.create_all(engine)
    
    # Create database session
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Test user creation
        print("\nTesting user creation...")
        user = create_user(session, "testuser", "test@example.com", "password123")
        print(f"Created user with ID: {user.id}")
        
        # Test user retrieval
        print("\nTesting user retrieval...")
        retrieved_user = get_user_by_id(session, user.id)
        print(f"Retrieved user: {retrieved_user.username}")
        
        # Test user authentication
        print("\nTesting user authentication...")
        assert retrieved_user.check_password("password123"), "Password check failed"
        print("Password authentication successful")
        
        # Test user update
        print("\nTesting user update...")
        update_data = {"email": "updated@example.com"}
        updated_user = update_user(session, user.id, update_data)
        print(f"Updated user email: {updated_user.email}")
        
        # Test campaign creation with user association
        print("\nTesting campaign creation...")
        campaign_data = {
            "product_name": "Test Product",
            "product_description": "A revolutionary test product",
            "target_audience": "Tech-savvy users aged 25-40",
            "key_use_cases": "Testing, Validation, Quality Assurance",
            "campaign_goal": "Increase product awareness",
            "niche": "Software Testing"
        }
        campaign = create_campaign(session, user.id, campaign_data)
        print(f"Created campaign with ID: {campaign.id}")
        
        # Verify user-campaign relationship
        print("\nVerifying user-campaign relationship...")
        assert campaign.user_id == user.id, "Campaign not properly associated with user"
        assert len(user.campaigns) > 0, "User campaigns relationship not working"
        print("User-campaign relationship verified")
        
        # Test campaign retrieval
        print("\nTesting campaign retrieval...")
        retrieved_campaign = get_campaign(session, campaign.id)
        print(f"Retrieved campaign: {retrieved_campaign.product_name}")
        
        # Test campaign update
        print("\nTesting campaign update...")
        update_data = {"product_name": "Updated Test Product"}
        updated_campaign = update_campaign(session, campaign.id, update_data)
        print(f"Updated campaign name: {updated_campaign.product_name}")
        
        # Test ad script creation
        print("\nTesting ad script creation...")
        ad_script = create_ad_script(
            session,
            campaign.id,
            "This is a test ad script content.",
            "openai",
            "gpt-4",
            [{"title": "Test Reddit Post", "url": "https://reddit.com/test"}]
        )
        print(f"Created ad script with ID: {ad_script.id}")
        
        # Test ad script retrieval
        print("\nTesting ad script retrieval...")
        campaign_scripts = get_campaign_ad_scripts(session, campaign.id)
        print(f"Number of ad scripts for campaign: {len(campaign_scripts)}")
        
        # Test ad script deletion
        print("\nTesting ad script deletion...")
        deleted = delete_ad_script(session, ad_script.id)
        print(f"Ad script deleted: {deleted}")
        
        # Test campaign deletion
        print("\nTesting campaign deletion...")
        deleted = delete_campaign(session, campaign.id)
        print(f"Campaign deleted: {deleted}")
        
        # Test user deletion
        print("\nTesting user deletion...")
        deleted = delete_user(session, user.id)
        print(f"User deleted: {deleted}")
        
        print("\nAll database operations tested successfully!")
        
    except Exception as e:
        print(f"Error during testing: {str(e)}")
        raise
    finally:
        session.close()
        engine.dispose()
        
        # Clean up test database
        if os.path.exists("test_adsynth.db"):
            try:
                os.remove("test_adsynth.db")
                print("\nTest database cleaned up.")
            except PermissionError:
                print("\nCould not remove test database - file is in use.")

if __name__ == "__main__":
    main()