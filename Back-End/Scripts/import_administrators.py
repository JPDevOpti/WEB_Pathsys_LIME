#!/usr/bin/env python3
"""
Script to insert system administrators

This script creates administrator users in the database with the specified credentials.
Administrators have full access to the system.

Usage:
    python3 Scripts/import_administrators_en.py [--dry-run]

Arguments:
    --dry-run: Only show what would be done without executing real changes
"""

import asyncio
import argparse
import sys
import os
from datetime import datetime

# Add project root directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config.database import get_database
from app.shared.services.user_management import UserManagementService
from app.modules.auth.schemas.administrator import AdministratorCreate


# Administrator data
ADMINISTRATORS = [
    {
        "name": "Juan Pablo Restrepo",
        "email": "juan.restrepo183@udea.edu.co",
        "password": "Nomerobe-12345"
    },
    {
        "name": "Juliana Duque",
        "email": "juliana.duqueg@udea.edu.co", 
        "password": "juliana.duque2025"
    },
    {
        "name": "System Administrator",
        "email": "admin@lime.edu.co",
        "password": "admin123"
    }
]


async def create_administrators(dry_run: bool = False):
    """Create administrators in the database"""
    try:
        # Get database connection
        db = await get_database()
        user_service = UserManagementService(db)
        
        created = 0
        skipped = 0
        errors = 0
        
        print(f"{'='*60}")
        print("ADMINISTRATOR IMPORT")
        print(f"{'='*60}")
        print(f"Mode: {'DRY-RUN (no changes)' if dry_run else 'REAL EXECUTION'}")
        print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Total administrators to process: {len(ADMINISTRATORS)}")
        print(f"{'='*60}")
        
        for i, admin_data in enumerate(ADMINISTRATORS, 1):
            name = admin_data["name"]
            email = admin_data["email"]
            password = admin_data["password"]
            
            print(f"\n[{i}/{len(ADMINISTRATORS)}] Processing: {name}")
            print(f"  Email: {email}")
            print(f"  Role: administrator")
            
            try:
                # Previous validations
                if not name or not name.strip():
                    print(f"  [SKIP] Empty or invalid name")
                    skipped += 1
                    continue
                
                if not email or not email.strip():
                    print(f"  [SKIP] Empty or invalid email")
                    skipped += 1
                    continue
                
                if not password or len(password) < 6:
                    print(f"  [SKIP] Password must have at least 6 characters")
                    skipped += 1
                    continue
                
                # Validate data using administrator schema
                admin_schema = AdministratorCreate(
                    name=name,
                    email=email,
                    password=password,
                    is_active=True
                )
                
                # Check if user already exists
                existing_user = await user_service.check_email_exists_in_users(email)
                
                if existing_user:
                    print(f"  [SKIP] User already exists in database")
                    skipped += 1
                    continue
                
                if dry_run:
                    print(f"  [DRY-RUN] Would create administrator: {name}")
                    print(f"    - Email: {email}")
                    print(f"    - Role: administrator")
                    print(f"    - Status: active")
                    print(f"    - Validation: ✅ Valid data")
                    created += 1
                else:
                    # Create administrator, using name as default administrative code
                    admin_code = admin_schema.name.replace(" ", "_").lower()[:20]
                    user = await user_service.create_user_for_administrator(
                        name=admin_schema.name,
                        email=admin_schema.email,
                        password=admin_schema.password,
                        is_active=admin_schema.is_active,
                        administrator_code=admin_code
                    )
                    
                    if user:
                        print(f"  [OK] Administrator created successfully")
                        print(f"    - ID: {user.get('id', 'N/A')}")
                        print(f"    - Email: {user.get('email', 'N/A')}")
                        print(f"    - Role: {user.get('role', 'N/A')}")
                        print(f"    - Status: {'Active' if user.get('is_active') else 'Inactive'}")
                        created += 1
                    else:
                        print(f"  [ERROR] Could not create administrator")
                        errors += 1
                        
            except ValueError as e:
                print(f"  [SKIP] Validation error: {str(e)}")
                skipped += 1
            except Exception as e:
                print(f"  [ERROR] Unexpected error: {str(e)}")
                errors += 1
        
        # Final summary
        print(f"\n{'='*60}")
        print("IMPORT SUMMARY")
        print(f"{'='*60}")
        print(f"Total processed: {len(ADMINISTRATORS)}")
        print(f"Created: {created}")
        print(f"Skipped: {skipped}")
        print(f"Errors: {errors}")
        
        if dry_run:
            print(f"\n⚠️  DRY-RUN MODE: No changes were made to the database")
            print(f"To execute for real, run the script without --dry-run")
        else:
            print(f"\n✅ Import completed")
            
        print(f"{'='*60}")
        
    except Exception as e:
        print(f"❌ Fatal error: {str(e)}")
        sys.exit(1)


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Import system administrators",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 Scripts/import_administrators_en.py --dry-run    # Only show what would be done
  python3 Scripts/import_administrators_en.py              # Execute for real
        """
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only show what would be done without executing real changes"
    )
    
    args = parser.parse_args()
    
    # Execute import
    asyncio.run(create_administrators(dry_run=args.dry_run))


if __name__ == "__main__":
    main()
