"""Database models for AI Ad Generator.
Defines SQLAlchemy models for storing campaigns and generated ad scripts.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, create_engine, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash

Base = declarative_base()

class User(Base):
    """Model for storing user information."""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(256), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship with Campaign
    campaigns = relationship('Campaign', back_populates='user')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Campaign(Base):
    """Model for storing campaign information."""
    __tablename__ = 'campaigns'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    product_name = Column(String(100), nullable=False)
    product_description = Column(Text, nullable=False)
    target_audience = Column(String(200), nullable=False)
    key_use_cases = Column(Text, nullable=False)
    campaign_goal = Column(String(200), nullable=False)
    niche = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship('User', back_populates='campaigns')
    ad_scripts = relationship('AdScript', back_populates='campaign')

class AdScript(Base):
    """Model for storing generated ad scripts."""
    __tablename__ = 'ad_scripts'
    
    id = Column(Integer, primary_key=True)
    campaign_id = Column(Integer, ForeignKey('campaigns.id'), nullable=False)
    content = Column(Text, nullable=False)
    provider = Column(String(50), nullable=False)  # openai, claude, or groq
    model = Column(String(100), nullable=False)    # specific model used
    platform = Column(String(50), nullable=True)   # general, instagram, youtube, etc.
    reddit_references = Column(Text)               # JSON string of referenced Reddit posts
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship with Campaign
    campaign = relationship('Campaign', back_populates='ad_scripts')

def init_db(database_url: str):
    """Initialize the database with all defined models.
    
    Args:
        database_url (str): SQLAlchemy database URL
    """
    engine = create_engine(database_url)
    Base.metadata.create_all(engine)