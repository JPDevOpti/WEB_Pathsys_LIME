#!/usr/bin/env python3
"""
Quick MongoDB Connection Test
Simple script to quickly test MongoDB Atlas connection
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

async def quick_test():
    # Load environment
    load_dotenv('.env')
    load_dotenv('config.atlas.env')
    load_dotenv('render.env')
    
    mongodb_url = os.getenv('MONGODB_URL')
    database_name = os.getenv('DATABASE_NAME', 'lime_pathsys')
    
    if not mongodb_url:
        print("❌ MONGODB_URL not found")
        return False
    
    print(f"Testing connection to: {database_name}")
    print(f"URL: {mongodb_url[:50]}...")
    
    try:
        # Simple connection test
        client = AsyncIOMotorClient(mongodb_url)
        
        # Test ping
        await client.admin.command('ping')
        print("✅ Ping successful")
        
        # Test database access
        db = client[database_name]
        collections = await db.list_collection_names()
        print(f"✅ Database access successful. Collections: {len(collections)}")
        
        # Close connection
        client.close()
        print("✅ Connection closed successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = asyncio.run(quick_test())
    exit(0 if success else 1)