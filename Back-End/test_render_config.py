#!/usr/bin/env python3
"""
Render Deployment MongoDB Test
Specifically tests the MongoDB configuration that will be used in Render
"""

import asyncio
import os
import sys
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

async def test_render_config():
    """Test MongoDB connection using Render configuration"""
    
    print("🚀 Testing Render Deployment Configuration")
    print("=" * 50)
    
    # Load render.env specifically
    if os.path.exists('render.env'):
        load_dotenv('render.env')
        print("✅ Loaded render.env configuration")
    else:
        print("❌ render.env file not found")
        return False
    
    # Get configuration
    mongodb_url = os.getenv('MONGODB_URL')
    database_name = os.getenv('DATABASE_NAME', 'lime_pathsys')
    environment = os.getenv('ENVIRONMENT')
    
    print(f"Environment: {environment}")
    print(f"Database: {database_name}")
    print(f"MongoDB URL: {mongodb_url[:50]}...")
    print()
    
    if not mongodb_url:
        print("❌ MONGODB_URL not found in render.env")
        return False
    
    # Test with the exact configuration used in database.py for production
    connection_options = {
        "serverSelectionTimeoutMS": 30000,
        "connectTimeoutMS": 30000,
        "socketTimeoutMS": 30000,
        "maxPoolSize": 10,
        "minPoolSize": 1,
        "maxIdleTimeMS": 45000,
        "waitQueueTimeoutMS": 30000,
        "retryWrites": True,
        "retryReads": True
    }
    
    print("🔍 Testing with production configuration...")
    print(f"Connection options: {list(connection_options.keys())}")
    print()
    
    client = None
    try:
        # Create client
        print("1. Creating MongoDB client...")
        client = AsyncIOMotorClient(mongodb_url, **connection_options)
        
        # Test ping
        print("2. Testing ping...")
        await client.admin.command('ping')
        print("   ✅ Ping successful")
        
        # Test database access
        print("3. Testing database access...")
        db = client[database_name]
        collections = await db.list_collection_names()
        print(f"   ✅ Database access successful. Collections: {len(collections)}")
        
        # List collections
        if collections:
            print("   📋 Available collections:")
            for collection in collections:
                print(f"      - {collection}")
        
        # Test a simple query
        print("4. Testing simple query...")
        test_collection = db.get_collection(collections[0]) if collections else db.test
        doc_count = await test_collection.count_documents({})
        print(f"   ✅ Query successful. Documents in {test_collection.name}: {doc_count}")
        
        # Test connection with SSL parameters from URL
        print("5. Verifying SSL parameters in URL...")
        ssl_params = ['ssl=true', 'tlsAllowInvalidCertificates=true', 'tlsAllowInvalidHostnames=true']
        for param in ssl_params:
            if param in mongodb_url:
                print(f"   ✅ {param} found in URL")
            else:
                print(f"   ⚠️  {param} not found in URL")
        
        print("\n🎉 All Render configuration tests passed!")
        print("🚀 Configuration is ready for Render deployment!")
        return True
        
    except Exception as e:
        print(f"\n❌ Render configuration test failed: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        return False
        
    finally:
        if client:
            print("\n6. Closing connection...")
            client.close()
            print("   ✅ Connection closed")

async def main():
    """Run Render configuration test"""
    
    success = await test_render_config()
    
    print("\n" + "="*50)
    print("RENDER TEST SUMMARY")
    print("="*50)
    
    if success:
        print("✅ Render configuration test passed!")
        print("🚀 Ready for Render deployment!")
        print("\nNext steps:")
        print("1. Use the render.env file for environment variables in Render")
        print("2. Deploy to Render with confidence")
        print("3. Monitor logs for any connection issues")
        return True
    else:
        print("❌ Render configuration test failed.")
        print("❌ Fix configuration before deploying to Render.")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)