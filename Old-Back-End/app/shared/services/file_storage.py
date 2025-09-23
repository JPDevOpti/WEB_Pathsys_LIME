import os
import uuid
import shutil
import logging
from pathlib import Path
from typing import Optional, List, BinaryIO
from datetime import datetime
from fastapi import UploadFile
from app.config.settings import settings
from app.core.exceptions import ValidationException

logger = logging.getLogger(__name__)

class FileStorageService:
    """Servicio para manejo de archivos"""
    
    def __init__(self):
        self.upload_dir = Path(settings.UPLOAD_DIR)
        self.max_file_size = settings.MAX_FILE_SIZE
        self.allowed_extensions = {
            'images': {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'},
            'documents': {'.pdf', '.doc', '.docx', '.txt', '.rtf'},
            'spreadsheets': {'.xls', '.xlsx', '.csv'},
            'archives': {'.zip', '.rar', '.7z', '.tar', '.gz'},
            'medical': {'.dcm', '.dicom'}  # Archivos médicos
        }
        
        # Crear directorio de uploads si no existe
        self.upload_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_file_category(self, extension: str) -> str:
        """Obtener categoría del archivo basada en su extensión"""
        extension = extension.lower()
        for category, extensions in self.allowed_extensions.items():
            if extension in extensions:
                return category
        return 'other'
    
    def _validate_file(self, file: UploadFile) -> None:
        """Validar archivo antes de guardarlo"""
        # Validar tamaño
        if hasattr(file, 'size') and file.size and file.size > self.max_file_size:
            raise ValidationException(
                f"El archivo excede el tamaño máximo permitido ({self.max_file_size} bytes)"
            )
        
        # Validar extensión
        if file.filename:
            extension = Path(file.filename).suffix.lower()
            all_extensions = set()
            for exts in self.allowed_extensions.values():
                all_extensions.update(exts)
            
            if extension not in all_extensions:
                raise ValidationException(
                    f"Tipo de archivo no permitido: {extension}"
                )
    
    async def save_file(
        self,
        file: UploadFile,
        subfolder: str = "general",
        custom_name: Optional[str] = None
    ) -> dict:
        """Guardar archivo en el sistema"""
        try:
            # Validar archivo
            self._validate_file(file)
            
            # Generar nombre único si no se proporciona uno personalizado
            if custom_name:
                filename = custom_name
            else:
                file_extension = Path(file.filename).suffix if file.filename else ''
                unique_id = str(uuid.uuid4())
                filename = f"{unique_id}{file_extension}"
            
            # Crear directorio de destino
            category = self._get_file_category(Path(filename).suffix)
            dest_dir = self.upload_dir / subfolder / category
            dest_dir.mkdir(parents=True, exist_ok=True)
            
            # Ruta completa del archivo
            file_path = dest_dir / filename
            
            # Guardar archivo
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            
            # Información del archivo guardado
            file_info = {
                'filename': filename,
                'original_filename': file.filename,
                'path': str(file_path),
                'relative_path': str(file_path.relative_to(self.upload_dir)),
                'size': len(content),
                'content_type': file.content_type,
                'category': category,
                'subfolder': subfolder,
                'upload_date': datetime.utcnow().isoformat()
            }
            
            logger.info(f"Archivo guardado: {filename} en {file_path}")
            return file_info
            
        except Exception as e:
            logger.error(f"Error al guardar archivo: {str(e)}")
            raise ValidationException(f"Error al guardar archivo: {str(e)}")
    
    def delete_file(self, file_path: str) -> bool:
        """Eliminar archivo del sistema"""
        try:
            full_path = Path(file_path)
            if not full_path.is_absolute():
                full_path = self.upload_dir / file_path
            
            if full_path.exists():
                full_path.unlink()
                logger.info(f"Archivo eliminado: {full_path}")
                return True
            else:
                logger.warning(f"Archivo no encontrado para eliminar: {full_path}")
                return False
                
        except Exception as e:
            logger.error(f"Error al eliminar archivo: {str(e)}")
            return False
    
    def get_file_info(self, file_path: str) -> Optional[dict]:
        """Obtener información de un archivo"""
        try:
            full_path = Path(file_path)
            if not full_path.is_absolute():
                full_path = self.upload_dir / file_path
            
            if not full_path.exists():
                return None
            
            stat = full_path.stat()
            return {
                'filename': full_path.name,
                'path': str(full_path),
                'size': stat.st_size,
                'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'extension': full_path.suffix,
                'category': self._get_file_category(full_path.suffix)
            }
            
        except Exception as e:
            logger.error(f"Error al obtener información del archivo: {str(e)}")
            return None
    
    def list_files(self, subfolder: str = "", category: Optional[str] = None) -> List[dict]:
        """Listar archivos en un directorio"""
        try:
            search_dir = self.upload_dir
            if subfolder:
                search_dir = search_dir / subfolder
            
            if category:
                search_dir = search_dir / category
            
            if not search_dir.exists():
                return []
            
            files = []
            for file_path in search_dir.rglob('*'):
                if file_path.is_file():
                    file_info = self.get_file_info(str(file_path))
                    if file_info:
                        files.append(file_info)
            
            return files
            
        except Exception as e:
            logger.error(f"Error al listar archivos: {str(e)}")
            return []
    
    def get_file_url(self, file_path: str) -> str:
        """Obtener URL para acceder al archivo"""
        # En un entorno de producción, esto podría ser una URL de CDN
        return f"/files/{file_path}"
    
    def cleanup_old_files(self, days: int = 30) -> int:
        """Limpiar archivos antiguos (para mantenimiento)"""
        try:
            count = 0
            cutoff_time = datetime.now().timestamp() - (days * 24 * 60 * 60)
            
            for file_path in self.upload_dir.rglob('*'):
                if file_path.is_file():
                    if file_path.stat().st_mtime < cutoff_time:
                        file_path.unlink()
                        count += 1
            
            logger.info(f"Limpieza completada: {count} archivos eliminados")
            return count
            
        except Exception as e:
            logger.error(f"Error en limpieza de archivos: {str(e)}")
            return 0
    
    def get_storage_stats(self) -> dict:
        """Obtener estadísticas de almacenamiento"""
        try:
            total_size = 0
            file_count = 0
            category_stats = {}
            
            for file_path in self.upload_dir.rglob('*'):
                if file_path.is_file():
                    size = file_path.stat().st_size
                    total_size += size
                    file_count += 1
                    
                    category = self._get_file_category(file_path.suffix)
                    if category not in category_stats:
                        category_stats[category] = {'count': 0, 'size': 0}
                    
                    category_stats[category]['count'] += 1
                    category_stats[category]['size'] += size
            
            return {
                'total_files': file_count,
                'total_size': total_size,
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'categories': category_stats,
                'upload_dir': str(self.upload_dir)
            }
            
        except Exception as e:
            logger.error(f"Error al obtener estadísticas: {str(e)}")
            return {}

# Instancia global del servicio
file_storage_service = FileStorageService()