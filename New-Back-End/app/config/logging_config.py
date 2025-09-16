import logging
import logging.config
import sys
from typing import Dict, Any
import os
from app.config.settings import settings

def setup_logging() -> None:
    """Configurar logging estructurado para la aplicación"""
    
    # Configuración base - Logging desactivado
    log_config: Dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json": {
                "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
                "format": "%(asctime)s %(name)s %(levelname)s %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            },
            "simple": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "ERROR",  # Solo errores críticos
                "formatter": "simple",
                "stream": sys.stdout
            }
        },
        "loggers": {
            "": {  # Root logger
                "handlers": ["console"],
                "level": "ERROR",
                "propagate": False
            },
            "app": {
                "handlers": ["console"],
                "level": "ERROR",
                "propagate": False
            },
            "uvicorn": {
                "handlers": ["console"],
                "level": "ERROR",
                "propagate": False
            },
            "motor": {
                "handlers": ["console"],
                "level": "ERROR",
                "propagate": False
            }
        }
    }
    
    # Aplicar configuración
    logging.config.dictConfig(log_config)

def get_logger(name: str) -> logging.Logger:
    """Obtener logger configurado"""
    return logging.getLogger(f"app.{name}")
