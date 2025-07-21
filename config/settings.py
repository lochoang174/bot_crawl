"""
Configuration settings for the bot detection bypass tool
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()



class Settings:
    """Application settings"""
    
    # MongoDB Configuration
    MONGODB_CONNECTION_STRING = os.getenv("MONGODB_CONNECTION_STRING", "mongodb://localhost:27017/")
    MONGODB_DATABASE_NAME = os.getenv("MONGODB_DATABASE_NAME", "crawl_bot_db")
    
    # MongoDB Collections
    MONGODB_COLLECTIONS = {
        "url": "url"
    }
   