#!/usr/bin/env python3
"""
Script para insertar administradores del sistema

Este script crea usuarios administradores en la base de datos con las credenciales especificadas.
Los administradores tienen acceso completo al sistema.

Uso:
    python3 scripts/import_administrators.py [--dry-run]

Argumentos:
    --dry-run: Solo mostrar qué se haría sin ejecutar cambios reales
"""

import asyncio
import argparse
import sys
import os
from datetime import datetime

# Agregar el directorio raíz del proyecto al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config.database import get_database
from app.shared.services.user_management import UserManagementService
from app.modules.auth.schemas.administrator import AdministratorCreate


# Datos de los administradores
ADMINISTRATORS = [
    {
        "nombre": "Juan Pablo Restrepo",
        "email": "juan.restrepo183@udea.edu.co",
        "password": "Nomerobe-12345"
    },
    {
        "nombre": "Juliana Duque",
        "email": "juliana.duqueg@udea.edu.co", 
        "password": "juliana.duque2025"
    },
    {
        "nombre": "Administrador del Sistema",
        "email": "admin@lime.edu.co",
        "password": "admin123"
    }
]


async def create_administrators(dry_run: bool = False):
    """Crear administradores en la base de datos"""
    try:
        # Obtener conexión a la base de datos
        db = await get_database()
        user_service = UserManagementService(db)
        
        created = 0
        skipped = 0
        errors = 0
        
        print(f"{'='*60}")
        print("IMPORTACIÓN DE ADMINISTRADORES")
        print(f"{'='*60}")
        print(f"Modo: {'DRY-RUN (sin cambios)' if dry_run else 'EJECUCIÓN REAL'}")
        print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Total administradores a procesar: {len(ADMINISTRATORS)}")
        print(f"{'='*60}")
        
        for i, admin_data in enumerate(ADMINISTRATORS, 1):
            nombre = admin_data["nombre"]
            email = admin_data["email"]
            password = admin_data["password"]
            
            print(f"\n[{i}/{len(ADMINISTRATORS)}] Procesando: {nombre}")
            print(f"  Email: {email}")
            print(f"  Rol: administrador")
            
            try:
                # Validaciones previas
                if not nombre or not nombre.strip():
                    print(f"  [SKIP] Nombre vacío o inválido")
                    skipped += 1
                    continue
                
                if not email or not email.strip():
                    print(f"  [SKIP] Email vacío o inválido")
                    skipped += 1
                    continue
                
                if not password or len(password) < 6:
                    print(f"  [SKIP] Contraseña debe tener al menos 6 caracteres")
                    skipped += 1
                    continue
                
                # Validar datos usando el esquema de administrador
                admin_schema = AdministratorCreate(
                    nombre=nombre,
                    email=email,
                    password=password,
                    is_active=True
                )
                
                # Verificar si el usuario ya existe
                existing_user = await user_service.check_email_exists_in_users(email)
                
                if existing_user:
                    print(f"  [SKIP] El usuario ya existe en la base de datos")
                    skipped += 1
                    continue
                
                if dry_run:
                    print(f"  [DRY-RUN] Se crearía el administrador: {nombre}")
                    print(f"    - Email: {email}")
                    print(f"    - Rol: administrador")
                    print(f"    - Estado: activo")
                    print(f"    - Validación: ✅ Datos válidos")
                    created += 1
                else:
                    # Crear el administrador
                    user = await user_service.create_user_for_administrator(
                        name=admin_schema.nombre,
                        email=admin_schema.email,
                        password=admin_schema.password,
                        is_active=admin_schema.is_active
                    )
                    
                    if user:
                        print(f"  [OK] Administrador creado exitosamente")
                        print(f"    - ID: {user.get('id', 'N/A')}")
                        print(f"    - Email: {user.get('email', 'N/A')}")
                        print(f"    - Rol: {user.get('rol', 'N/A')}")
                        print(f"    - Estado: {'Activo' if user.get('is_active') else 'Inactivo'}")
                        created += 1
                    else:
                        print(f"  [ERROR] No se pudo crear el administrador")
                        errors += 1
                        
            except ValueError as e:
                print(f"  [SKIP] Error de validación: {str(e)}")
                skipped += 1
            except Exception as e:
                print(f"  [ERROR] Error inesperado: {str(e)}")
                errors += 1
        
        # Resumen final
        print(f"\n{'='*60}")
        print("RESUMEN DE IMPORTACIÓN")
        print(f"{'='*60}")
        print(f"Total procesados: {len(ADMINISTRATORS)}")
        print(f"Creados: {created}")
        print(f"Saltados: {skipped}")
        print(f"Errores: {errors}")
        
        if dry_run:
            print(f"\n⚠️  MODO DRY-RUN: No se realizaron cambios en la base de datos")
            print(f"Para ejecutar realmente, ejecuta el script sin --dry-run")
        else:
            print(f"\n✅ Importación completada")
            
        print(f"{'='*60}")
        
    except Exception as e:
        print(f"❌ Error fatal: {str(e)}")
        sys.exit(1)


def main():
    """Función principal"""
    parser = argparse.ArgumentParser(
        description="Importar administradores del sistema",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python3 scripts/import_administrators.py --dry-run    # Solo mostrar qué se haría
  python3 scripts/import_administrators.py              # Ejecutar realmente
        """
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Solo mostrar qué se haría sin ejecutar cambios reales"
    )
    
    args = parser.parse_args()
    
    # Ejecutar la importación
    asyncio.run(create_administrators(dry_run=args.dry_run))


if __name__ == "__main__":
    main()
