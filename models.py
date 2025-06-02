from typing import Optional
from sqlmodel import SQLModel, Field
from pydantic import BaseModel
from datetime import datetime



#=================================================================================================================================================================================================







class Silla(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    fila: str = Field(nullable=False)
    numero: int = Field(nullable=False)
    estado: str = Field(nullable=False, default="disponible")
    zona: str = Field(nullable=False)
    dia: int = Field(nullable=False)
    comprado_por: Optional[int] = Field(default=None, foreign_key="usuario.id")




#=================================================================================================================================================================================================




class CompraRequest(SQLModel):
    zona: str = Field(description="Zona: VIP o General")
    dia: int = Field(ge=1, le=2, description="Día del evento: 1 o 2")
    cantidad: int = Field(gt=0, description="Cantidad de sillas a comprar")
    usuario_id: Optional[int] = Field(default=None, description="ID del usuario que compra (opcional)")






#=================================================================================================================================================================================================



class Usuario(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    apellido: str
    zona: str




#=================================================================================================================================================================================================







class Sincronizacion(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    silla_id: int
    usuario_id: Optional[int] = None
    fecha: datetime = Field(default_factory=datetime.utcnow)









