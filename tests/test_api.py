"""Test suite for AI Ad Generator API endpoints.
Tests user authentication, campaign management, and ad script operations.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.api.main import app
from src.database.models import Base
from src.api.dependencies import get_db

# Create test database
TEST_SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    TEST_SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override dependency
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def client():
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as test_client:
        yield test_client
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def test_user():
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123"
    }

@pytest.fixture
def test_campaign():
    return {
        "product_name": "Test Product",
        "product_description": "A test product description",
        "niche": "Technology",
        "target_audience": "Tech enthusiasts",
        "key_use_cases": "Testing and development",
        "campaign_goal": "Increase awareness"
    }

@pytest.fixture
def test_ad_script():
    return {
        "campaign_id": 1,
        "provider": "groq",
        "model": "llama-3.3-70b-versatile"
    }

@pytest.fixture
def test_ad_script_llama():
    return {
        "campaign_id": 1,
        "provider": "groq",
        "model": "llama-3.3-70b-versatile"
    }

@pytest.fixture
def test_ad_script_deepseek():
    return {
        "campaign_id": 1,
        "provider": "groq",
        "model": "deepseek-r1-distill-llama-70b"
    }

@pytest.fixture
def authenticated_client(client, test_user):
    # Register user
    client.post("/api/register", json=test_user)
    # Login
    response = client.post(
        "/api/token",
        data={
            "username": test_user["username"],
            "password": test_user["password"]
        }
    )
    token = response.json()["access_token"]
    client.headers = {"Authorization": f"Bearer {token}"}
    return client

def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_register_user(client, test_user):
    """Test user registration."""
    response = client.post("/api/register", json=test_user)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == test_user["username"]
    assert data["email"] == test_user["email"]
    assert "id" in data

def test_login(client, test_user):
    """Test user login and token generation."""
    # Register user first
    client.post("/api/register", json=test_user)
    # Attempt login
    response = client.post(
        "/api/token",
        data={
            "username": test_user["username"],
            "password": test_user["password"]
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_create_campaign(authenticated_client, test_campaign):
    """Test campaign creation."""
    response = authenticated_client.post("/api/campaigns/", json=test_campaign)
    assert response.status_code == 200
    data = response.json()
    assert data["product_name"] == test_campaign["product_name"]
    assert "id" in data

def test_get_campaign(authenticated_client, test_campaign):
    """Test getting campaign details."""
    # Create campaign first
    create_response = authenticated_client.post("/api/campaigns/", json=test_campaign)
    campaign_id = create_response.json()["id"]
    
    # Get campaign details
    response = authenticated_client.get(f"/api/campaigns/{campaign_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["product_name"] == test_campaign["product_name"]

def test_update_campaign(authenticated_client, test_campaign):
    """Test updating campaign details."""
    # Create campaign first
    create_response = authenticated_client.post("/api/campaigns/", json=test_campaign)
    campaign_id = create_response.json()["id"]
    
    # Update campaign
    updated_data = test_campaign.copy()
    updated_data["product_name"] = "Updated Product"
    response = authenticated_client.put(f"/api/campaigns/{campaign_id}", json=updated_data)
    assert response.status_code == 200
    data = response.json()
    assert data["product_name"] == "Updated Product"

def test_delete_campaign(authenticated_client, test_campaign):
    """Test deleting a campaign."""
    # Create campaign first
    create_response = authenticated_client.post("/api/campaigns/", json=test_campaign)
    campaign_id = create_response.json()["id"]
    
    # Delete campaign
    response = authenticated_client.delete(f"/api/campaigns/{campaign_id}")
    assert response.status_code == 204
    
    # Verify campaign is deleted
    get_response = authenticated_client.get(f"/api/campaigns/{campaign_id}")
    assert get_response.status_code == 404

def test_generate_ad_script_groq(authenticated_client, test_campaign, test_ad_script):
    """Test ad script generation using Groq provider."""
    # Create campaign first
    create_response = authenticated_client.post("/api/campaigns/", json=test_campaign)
    campaign_id = create_response.json()["id"]
    
    # Generate ad script using Groq
    test_ad_script["campaign_id"] = campaign_id
    response = authenticated_client.post("/api/ad-scripts/generate", json=test_ad_script)
    assert response.status_code == 200
    data = response.json()
    assert data["campaign_id"] == campaign_id
    assert data["provider"] == "groq"
    assert data["model"] == "llama-3.3-70b-versatile"
    assert "content" in data

def test_generate_ad_script_groq_llama(authenticated_client, test_campaign, test_ad_script_llama):
    """Test ad script generation using Groq Llama model."""
    # Create campaign first
    create_response = authenticated_client.post("/api/campaigns/", json=test_campaign)
    campaign_id = create_response.json()["id"]
    
    # Generate ad script using Groq Llama
    test_ad_script_llama["campaign_id"] = campaign_id
    response = authenticated_client.post("/api/ad-scripts/generate", json=test_ad_script_llama)
    assert response.status_code == 200
    data = response.json()
    assert data["campaign_id"] == campaign_id
    assert data["provider"] == "groq"
    assert data["model"] == "llama-3.3-70b-versatile"
    assert "content" in data

def test_generate_ad_script_groq_deepseek(authenticated_client, test_campaign, test_ad_script_deepseek):
    """Test ad script generation using Groq Deepseek model."""
    # Create campaign first
    create_response = authenticated_client.post("/api/campaigns/", json=test_campaign)
    campaign_id = create_response.json()["id"]
    
    # Generate ad script using Groq Deepseek
    test_ad_script_deepseek["campaign_id"] = campaign_id
    response = authenticated_client.post("/api/ad-scripts/generate", json=test_ad_script_deepseek)
    assert response.status_code == 200
    data = response.json()
    assert data["campaign_id"] == campaign_id
    assert data["provider"] == "groq"
    assert data["model"] == "deepseek-r1-distill-llama-70b"
    assert "content" in data

def test_get_campaign_scripts(authenticated_client, test_campaign, test_ad_script):
    """Test getting all ad scripts for a campaign."""
    # Create campaign first
    create_response = authenticated_client.post("/api/campaigns/", json=test_campaign)
    campaign_id = create_response.json()["id"]
    
    # Generate ad script
    test_ad_script["campaign_id"] = campaign_id
    authenticated_client.post("/api/ad-scripts/generate", json=test_ad_script)
    
    # Get campaign scripts
    response = authenticated_client.get(f"/api/ad-scripts/campaign/{campaign_id}")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["campaign_id"] == campaign_id

def test_update_ad_script(authenticated_client, test_campaign, test_ad_script):
    """Test updating ad script content."""
    # Create campaign and generate ad script
    create_response = authenticated_client.post("/api/campaigns/", json=test_campaign)
    campaign_id = create_response.json()["id"]
    test_ad_script["campaign_id"] = campaign_id
    script_response = authenticated_client.post("/api/ad-scripts/generate", json=test_ad_script)
    script_id = script_response.json()["id"]
    
    # Update ad script
    new_content = "Updated ad script content"
    response = authenticated_client.put(f"/api/ad-scripts/{script_id}", json={"content": new_content})
    assert response.status_code == 200
    data = response.json()
    assert data["content"] == new_content

def test_delete_ad_script(authenticated_client, test_campaign, test_ad_script):
    """Test deleting an ad script."""
    # Create campaign and generate ad script
    create_response = authenticated_client.post("/api/campaigns/", json=test_campaign)
    campaign_id = create_response.json()["id"]
    test_ad_script["campaign_id"] = campaign_id
    script_response = authenticated_client.post("/api/ad-scripts/generate", json=test_ad_script)
    script_id = script_response.json()["id"]
    
    # Delete ad script
    response = authenticated_client.delete(f"/api/ad-scripts/{script_id}")
    assert response.status_code == 204
    
    # Verify script is deleted
    get_response = authenticated_client.get(f"/api/ad-scripts/campaign/{campaign_id}")
    assert get_response.status_code == 200
    data = get_response.json()
    assert len(data) == 0
