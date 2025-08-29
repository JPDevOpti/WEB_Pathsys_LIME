import os
import sys
from pathlib import Path
import asyncio
import argparse
from typing import Optional, Tuple, List, Dict

CURRENT_DIR = Path(__file__).resolve().parent
BACKEND_ROOT = CURRENT_DIR.parent
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.config.database import connect_to_mongo, close_mongo_connection
from app.shared.services.user_management import UserManagementService

ADMINS_DATA: List[Dict[str, str]] = [
    {
        "name": "Administrador LIME",
        "email": "admin@lime.edu.co",
        "password": "admin123"
    },
    {
        "name": "Juan Restrepo",
        "email": "juan.restrepo183@udea.edu.co",
        "password": "4123"
    },
    {
        "name": "Juliana Duque",
        "email": "juliana.duqueg@udea.edu.co",
        "password": "juliana.duqueg"
    }
]

async def import_admins(dry_run: bool) -> Tuple[int, int]:
    """Importa la lista de administradores. Retorna (creados, saltados)."""
    created = 0
    skipped = 0

    if dry_run:
        for admin in ADMINS_DATA:
            name = admin["name"]
            email = admin["email"]
            password = admin["password"]
            print(f"[DRY-RUN] {name} -> email={email} password={password}")
            created += 1
        return created, skipped

    db = await connect_to_mongo()
    try:
        user_service = UserManagementService(db)

        for admin in ADMINS_DATA:
            name = admin["name"]
            email = admin["email"]
            password = admin["password"]

            try:
                user_doc = await user_service._create_user_with_role(
                    name=name,
                    email=email,
                    password=password,
                    role="administrador",
                    is_active=True
                )
                
                if user_doc:
                    print(f"✅ Administrador creado: {name} ({email})")
                    created += 1
                else:
                    print(f"❌ Error al crear administrador: {name}")
                    skipped += 1
                    
            except ValueError as e:
                if "Ya existe un usuario" in str(e):
                    print(f"⚠️  Administrador ya existe: {name} ({email})")
                    skipped += 1
                else:
                    print(f"❌ Error al crear administrador {name}: {e}")
                    skipped += 1
            except Exception as e:
                print(f"❌ Error inesperado al crear administrador {name}: {e}")
                skipped += 1

    finally:
        await close_mongo_connection()

    return created, skipped

async def main():
    parser = argparse.ArgumentParser(description="Importar administradores al sistema")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ejecutar sin hacer cambios en la base de datos"
    )
    
    args = parser.parse_args()
    
    print("🚀 Iniciando importación de administradores...")
    if args.dry_run:
        print("🔍 Modo DRY-RUN: No se harán cambios en la base de datos")
    
    created, skipped = await import_admins(args.dry_run)
    
    print(f"\n📊 Resumen:")
    print(f"   ✅ Administradores creados: {created}")
    print(f"   ⚠️  Administradores saltados: {skipped}")
    print(f"   📝 Total procesados: {created + skipped}")

if __name__ == "__main__":
    asyncio.run(main())
