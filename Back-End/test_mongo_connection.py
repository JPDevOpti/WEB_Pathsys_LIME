#!/usr/bin/env python3
"""
MongoDB Atlas Connection Test Script
Tests MongoDB connection with different configurations to verify SSL and connectivity
"""

import asyncio
import os
import sys
import time
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import certifi
import ssl

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

class MongoConnectionTester:
    def __init__(self):
        self.test_results = []
        
    def log_result(self, test_name: str, success: bool, message: str, duration: float = 0):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "message": message,
            "duration": f"{duration:.2f}s",
            "timestamp": datetime.now().strftime("%H:%M:%S")
        }
        self.test_results.append(result)
        print(f"[{result['timestamp']}] {status} {test_name}: {message} ({result['duration']})")
        
    async def test_basic_connection(self, mongodb_url: str, test_name: str):
        """Test basic MongoDB connection"""
        start_time = time.time()
        client = None
        
        try:
            client = AsyncIOMotorClient(mongodb_url)
            await client.admin.command('ping')
            duration = time.time() - start_time
            self.log_result(test_name, True, "Connection successful", duration)
            return True
            
        except Exception as e:
            duration = time.time() - start_time
            self.log_result(test_name, False, f"Connection failed: {str(e)}", duration)
            return False
            
        finally:
            if client:
                client.close()
                
    async def test_ssl_connection(self, mongodb_url: str, ssl_options: dict, test_name: str):
        """Test MongoDB connection with specific SSL options"""
        start_time = time.time()
        client = None
        
        try:
            client = AsyncIOMotorClient(mongodb_url, **ssl_options)
            await client.admin.command('ping')
            duration = time.time() - start_time
            self.log_result(test_name, True, f"SSL connection successful with options: {list(ssl_options.keys())}", duration)
            return True
            
        except Exception as e:
            duration = time.time() - start_time
            self.log_result(test_name, False, f"SSL connection failed: {str(e)}", duration)
            return False
            
        finally:
            if client:
                client.close()
                
    async def test_database_operations(self, mongodb_url: str, database_name: str, ssl_options: dict):
        """Test basic database operations"""
        start_time = time.time()
        client = None
        
        try:
            client = AsyncIOMotorClient(mongodb_url, **ssl_options)
            db = client[database_name]
            
            # Test collection listing
            collections = await db.list_collection_names()
            
            # Test a simple find operation
            test_collection = db.test_connection
            await test_collection.find_one()
            
            duration = time.time() - start_time
            self.log_result("Database Operations", True, f"Database operations successful. Collections found: {len(collections)}", duration)
            return True
            
        except Exception as e:
            duration = time.time() - start_time
            self.log_result("Database Operations", False, f"Database operations failed: {str(e)}", duration)
            return False
            
        finally:
            if client:
                client.close()
                
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*80)
        print("MONGODB CONNECTION TEST SUMMARY")
        print("="*80)
        
        passed = sum(1 for result in self.test_results if "PASS" in result["status"])
        failed = len(self.test_results) - passed
        
        print(f"Total Tests: {len(self.test_results)}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Success Rate: {(passed/len(self.test_results)*100):.1f}%")
        
        print("\nDETAILED RESULTS:")
        print("-" * 80)
        for result in self.test_results:
            print(f"{result['status']} {result['test']}")
            print(f"    Message: {result['message']}")
            print(f"    Duration: {result['duration']}")
            print()

async def main():
    print("MongoDB Atlas Connection Test Script")
    print("=" * 50)
    
    # Load environment variables
    env_files = ['.env', 'config.atlas.env', 'render.env']
    for env_file in env_files:
        if os.path.exists(env_file):
            load_dotenv(env_file)
            print(f"Loaded environment from: {env_file}")
    
    # Get configuration
    mongodb_url = os.getenv('MONGODB_URL')
    database_name = os.getenv('DATABASE_NAME', 'lime_pathsys')
    environment = os.getenv('ENVIRONMENT', 'development')
    
    if not mongodb_url:
        print("❌ ERROR: MONGODB_URL not found in environment variables")
        return
        
    print(f"Environment: {environment}")
    print(f"Database: {database_name}")
    print(f"MongoDB URL: {mongodb_url[:50]}...")
    print()
    
    tester = MongoConnectionTester()
    
    # Test 1: Basic connection without SSL options
    print("🔍 Testing basic connection...")
    await tester.test_basic_connection(mongodb_url, "Basic Connection")
    
    # Test 2: Connection with minimal SSL options
    print("\n🔍 Testing minimal SSL configuration...")
    minimal_ssl_options = {
        "serverSelectionTimeoutMS": 10000,
        "connectTimeoutMS": 10000,
        "socketTimeoutMS": 10000,
    }
    await tester.test_ssl_connection(mongodb_url, minimal_ssl_options, "Minimal SSL Config")
    
    # Test 3: Connection with production SSL options
    print("\n🔍 Testing production SSL configuration...")
    production_ssl_options = {
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
    await tester.test_ssl_connection(mongodb_url, production_ssl_options, "Production SSL Config")
    
    # Test 4: Connection with Render-specific options
    print("\n🔍 Testing Render-specific configuration...")
    render_ssl_options = {
        "serverSelectionTimeoutMS": 30000,
        "connectTimeoutMS": 30000,
        "socketTimeoutMS": 30000,
        "maxPoolSize": 5,
        "tls": True,
        "tlsAllowInvalidCertificates": True,
        "tlsAllowInvalidHostnames": True
    }
    await tester.test_ssl_connection(mongodb_url, render_ssl_options, "Render SSL Config")
    
    # Test 5: Database operations
    print("\n🔍 Testing database operations...")
    await tester.test_database_operations(mongodb_url, database_name, production_ssl_options)
    
    # Print summary
    tester.print_summary()
    
    # Return exit code based on results
    failed_tests = sum(1 for result in tester.test_results if "FAIL" in result["status"])
    if failed_tests > 0:
        print(f"\n❌ {failed_tests} test(s) failed. Check configuration.")
        sys.exit(1)
    else:
        print("\n✅ All tests passed! MongoDB connection is working correctly.")
        sys.exit(0)

if __name__ == "__main__":
    asyncio.run(main())