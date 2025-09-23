import os
import sys
from pathlib import Path
import asyncio
import argparse
import pandas as pd
from typing import Optional, Tuple, List, Dict
import tkinter as tk
from tkinter import filedialog, messagebox

# Asegurar que el paquete 'app' sea importable al ejecutar el script directamente
CURRENT_DIR = Path(__file__).resolve().parent
BACKEND_ROOT = CURRENT_DIR.parent
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.config.database import connect_to_mongo, close_mongo_connection
from app.modules.enfermedades.repositories.enfermedad_repository import EnfermedadRepository
from app.modules.enfermedades.models.enfermedad import EnfermedadCreate


def normalize_text(text: str) -> str:
    """Normaliza el texto eliminando espacios extra y caracteres especiales"""
    if text is None or pd.isna(text):
        return None
    return " ".join(str(text).split()).strip()


def select_excel_file() -> Optional[str]:
    """Abre un diálogo para seleccionar el archivo Excel"""
    root = tk.Tk()
    root.withdraw()  # Ocultar la ventana principal
    
    file_path = filedialog.askopenfilename(
        title="Seleccionar archivo Excel con datos de cáncer (CIEO)",
        filetypes=[
            ("Excel files", "*.xlsx *.xls"),
            ("All files", "*.*")
        ]
    )
    
    if not file_path:
        print("No se seleccionó ningún archivo.")
        return None
    
    return file_path


def validate_excel_structure(df: pd.DataFrame) -> bool:
    """Valida que el Excel tenga las columnas requeridas para cáncer"""
    # Para cáncer, esperamos columnas con códigos C y descripciones
    # El archivo puede tener diferentes estructuras, así que validamos flexibilidad
    print(f"Columnas encontradas en el archivo: {list(df.columns)}")
    
    # Buscar columnas que contengan códigos (que empiecen con C)
    code_columns = [col for col in df.columns if any(str(df[col].iloc[i]).startswith('C') for i in range(min(5, len(df))) if pd.notna(df[col].iloc[i]))]
    
    if not code_columns:
        print("Error: No se encontraron columnas con códigos de cáncer (que empiecen con C)")
        return False
    
    print(f"Columnas de códigos encontradas: {code_columns}")
    
    # Buscar columnas con descripciones (texto largo)
    desc_columns = [col for col in df.columns if df[col].dtype == 'object' and col not in code_columns]
    
    if not desc_columns:
        print("Error: No se encontraron columnas con descripciones")
        return False
    
    print(f"Columnas de descripciones encontradas: {desc_columns}")
    
    return True


def process_excel_data(file_path: str) -> List[Dict[str, str]]:
    """Procesa el archivo Excel y retorna una lista de enfermedades de cáncer"""
    try:
        # Leer el archivo Excel
        df = pd.read_excel(file_path)
        print(f"Archivo cargado exitosamente. Filas encontradas: {len(df)}")
        
        # Validar estructura
        if not validate_excel_structure(df):
            return []
        
        # Buscar columnas automáticamente
        code_columns = [col for col in df.columns if any(str(df[col].iloc[i]).startswith('C') for i in range(min(5, len(df))) if pd.notna(df[col].iloc[i]))]
        desc_columns = [col for col in df.columns if df[col].dtype == 'object' and col not in code_columns]
        
        # Usar la primera columna de códigos y la primera de descripciones
        code_column = code_columns[0] if code_columns else None
        desc_column = desc_columns[0] if desc_columns else None
        
        print(f"Usando columna de códigos: {code_column}")
        print(f"Usando columna de descripciones: {desc_column}")
        
        # Procesar datos
        diseases = []
        for index, row in df.iterrows():
            codigo = normalize_text(row.get(code_column))
            descripcion = normalize_text(row.get(desc_column))
            
            # Validar datos requeridos
            if not codigo or not descripcion:
                print(f"Fila {index + 1}: Saltada - código o descripción vacío")
                continue
            
            # Verificar que el código empiece con C (código de cáncer)
            if not str(codigo).startswith('C'):
                print(f"Fila {index + 1}: Saltada - código '{codigo}' no empieza con C")
                continue
            
            # Extraer nombre de la descripción (primeras palabras)
            nombre = descripcion[:100] if len(descripcion) > 100 else descripcion
            
            disease = {
                'tabla': 'CIEO',  # Clasificación Internacional de Enfermedades para Oncología
                'codigo': codigo,
                'nombre': nombre,
                'descripcion': descripcion
            }
            diseases.append(disease)
        
        print(f"Procesadas {len(diseases)} enfermedades de cáncer válidas de {len(df)} filas totales")
        return diseases
        
    except Exception as e:
        print(f"Error al procesar el archivo Excel: {e}")
        return []


def dedupe_diseases(diseases: List[Dict[str, str]]) -> Dict[str, Dict[str, str]]:
    """Elimina duplicados basándose en el código"""
    merged: Dict[str, Dict[str, str]] = {}
    for disease in diseases:
        codigo = disease.get('codigo', '')
        if codigo:
            merged[codigo] = disease
    return merged


async def import_cancer_diseases(diseases: List[Dict[str, str]], dry_run: bool) -> Tuple[int, int]:
    """Importa las enfermedades de cáncer a la base de datos"""
    created = 0
    skipped = 0
    
    # Eliminar duplicados
    unique_diseases = dedupe_diseases(diseases)
    print(f"Importando {len(unique_diseases)} enfermedades de cáncer únicas...")
    
    if dry_run:
        for codigo, disease in unique_diseases.items():
            print(f"[DRY-RUN] {codigo} -> nombre='{disease['nombre']}', descripcion='{disease['descripcion']}'")
            created += 1
        return created, skipped
    
    db = await connect_to_mongo()
    try:
        repo = EnfermedadRepository(db)
        for codigo, disease in unique_diseases.items():
            try:
                payload = EnfermedadCreate(
                    tabla=disease['tabla'],
                    codigo=disease['codigo'],
                    nombre=disease['nombre'],
                    descripcion=disease['descripcion'],
                    is_active=True
                )
                await repo.create(payload)
                print(f"[OK] Enfermedad de cáncer creada: {codigo} - {disease['nombre']}")
                created += 1
            except Exception as e:
                print(f"[SKIP] {codigo} - {disease['nombre']} -> {e}")
                skipped += 1
        return created, skipped
    finally:
        await close_mongo_connection()


def main():
    parser = argparse.ArgumentParser(description="Importar enfermedades de cáncer (CIEO) desde archivo Excel")
    parser.add_argument("--file", help="Ruta al archivo Excel (opcional, si no se proporciona se abrirá un diálogo)")
    parser.add_argument("--dry-run", action="store_true", help="No escribir a la BD, solo previsualizar")
    args = parser.parse_args()
    
    # Obtener ruta del archivo
    file_path = args.file
    if not file_path:
        file_path = select_excel_file()
        if not file_path:
            print("No se seleccionó ningún archivo. Saliendo...")
            return
    
    # Verificar que el archivo existe
    if not os.path.exists(file_path):
        print(f"Error: El archivo {file_path} no existe.")
        return
    
    print(f"Procesando archivo de cáncer: {file_path}")
    
    # Procesar datos del Excel
    diseases = process_excel_data(file_path)
    if not diseases:
        print("No se pudieron procesar datos del archivo Excel.")
        return
    
    # Importar enfermedades de cáncer
    created, skipped = asyncio.run(import_cancer_diseases(diseases, dry_run=args.dry_run))
    print(f"Completado. Enfermedades de cáncer creadas: {created}, Saltadas: {skipped}")


if __name__ == "__main__":
    main()
