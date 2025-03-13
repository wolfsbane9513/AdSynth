"""Supabase configuration and client setup."""

import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get Supabase credentials
supabase_url = os.getenv("SUPABASE_URL")
supabase_anon_key = os.getenv("SUPABASE_ANON_KEY")

# Debug logging
print("Supabase URL:", supabase_url)
print("Anon Key exists:", bool(supabase_anon_key))

# Validate credentials
if not supabase_url:
    raise ValueError("SUPABASE_URL is not set in environment variables")
if not supabase_anon_key:
    raise ValueError("SUPABASE_ANON_KEY is not set in environment variables")

# Initialize Supabase client
try:
    supabase: Client = create_client(supabase_url, supabase_anon_key)
    print("Supabase client initialized successfully")
except Exception as e:
    print(f"Error initializing Supabase client: {str(e)}")
    raise

def get_supabase_client() -> Client:
    """Get the Supabase client instance.
    
    Returns:
        Client: Supabase client instance
    """
    return supabase 

def get_supabase_admin_client() -> Client:
    """Get the Supabase admin client instance.
    
    Returns:
        Client: Supabase admin client instance with service role privileges
    """
    return supabase_admin