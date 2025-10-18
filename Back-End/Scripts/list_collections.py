#!/usr/bin/env python3
import sys
import os
import asyncio
from datetime import datetime

# Add project root directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config.database import connect_to_mongo, close_mongo_connection

async def main():
    print("="*60)
    print("MONGO COLLECTIONS INSPECT")
    print("="*60)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    try:
        db = await connect_to_mongo()
        names = await db.list_collection_names()
        names_sorted = sorted(names)
        print(f"Total collections: {len(names_sorted)}")
        for name in names_sorted:
            try:
                count = await db[name].count_documents({})
                print(f"- {name}: {count} docs")
            except Exception as e:
                print(f"- {name}: error counting -> {e}")
    except Exception as e:
        print(f"Error connecting or listing collections: {e}")
    finally:
        try:
            await close_mongo_connection()
        except Exception:
            pass

if __name__ == "__main__":
    asyncio.run(main())