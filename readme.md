#  API de Venta de Sillas para Conciertos

API REST desarrollada con **FastAPI** y **SQLModel**, que gestiona la venta de boletas para conciertos en un estadio. Se manejan precios por zona (VIP o General), descuentos según el día, compras con o sin usuario registrado, y sincronización con proveedores externos.

---

##  Tecnologías utilizadas

- Python 3.10+
- FastAPI
- SQLModel
- SQLite
- Pydantic

---

##  Estructura del Proyecto



├── main.py 
├── models.py 
├── database.py 
├── router.py 
├── README.md 





 Silla
Asiento disponible o vendido.

Campos: id, fila, numero, estado, zona, dia, comprado_por (opcional)

 CompraRequest
DTO para realizar una compra.

Campos: zona, dia, cantidad, usuario_id (opcional)

 Usuario
Información personal del comprador.

Campos: id, nombre, apellido, zona

 Sincronizacion
Registro de compras sincronizadas.

Campos: id, silla_id, usuario_id (opcional), fecha




 Conexión a base de datos (database.py)
Usa SQLite y se configura automáticamente:

python
Copiar
Editar
DATABASE_URL = "sqlite:///./miro.db"
engine = create_engine(DATABASE_URL, echo=True)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session




Endpoints disponibles (router.py)
 Ventas y Sillas
POST /sillas/cargar – Carga sillas para los 2 días y ambas zonas.

GET /sillas/disponibles?zona=VIP – Lista sillas disponibles, filtrado opcional por zona.

GET /disponibilidad?dia=1 – Muestra sillas vendidas/disponibles por zona para un día.

POST /comprar – Realiza una compra. El usuario es opcional.

 Usuarios
POST /usuarios/ – Registra un nuevo usuario.

GET /usuarios/ – Lista todos los usuarios registrados.

PUT /usuarios/{id} – Actualiza datos de un usuario existente.

GET /usuarios/{id}/compras – Muestra sillas compradas por el usuario.

 Lógica de precios y descuentos
Zonas disponibles: VIP, General

Días disponibles: 1, 2

Precios:

VIP: $500,000 (sin descuento)

General: $300,000

Día 2 tiene 36.67% de descuento

Las compras pueden hacerse sin registrar un usuario

 Documentación automática
FastAPI genera automáticamente la documentación Swagger:

bash
Copiar
Editar
http://localhost:8000/docs
 Notas
El sistema está diseñado para manejar sincronización con múltiples proveedores (a través del modelo Sincronizacion).

Toda verificación de disponibilidad se hace en tiempo real sobre la base de datos.

 Licencia
Este proyecto es de uso libre para fines educativos, prácticas o pruebas.


