import logging
import logging.config
import sys
from typing import Dict, Any
import os
from app.config.settings import settings

def setup_logging() -> None:
    """Configurar logging estructurado para la aplicación"""
    
    # Asegurar que exista el directorio de logs
    try:
        os.makedirs("logs", exist_ok=True)
    except Exception:
        pass

    # Configuración base
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
                "level": settings.LOG_LEVEL,
                "formatter": settings.LOG_FORMAT,
                "stream": sys.stdout
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": settings.LOG_LEVEL,
                "formatter": settings.LOG_FORMAT,
                "filename": "logs/app.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5
            }
        },
        "loggers": {
            "": {  # Root logger
                "handlers": ["console"],
                "level": settings.LOG_LEVEL,
                "propagate": False
            },
            "app": {
                "handlers": ["console", "file"],
                "level": settings.LOG_LEVEL,
                "propagate": False
            },
            "uvicorn": {
                "handlers": ["console"],
                "level": "INFO",
                "propagate": False
            },
            "motor": {
                "handlers": ["console"],
                "level": "WARNING",
                "propagate": False
            }
        }
    }
    
    # Aplicar configuración
    logging.config.dictConfig(log_config)
    
    # Configurar logger principal
    logger = logging.getLogger("app")
    logger.info(f"Logging configurado - Nivel: {settings.LOG_LEVEL}, Formato: {settings.LOG_FORMAT}")

def get_logger(name: str) -> logging.Logger:
    """Obtener logger configurado"""
    return logging.getLogger(f"app.{name}")
