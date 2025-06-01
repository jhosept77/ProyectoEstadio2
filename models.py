from typing import Optional
from sqlmodel import SQLModel, Field
from pydantic import BaseModel



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
    zona: str
    dia: int
    cantidad: int
    usuario_id: int






#=================================================================================================================================================================================================



class Usuario(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    apellido: str
    zona: str
