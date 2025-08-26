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
        title="Seleccionar archivo Excel con datos de enfermedades",
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
    """Valida que el Excel tenga las columnas requeridas"""
    required_columns = ['Tabla', 'Codigo', 'Nombre', 'Descripcion']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        print(f"Error: Faltan las siguientes columnas en el archivo Excel: {missing_columns}")
        print(f"Columnas encontradas: {list(df.columns)}")
        return False
    
    return True


def process_excel_data(file_path: str) -> List[Dict[str, str]]:
    """Procesa el archivo Excel y retorna una lista de enfermedades"""
    try:
        # Leer el archivo Excel
        df = pd.read_excel(file_path)
        print(f"Archivo cargado exitosamente. Filas encontradas: {len(df)}")
        
        # Validar estructura
        if not validate_excel_structure(df):
            return []
        
        # Procesar datos
        diseases = []
        for index, row in df.iterrows():
            tabla = normalize_text(row.get('Tabla'))
            codigo = normalize_text(row.get('Codigo'))
            nombre = normalize_text(row.get('Nombre'))
            descripcion = normalize_text(row.get('Descripcion'))
            
            # Validar datos requeridos
            if not codigo or not nombre:
                print(f"Fila {index + 1}: Saltada - código o nombre vacío")
                continue
            
            disease = {
                'tabla': tabla,
                'codigo': codigo,
                'nombre': nombre,
                'descripcion': descripcion
            }
            diseases.append(disease)
        
        print(f"Procesadas {len(diseases)} enfermedades válidas de {len(df)} filas totales")
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


async def import_diseases(diseases: List[Dict[str, str]], dry_run: bool) -> Tuple[int, int]:
    """Importa las enfermedades a la base de datos"""
    created = 0
    skipped = 0
    
    # Eliminar duplicados
    unique_diseases = dedupe_diseases(diseases)
    print(f"Importando {len(unique_diseases)} enfermedades únicas...")
    
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
                    isActive=True
                )
                await repo.create(payload)
                print(f"[OK] Enfermedad creada: {codigo} - {disease['nombre']}")
                created += 1
            except Exception as e:
                print(f"[SKIP] {codigo} - {disease['nombre']} -> {e}")
                skipped += 1
        return created, skipped
    finally:
        await close_mongo_connection()


def main():
    parser = argparse.ArgumentParser(description="Importar enfermedades desde archivo Excel")
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
    
    print(f"Procesando archivo: {file_path}")
    
    # Procesar datos del Excel
    diseases = process_excel_data(file_path)
    if not diseases:
        print("No se pudieron procesar datos del archivo Excel.")
        return
    
    # Importar enfermedades
    created, skipped = asyncio.run(import_diseases(diseases, dry_run=args.dry_run))
    print(f"Completado. Creadas: {created}, Saltadas: {skipped}")


if __name__ == "__main__":
    main()
