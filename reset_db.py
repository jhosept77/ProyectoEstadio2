from sqlmodel import SQLModel
from database import engine

print("Eliminando y recreando las tablas...")

SQLModel.metadata.drop_all(engine)
SQLModel.metadata.create_all(engine)

print(" Base de datos reiniciada correctamente.")

