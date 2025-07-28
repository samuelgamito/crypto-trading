#!/usr/bin/env python3
"""
Test script for MongoDB authentication
"""

import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from src.utils.mongo_service import MongoService

def test_mongo_connection():
    """Test MongoDB connection with authentication"""
    print("🧪 Testing MongoDB Authentication")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Get MongoDB configuration
    connection_string = os.getenv('MONGO_CONNECTION_STRING', 'mongodb://localhost:27017/')
    database_name = os.getenv('MONGO_DATABASE', 'crypto_trading')
    username = os.getenv('MONGO_USERNAME')
    password = os.getenv('MONGO_PASSWORD')
    enable_logging = os.getenv('ENABLE_MONGO_LOGGING', 'true').lower() == 'true'
    
    print(f"📊 MongoDB Configuration:")
    print(f"   Connection String: {connection_string}")
    print(f"   Database: {database_name}")
    print(f"   Username: {username if username else 'None (no auth)'}")
    print(f"   Password: {'*' * len(password) if password else 'None (no auth)'}")
    print(f"   Enable Logging: {enable_logging}")
    print()
    
    if not enable_logging:
        print("⚠️  MongoDB logging is disabled in environment")
        return
    
    try:
        # Initialize MongoDB service
        print("🔌 Initializing MongoDB service...")
        mongo_service = MongoService(
            connection_string=connection_string,
            database_name=database_name,
            username=username,
            password=password
        )
        
        # Test connection
        if mongo_service.is_connected():
            print("✅ MongoDB connection successful!")
            
            # Test storing a sample signal
            print("📝 Testing signal storage...")
            sample_signal = {
                "test": True,
                "message": "Authentication test signal",
                "timestamp": "2025-07-27T19:47:53.496Z"
            }
            
            success = mongo_service.store_trading_signal(sample_signal)
            if success:
                print("✅ Signal storage test successful!")
            else:
                print("❌ Signal storage test failed!")
            
            # Test retrieving signals
            print("📖 Testing signal retrieval...")
            signals = mongo_service.get_recent_signals(limit=5)
            print(f"✅ Retrieved {len(signals)} recent signals")
            
            # Close connection
            mongo_service.close_connection()
            print("🔌 MongoDB connection closed")
            
        else:
            print("❌ MongoDB connection failed!")
            print("   Check your connection string and credentials")
            
    except Exception as e:
        print(f"❌ Error testing MongoDB connection: {e}")
        print("   Make sure MongoDB is running and credentials are correct")

if __name__ == "__main__":
    test_mongo_connection() 