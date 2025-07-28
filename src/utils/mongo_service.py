"""
MongoDB service for storing trading signals
"""

import logging
from datetime import datetime
from operator import or_
from typing import Dict, List, Optional
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError


class MongoService:
    """Service for MongoDB operations"""
    
    def __init__(self, connection_string: str = None, database_name: str = "crypto_trading", 
                 username: str = None, password: str = None):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.database_name = database_name
        self.client = None
        self.db = None
        
        # Default to local MongoDB if no connection string provided
        if connection_string is None:
            connection_string = "mongodb://localhost:27017/"
        
        # Build connection string with authentication if credentials provided
        if username and password:
            # Parse the connection string to add authentication
            if connection_string.startswith("mongodb+srv://") or connection_string.startswith("mongodb://"):
                # Extract host and port from connection string
                if "@" in connection_string:
                    # Already has authentication, use as is
                    auth_connection_string = connection_string
                else:
                    # Add authentication to connection string
                    # mongodb://localhost:27017/ -> mongodb://username:password@localhost:27017/
                    conn_params = connection_string.split("://")
                    auth_connection_string = f"{conn_params[0]}://{username}:{password}@{conn_params[1]}"
            else:
                # Assume it's already a complete connection string
                auth_connection_string = connection_string
        else:
            auth_connection_string = connection_string
        
        try:
            self.client = MongoClient(auth_connection_string, serverSelectionTimeoutMS=5000)
            # Test connection
            self.client.admin.command('ping')
            self.db = self.client[database_name]
            self.logger.info(f"Connected to MongoDB: {database_name}")
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            self.logger.error(f"Failed to connect to MongoDB: {e}")
            self.client = None
            self.db = None
    
    def is_connected(self) -> bool:
        """Check if MongoDB connection is active"""
        return self.client is not None and self.db is not None
    
    def store_trading_signal(self, signal_data: Dict) -> bool:
        """Store a trading signal in MongoDB"""
        if not self.is_connected():
            self.logger.error("MongoDB not connected")
            return False
        
        try:
            # Add timestamp if not present
            if 'created_at' not in signal_data:
                signal_data['created_at'] = datetime.utcnow().isoformat() + 'Z'
            
            # Insert into signals collection
            result = self.db.signals.insert_one(signal_data)
            self.logger.info(f"Signal stored with ID: {result.inserted_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error storing signal: {e}")
            return False
    
    def get_recent_signals(self, limit: int = 100) -> List[Dict]:
        """Get recent trading signals"""
        if not self.is_connected():
            self.logger.error("MongoDB not connected")
            return []
        
        try:
            cursor = self.db.signals.find().sort('created_at', -1).limit(limit)
            return list(cursor)
        except Exception as e:
            self.logger.error(f"Error retrieving signals: {e}")
            return []
    
    def get_signals_by_decision(self, decision: str, limit: int = 50) -> List[Dict]:
        """Get signals filtered by decision type"""
        if not self.is_connected():
            self.logger.error("MongoDB not connected")
            return []
        
        try:
            cursor = self.db.signals.find({'decision': decision}).sort('created_at', -1).limit(limit)
            return list(cursor)
        except Exception as e:
            self.logger.error(f"Error retrieving signals by decision: {e}")
            return []
    
    def close_connection(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            self.logger.info("MongoDB connection closed") 