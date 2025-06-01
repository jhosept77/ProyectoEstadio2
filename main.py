from fastapi import FastAPI
from sqlmodel import SQLModel, Field
from typing import Optional
from fastapi import FastAPI, Depends
from sqlmodel import Session, select
from typing import List
from database import get_session, create_db_and_tables
from fastapi import FastAPI
from sqlmodel import SQLModel, create_engine
from fastapi import FastAPI, HTTPException
from sqlmodel import Session, create_engine, select
from models import Silla, CompraRequest
from fastapi import FastAPI, Query
from typing import Dict
from database import engine
from models import Silla
from fastapi import Query
from models import Usuario


#=================================================================================================================================================================================================


sqlite_file_name = "miro.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
engine = create_engine(sqlite_url, echo=True)


SQLModel.metadata.create_all(engine)





app = FastAPI()



@app.on_event("startup")
def on_startup():
    create_db_and_tables()





#=================================================================================================================================================================================================




def crear_sillas(session: Session, cantidad: int, zona: str, dia: int):
    fila = "A" if zona == "VIP" else "B"
    for numero in range(1, cantidad + 1):
        silla = Silla(
            zona=zona,
            fila=fila,
            numero=numero,
            estado="disponible",
            dia=dia  
        )
        session.add(silla)
    session.commit()



@app.post("/sillas/cargar")
def cargar_sillas():
    with Session(engine) as session:
        crear_sillas(session, 200, "VIP", dia=1)
        crear_sillas(session, 200, "VIP", dia=2)
        crear_sillas(session, 400, "General", dia=1)
        crear_sillas(session, 400, "General", dia=2)
    return {"mensaje": "Sillas creadas para ambos días y zonas"}





#=================================================================================================================================================================================================




from fastapi import FastAPI, Query
from sqlmodel import Session, select
from typing import Dict
from database import engine
from models import Silla


@app.get("/disponibilidad")
def disponibilidad_por_dia_y_segmento(dia: int = Query(..., ge=1, le=2)):
    with Session(engine) as session:
        zonas = ["VIP", "General"]
        resultado: Dict[str, Dict[str, int]] = {}

        for zona in zonas:
            disponibles = session.exec(
                select(Silla).where(
                    Silla.zona == zona,
                    Silla.estado == "disponible",
                    Silla.dia == dia
                )
            ).all()

            vendidos = session.exec(
                select(Silla).where(
                    Silla.zona == zona,
                    Silla.estado == "vendido",
                    Silla.dia == dia
                )
            ).all()

            resultado[zona] = {
                "disponibles": len(disponibles),
                "vendidos": len(vendidos)
            }

    return {
        "dia": dia,
        "disponibilidad": resultado
    }





#=================================================================================================================================================================================================





from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import Session, select
from typing import Optional
from models import CompraRequest, Usuario, Silla
from database import get_session

PRECIOS = {
    "VIP": {1: 500000, 2: 500000},
    "General": {1: 300000, 2: 190000}
}

@app.post("/comprar")
def comprar(request: CompraRequest, session: Session = Depends(get_session)):

 
    if request.zona not in PRECIOS or request.dia not in PRECIOS[request.zona]:
        raise HTTPException(status_code=400, detail="Zona o día inválido")

   
    usuario = None
    if request.usuario_id is not None:
        usuario = session.get(Usuario, request.usuario_id)
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

    sillas_disponibles = session.exec(
        select(Silla)
        .where(
            Silla.zona == request.zona,
            Silla.estado == "disponible",
            Silla.dia == request.dia
        )
        .limit(request.cantidad)
    ).all()

    if len(sillas_disponibles) < request.cantidad:
        raise HTTPException(status_code=400, detail="No hay suficientes sillas disponibles")

   
    for silla in sillas_disponibles:
        silla.estado = "vendido"
        silla.comprado_por = usuario.id if usuario else None
        session.add(silla)

    session.commit()

  
    precio_unitario = PRECIOS[request.zona][request.dia]
    total = precio_unitario * request.cantidad

    return {
        "mensaje": "Compra realizada con éxito",
        "usuario": {
            "id": usuario.id,
            "nombre": usuario.nombre,
            "apellido": usuario.apellido
        } if usuario else None,
        "zona": request.zona,
        "dia": request.dia,
        "cantidad": request.cantidad,
        "precio_unitario": precio_unitario,
        "total": total,
        "sillas_compradas": [
            {"id": s.id, "numero": s.numero, "fila": s.fila} for s in sillas_disponibles
        ]
    }






