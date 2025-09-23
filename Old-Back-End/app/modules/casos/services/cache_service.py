"""Servicio de caché para optimizar consultas frecuentes del módulo de casos."""

import json
import asyncio
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timedelta
from functools import wraps
import hashlib

try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    print("Redis no disponible, usando caché en memoria")

from app.config.settings import settings


class CacheService:
    """Servicio de caché con soporte para Redis y fallback a memoria."""
    
    def __init__(self):
        self.redis_client = None
        self.memory_cache = {}
        self.cache_ttl = {
            'caso_stats': 300,  # 5 minutos
            'muestra_stats': 300,  # 5 minutos
            'casos_por_mes': 600,  # 10 minutos
            'oportunidad_stats': 600,  # 10 minutos
            'entidades_stats': 900,  # 15 minutos
            'pruebas_stats': 900,  # 15 minutos
            'caso_detail': 180,  # 3 minutos
            'caso_list': 60,  # 1 minuto
        }
        
        if REDIS_AVAILABLE:
            self._init_redis()
    
    def _init_redis(self):
        """Inicializar cliente Redis."""
        try:
            self.redis_client = redis.from_url(
                getattr(settings, 'REDIS_URL', 'redis://localhost:6379/0'),
                encoding='utf-8',
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True
            )
        except Exception as e:
            print(f"Error conectando a Redis: {e}")
            self.redis_client = None
    
    def _generate_cache_key(self, prefix: str, *args, **kwargs) -> str:
        """Generar clave de caché única."""
        key_data = f"{prefix}:{':'.join(map(str, args))}:{':'.join(f'{k}={v}' for k, v in sorted(kwargs.items()))}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    async def get(self, key: str) -> Optional[Any]:
        """Obtener valor del caché."""
        if self.redis_client:
            try:
                value = await self.redis_client.get(key)
                return json.loads(value) if value else None
            except Exception:
                pass
        
        # Fallback a memoria
        if key in self.memory_cache:
            data, expiry = self.memory_cache[key]
            if datetime.now() < expiry:
                return data
            else:
                del self.memory_cache[key]
        return None
    
    async def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        """Establecer valor en el caché."""
        if self.redis_client:
            try:
                await self.redis_client.setex(key, ttl, json.dumps(value, default=str))
                return True
            except Exception:
                pass
        
        # Fallback a memoria
        expiry = datetime.now() + timedelta(seconds=ttl)
        self.memory_cache[key] = (value, expiry)
        
        # Limpiar entradas expiradas periódicamente
        if len(self.memory_cache) > 1000:
            await self._cleanup_memory_cache()
        
        return True
    
    async def delete(self, key: str) -> bool:
        """Eliminar valor del caché."""
        if self.redis_client:
            try:
                await self.redis_client.delete(key)
                return True
            except Exception:
                pass
        
        # Fallback a memoria
        self.memory_cache.pop(key, None)
        return True
    
    async def delete_pattern(self, pattern: str) -> int:
        """Eliminar claves que coincidan con un patrón."""
        if self.redis_client:
            try:
                keys = await self.redis_client.keys(pattern)
                if keys:
                    return await self.redis_client.delete(*keys)
            except Exception:
                pass
        
        # Fallback a memoria
        deleted = 0
        for key in list(self.memory_cache.keys()):
            if pattern.replace('*', '') in key:
                del self.memory_cache[key]
                deleted += 1
        return deleted
    
    async def _cleanup_memory_cache(self):
        """Limpiar entradas expiradas del caché en memoria."""
        now = datetime.now()
        expired_keys = [
            key for key, (_, expiry) in self.memory_cache.items()
            if now >= expiry
        ]
        for key in expired_keys:
            del self.memory_cache[key]
    
    async def invalidate_caso_cache(self, caso_code: str):
        """Invalidar caché relacionado con un caso específico."""
        patterns = [
            f"caso_detail:{caso_code}",
            f"caso_list:*",
            f"caso_stats:*",
            f"muestra_stats:*",
            f"oportunidad_stats:*"
        ]
        
        for pattern in patterns:
            await self.delete_pattern(pattern)
    
    async def invalidate_stats_cache(self):
        """Invalidar caché de estadísticas."""
        patterns = [
            f"caso_stats:*",
            f"muestra_stats:*",
            f"entidades_stats:*",
            f"pruebas_stats:*",
            f"oportunidad_stats:*"
        ]
        
        for pattern in patterns:
            await self.delete_pattern(pattern)


def cached(ttl: int = 300, key_prefix: str = ""):
    """Decorador para caché de métodos."""
    def decorator(func):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            # Generar clave de caché
            cache_key = self.cache_service._generate_cache_key(
                f"{key_prefix}:{func.__name__}", 
                *args, 
                **kwargs
            )
            
            # Intentar obtener del caché
            cached_result = await self.cache_service.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Ejecutar función y guardar resultado
            result = await func(self, *args, **kwargs)
            await self.cache_service.set(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator


# Instancia global del servicio de caché
cache_service = CacheService()
