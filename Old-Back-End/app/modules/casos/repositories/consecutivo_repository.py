"""Repositorio para el manejo de consecutivos de casos."""

from typing import Optional, List
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.errors import DuplicateKeyError
from app.modules.casos.models.consecutivo import ConsecutivoCaso


class ConsecutivoRepository:
    """Repositorio para operaciones CRUD de consecutivos."""
    
    def __init__(self, database: AsyncIOMotorDatabase):
        self.database = database
        self.collection = database.consecutivos_casos
        
    async def inicializar_indices(self):
        """Crear índices únicos para optimizar consultas."""
        await self.collection.create_index("ano", unique=True)
    
    async def obtener_siguiente_numero(self, ano: int) -> int:
        """Obtener el siguiente número consecutivo de forma atómica."""
        self._validar_ano(ano)
        
        resultado = await self.collection.find_one_and_update(
            {"ano": ano},
            {
                "$inc": {"ultimo_numero": 1},
                "$set": {"fecha_actualizacion": datetime.utcnow()}
            },
            upsert=True,
            return_document=True
        )
        
        return resultado["ultimo_numero"] if resultado else 1
    
    async def consultar_proximo_numero(self, ano: int) -> int:
        """Consultar cuál será el próximo número consecutivo SIN incrementarlo."""
        self._validar_ano(ano)
        documento = await self.collection.find_one({"ano": ano}, {"ultimo_numero": 1})
        return documento["ultimo_numero"] + 1 if documento else 1
    
    
    async def obtener_consecutivo_por_ano(self, ano: int) -> Optional[ConsecutivoCaso]:
        """Obtener información del consecutivo para un año específico."""
        self._validar_ano(ano)
        documento = await self.collection.find_one({"ano": ano})
        return ConsecutivoCaso(**documento) if documento else None
    
    async def crear_consecutivo_ano(self, ano: int, numero_inicial: int = 0) -> ConsecutivoCaso:
        """Crear un nuevo control de consecutivos para un año."""
        self._validar_ano(ano)
        self._validar_numero_inicial(numero_inicial)
        
        consecutivo_data = {
            "ano": ano,
            "ultimo_numero": numero_inicial,
            "fecha_actualizacion": datetime.utcnow()
        }
        
        try:
            await self.collection.insert_one(consecutivo_data)
            return ConsecutivoCaso(**consecutivo_data)
        except DuplicateKeyError:
            raise ValueError(f"Ya existe un consecutivo para el año {ano}")
    
    async def listar_todos_consecutivos(self) -> List[ConsecutivoCaso]:
        """Listar todos los consecutivos por año."""
        cursor = self.collection.find({}, {"_id": 0}).sort("ano", -1)
        documentos = await cursor.to_list(length=None)
        return [ConsecutivoCaso(**doc) for doc in documentos]
    
    async def resetear_consecutivo_ano(self, ano: int, nuevo_numero: int = 0) -> bool:
        """Resetear el consecutivo de un año específico."""
        self._validar_ano(ano)
        self._validar_numero_inicial(nuevo_numero)
        
        resultado = await self.collection.update_one(
            {"ano": ano},
            {"$set": {"ultimo_numero": nuevo_numero, "fecha_actualizacion": datetime.utcnow()}}
        )
        return resultado.modified_count > 0
    
    async def generar_codigo_caso(self, ano: int) -> str:
        """Generar código completo del caso (YYYY-NNNNN)."""
        numero = await self.obtener_siguiente_numero(ano)
        return f"{ano}-{numero:05d}"
    
    async def obtener_estadisticas_consecutivos(self) -> dict:
        """Obtener estadísticas de todos los consecutivos."""
        pipeline = [
            {
                "$group": {
                    "_id": None,
                    "total_anos": {"$sum": 1},
                    "total_casos": {"$sum": "$ultimo_numero"},
                    "promedio_casos_por_ano": {"$avg": "$ultimo_numero"},
                    "ano_mas_activo": {
                        "$first": {
                            "$cond": [
                                {"$eq": [{"$max": "$ultimo_numero"}, "$ultimo_numero"]},
                                "$ano",
                                None
                            ]
                        }
                    }
                }
            }
        ]
        
        result = await self.collection.aggregate(pipeline).to_list(length=1)
        if result:
            stats = result[0]
            stats.pop("_id", None)
            return stats
        return {
            "total_anos": 0,
            "total_casos": 0,
            "promedio_casos_por_ano": 0,
            "ano_mas_activo": None
        }
    
    def _validar_ano(self, ano: int) -> None:
        """Validar que el año esté en un rango válido."""
        current_year = datetime.now().year
        if ano < 2000 or ano > current_year + 5:
            raise ValueError(f"Año {ano} no está en el rango válido (2000-{current_year + 5})")
    
    def _validar_numero_inicial(self, numero: int) -> None:
        """Validar que el número inicial sea válido."""
        if numero < 0:
            raise ValueError("El número inicial no puede ser negativo")
        if numero > 999999:
            raise ValueError("El número inicial excede el límite permitido (999,999)")