#=================================================================================================================================================================================================






@app.get("/sillas/disponibles")
def sillas_disponibles(zona: Optional[str] = None):
    with Session(engine) as session:
        query = select(Silla).where(Silla.estado == "disponible")
        if zona:
            query = query.where(Silla.zona == zona)
        sillas = session.exec(query).all()
        return {"cantidad": len(sillas), "sillas": sillas}
    






#=================================================================================================================================================================================================




from fastapi import FastAPI, Depends
from sqlmodel import Session
from database import get_session


@app.post("/usuarios/")
def crear_usuario(usuario: Usuario, session: Session = Depends(get_session)):
    session.add(usuario)
    session.commit()
    session.refresh(usuario)
    return {
        "mensaje": "Usuario registrado correctamente",
        "usuario_id": usuario.id
    }




#=================================================================================================================================================================================================



@app.get("/usuarios/{usuario_id}/compras")
def obtener_compras_usuario(usuario_id: int, session: Session = Depends(get_session)):
    sillas_compradas = session.exec(
        select(Silla).where(Silla.comprado_por == usuario_id)
    ).all()

    return {
        "usuario_id": usuario_id,
        "sillas_compradas": [{"id": s.id, "fila": s.fila, "numero": s.numero, "zona": s.zona, "dia": s.dia} for s in sillas_compradas]
    }






#=================================================================================================================================================================================================






from fastapi import Query, Depends
from typing import Optional
from sqlmodel import Session, select
from models import Silla, Usuario
from database import get_session

@app.get("/sillas/vendidas")
def obtener_sillas_vendidas(
    dia: Optional[int] = Query(None, ge=1, le=2),
    zona: Optional[str] = None,
    fila: Optional[str] = None,
    session: Session = Depends(get_session)
):
    query = select(Silla, Usuario).join(Usuario, Silla.comprado_por == Usuario.id, isouter=True).where(Silla.estado == "vendido")

    if dia is not None:
        query = query.where(Silla.dia == dia)
    if zona:
        query = query.where(Silla.zona == zona)
    if fila:
        query = query.where(Silla.fila == fila)

    results = session.exec(query).all()

   
    sillas_vendidas = []
    for silla, usuario in results:
        sillas_vendidas.append({
            "id": silla.id,
            "zona": silla.zona,
            "fila": silla.fila,
            "numero": silla.numero,
            "dia": silla.dia,
            "comprador": f"{usuario.nombre} {usuario.apellido}" if usuario else None
        })

    return {
        "total": len(sillas_vendidas),
        "sillas_vendidas": sillas_vendidas
    }






#=================================================================================================================================================================================================





from fastapi import HTTPException, Path, Depends
from sqlmodel import Session
from models import Usuario
from database import get_session

@app.put("/usuarios/{usuario_id}")
def actualizar_usuario(
    usuario_id: int = Path(..., description="ID del usuario a actualizar"),
    usuario_actualizado: Usuario = None,
    session: Session = Depends(get_session)
):
    usuario = session.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

  
    if usuario_actualizado.nombre is not None:
        usuario.nombre = usuario_actualizado.nombre
    if usuario_actualizado.apellido is not None:
        usuario.apellido = usuario_actualizado.apellido
    if usuario_actualizado.zona is not None:
        usuario.zona = usuario_actualizado.zona

    session.add(usuario)
    session.commit()
    session.refresh(usuario)

    return {
        "mensaje": "Usuario actualizado correctamente",
        "usuario": usuario
    }











@app.get("/usuarios/", response_model=List[Usuario])
def listar_usuarios(session: Session = Depends(get_session)):
    usuarios = session.exec(select(Usuario)).all()
    return usuarios
