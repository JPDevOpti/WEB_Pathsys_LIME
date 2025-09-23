"""Repositorio para el manejo de consecutivos de tickets."""

from typing import Optional, List
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.errors import DuplicateKeyError
from app.modules.tickets.models.consecutivo import ConsecutivoTicket


class ConsecutivoTicketRepository:
    """Repositorio para operaciones CRUD de consecutivos de tickets."""
    
    def __init__(self, database: AsyncIOMotorDatabase):
        self.database = database
        self.collection = database.consecutivos_tickets
        
    async def inicializar_indices(self):
        """Crear índices únicos para optimizar consultas."""
        await self.collection.create_index("year", unique=True)
    
    async def obtener_siguiente_numero(self, year: int) -> int:
        """Obtener el siguiente número consecutivo de forma atómica."""
        self._validar_year(year)
        
        resultado = await self.collection.find_one_and_update(
            {"year": year},
            {
                "$inc": {"last_number": 1},
                "$set": {"fecha_actualizacion": datetime.utcnow()}
            },
            upsert=True,
            return_document=True
        )
        
        return resultado["last_number"] if resultado else 1
    
    async def consultar_proximo_numero(self, year: int) -> int:
        """Consultar cuál será el próximo número consecutivo SIN incrementarlo."""
        self._validar_year(year)
        documento = await self.collection.find_one({"year": year}, {"last_number": 1})
        return documento["last_number"] + 1 if documento else 1
    
    async def obtener_consecutivo_por_year(self, year: int) -> Optional[ConsecutivoTicket]:
        """Obtener información del consecutivo para un año específico."""
        self._validar_year(year)
        documento = await self.collection.find_one({"year": year})
        return ConsecutivoTicket(**documento) if documento else None
    
    async def crear_consecutivo_year(self, year: int, numero_inicial: int = 0) -> ConsecutivoTicket:
        """Crear un nuevo control de consecutivos para un año."""
        self._validar_year(year)
        self._validar_numero_inicial(numero_inicial)
        
        consecutivo_data = {
            "year": year,
            "last_number": numero_inicial,
            "fecha_actualizacion": datetime.utcnow()
        }
        
        try:
            await self.collection.insert_one(consecutivo_data)
            return ConsecutivoTicket(**consecutivo_data)
        except DuplicateKeyError:
            raise ValueError(f"Ya existe un consecutivo para el año {year}")
    
    async def listar_todos_consecutivos(self) -> List[ConsecutivoTicket]:
        """Listar todos los consecutivos por año."""
        cursor = self.collection.find({}, {"_id": 0}).sort("year", -1)
        documentos = await cursor.to_list(length=None)
        return [ConsecutivoTicket(**doc) for doc in documentos]
    
    async def resetear_consecutivo_year(self, year: int, nuevo_numero: int = 0) -> bool:
        """Resetear el consecutivo de un año específico."""
        self._validar_year(year)
        self._validar_numero_inicial(nuevo_numero)
        
        resultado = await self.collection.update_one(
            {"year": year},
            {"$set": {"last_number": nuevo_numero, "fecha_actualizacion": datetime.utcnow()}}
        )
        return resultado.modified_count > 0
    
    async def generar_codigo_ticket(self, year: int) -> str:
        """Generar código completo del ticket (T-YYYY-NNN)."""
        numero = await self.obtener_siguiente_numero(year)
        return f"T-{year}-{numero:03d}"
    
    async def obtener_estadisticas_consecutivos(self) -> dict:
        """Obtener estadísticas de todos los consecutivos."""
        pipeline = [
            {
                "$group": {
                    "_id": None,
                    "total_years": {"$sum": 1},
                    "total_tickets": {"$sum": "$last_number"},
                    "min_year": {"$min": "$year"},
                    "max_year": {"$max": "$year"}
                }
            }
        ]
        
        resultado = await self.collection.aggregate(pipeline).to_list(1)
        if resultado:
            stats = resultado[0]
            stats.pop("_id")
            return stats
        
        return {
            "total_years": 0,
            "total_tickets": 0,
            "min_year": None,
            "max_year": None
        }
    
    def _validar_year(self, year: int) -> None:
        """Validar que el año esté en el rango permitido."""
        current_year = datetime.now().year
        if year < 2000 or year > current_year + 5:
            raise ValueError(f"Año debe estar entre 2000 y {current_year + 5}")
    
    def _validar_numero_inicial(self, numero: int) -> None:
        """Validar el número inicial."""
        if numero < 0:
            raise ValueError("El número inicial no puede ser negativo")
        if numero > 999999:
            raise ValueError("El número inicial excede el límite permitido")
