from fastapi import APIRouter, Query
from sqlmodel import Session, select
from typing import Optional
from models import Silla
from database import get_session
from fastapi import APIRouter, Depends, HTTPException, Path
from typing import List
from models import Usuario, Silla
from fastapi import APIRouter, Depends, HTTPException
from models import CompraRequest, Usuario, Silla, Sincronizacion




router = APIRouter()







#=================================================================================================================================================================================================








@router.post("/sillas/cargar")
def cargar_sillas():
    with Session(get_session()) as session:
        def crear_sillas(cantidad: int, zona: str, dia: int):
            fila = "A" if zona == "VIP" else "B"
            for numero in range(1, cantidad + 1):
                session.add(Silla(zona=zona, fila=fila, numero=numero, estado="disponible", dia=dia))
            session.commit()
        
        crear_sillas(200, "VIP", 1)
        crear_sillas(200, "VIP", 2)
        crear_sillas(400, "General", 1)
        crear_sillas(400, "General", 2)
    return {"mensaje": "Sillas creadas para ambos días y zonas"}

@router.get("/sillas/disponibles")
def sillas_disponibles(zona: Optional[str] = None):
    with Session(get_session()) as session:
        query = select(Silla).where(Silla.estado == "disponible")
        if zona:
            query = query.where(Silla.zona == zona)
        sillas = session.exec(query).all()
        return {
            "cantidad": len(sillas),
            "sillas": [{"id": s.id, "zona": s.zona, "fila": s.fila, "numero": s.numero, "dia": s.dia} for s in sillas]
        }

@router.get("/disponibilidad")
def disponibilidad(dia: int = Query(..., ge=1, le=2)):
    with Session(get_session()) as session:
        zonas = ["VIP", "General"]
        resultado = {}
        for zona in zonas:
            disponibles = session.exec(select(Silla).where(Silla.zona == zona, Silla.estado == "disponible", Silla.dia == dia)).all()
            vendidos = session.exec(select(Silla).where(Silla.zona == zona, Silla.estado == "vendido", Silla.dia == dia)).all()
            resultado[zona] = {"disponibles": len(disponibles), "vendidos": len(vendidos)}
    return {"dia": dia, "disponibilidad": resultado}




#=================================================================================================================================================================================================






@router.post("/usuarios/")
def crear_usuario(usuario: Usuario, session: Session = Depends(get_session)):
    session.add(usuario)
    session.commit()
    session.refresh(usuario)
    return {"mensaje": "Usuario registrado correctamente", "usuario_id": usuario.id}

@router.get("/usuarios/", response_model=List[Usuario])
def listar_usuarios(session: Session = Depends(get_session)):
    return session.exec(select(Usuario)).all()

@router.put("/usuarios/{usuario_id}")
def actualizar_usuario(usuario_id: int, usuario_actualizado: Usuario, session: Session = Depends(get_session)):
    usuario = session.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    if usuario_actualizado.nombre:
        usuario.nombre = usuario_actualizado.nombre
    if usuario_actualizado.apellido:
        usuario.apellido = usuario_actualizado.apellido
    if usuario_actualizado.zona:
        usuario.zona = usuario_actualizado.zona

    session.add(usuario)
    session.commit()
    session.refresh(usuario)
    return {"mensaje": "Usuario actualizado correctamente", "usuario": usuario}

@router.get("/usuarios/{usuario_id}/compras")
def obtener_compras(usuario_id: int, session: Session = Depends(get_session)):
    sillas = session.exec(select(Silla).where(Silla.comprado_por == usuario_id)).all()
    return {
        "usuario_id": usuario_id,
        "sillas_compradas": [{"id": s.id, "fila": s.fila, "numero": s.numero, "zona": s.zona, "dia": s.dia} for s in sillas]
    }


#=================================================================================================================================================================================================



router = APIRouter()

@router.post("/comprar")
def comprar(request: CompraRequest, session: Session = Depends(get_session)):
    PRECIOS = {"VIP": {1: 500000, 2: 500000}, "General": {1: 300000, 2: 300000}}
    DESCUENTOS = {"VIP": {1: 0, 2: 0}, "General": {1: 0, 2: 0.3667}}

    if request.zona not in PRECIOS or request.dia not in PRECIOS[request.zona]:
        raise HTTPException(status_code=400, detail="Zona o día inválido")

    usuario = session.get(Usuario, request.usuario_id) if request.usuario_id else None
    if request.usuario_id and not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    sillas = session.exec(select(Silla).where(Silla.zona == request.zona, Silla.estado == "disponible", Silla.dia == request.dia).limit(request.cantidad)).all()

    if len(sillas) < request.cantidad:
        raise HTTPException(status_code=400, detail="No hay suficientes sillas disponibles")

    for silla in sillas:
        silla.estado = "vendido"
        silla.comprado_por = usuario.id if usuario else None
        session.add(silla)
        session.add(Sincronizacion(silla_id=silla.id, usuario_id=usuario.id if usuario else None))

    session.commit()

    original = PRECIOS[request.zona][request.dia]
    descuento = DESCUENTOS[request.zona][request.dia]
    total = int(original * (1 - descuento)) * request.cantidad

    return {
        "mensaje": "Compra realizada con éxito",
        "usuario": {"id": usuario.id, "nombre": usuario.nombre, "apellido": usuario.apellido} if usuario else None,
        "zona": request.zona,
        "dia": request.dia,
        "cantidad": request.cantidad,
        "precio_original": original,
        "precio_con_descuento": int(original * (1 - descuento)),
        "descuento_aplicado": f"{descuento * 100:.2f}%",
        "total": total,
        "sillas_compradas": [{"id": s.id, "numero": s.numero, "fila": s.fila} for s in sillas]
    }






