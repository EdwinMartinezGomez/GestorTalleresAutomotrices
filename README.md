# GestorTalleresAutomotrices

Backend en Python para gestion de talleres automotrices con arquitectura por capas:

- controllers
- services
- repositories
- entities
- schemas

Incluye autenticacion con Keycloak usando access token y validacion de roles.

## Stack

- FastAPI
- SQLAlchemy
- PostgreSQL
- Keycloak (OIDC)

## Estructura

app/
- api/
- controllers/
- core/
- entities/
- repositories/
- schemas/
- services/

sql/
- schema.sql

## Configuracion

1. Crear entorno virtual:

	python -m venv .venv
	.venv\Scripts\activate

2. Instalar dependencias:

	pip install -r requirements.txt

3. Crear archivo .env a partir de .env.example y ajustar valores.

4. Crear base de datos y ejecutar script:

	psql -U postgres -d taller_automotriz -f sql/schema.sql

5. Iniciar servidor:

	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

## Keycloak

Variables necesarias:

- KEYCLOAK_SERVER_URL
- KEYCLOAK_REALM
- KEYCLOAK_CLIENT_ID
- KEYCLOAK_CLIENT_SECRET
- KEYCLOAK_AUDIENCE (opcional)

## Flujo de autenticacion

1. POST /auth/login con username y password
2. Obtener access_token
3. Enviar Authorization: Bearer <token> en todas las rutas protegidas
4. El middleware valida token y roles

## Roles sugeridos

- admin
- recepcionista
- mecanico
- almacen
- cajero
- gerencia

## Endpoints principales

- Auth: /auth/login, /auth/keycloak/status
- Clientes: /clientes
- Vehiculos: /vehiculos
- Inventario: /inventario, /inventario/movimientos, /inventario/alertas
- Ordenes: /ordenes, /ordenes/repuestos, /ordenes/resumen/estados
- Pagos: /pagos
- Historial: /historial, /historial/vehiculo-completo
- Reportes: /reportes/ingresos, /reportes/alertas-stock, /reportes/ordenes

## Nota

El servidor puede iniciar incluso si Keycloak no responde en startup. En ese caso, las rutas protegidas devoleran error hasta que Keycloak este disponible.