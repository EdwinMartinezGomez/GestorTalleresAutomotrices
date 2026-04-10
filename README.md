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
- Kafka

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

## Kafka

Variables recomendadas para .env:

- KAFKA_ENABLED=true
- KAFKA_BOOTSTRAP_SERVERS=localhost:9092
- KAFKA_CLIENT_ID=gestor-talleres-api
- KAFKA_TOPIC_PREFIX=talleres
- KAFKA_METRICS_ENABLED=true
- KAFKA_METRICS_CONSUMER_GROUP=gestor-talleres-metricas
- KAFKA_AUTO_OFFSET_RESET=latest

Levantar Kafka local:

	docker compose up -d

Los eventos se publican automaticamente en:

- talleres.auth
- talleres.clientes
- talleres.inventario
- talleres.ordenes
- talleres.pagos

Consulta de metricas agregadas por consumidor Kafka:

- GET /reportes/kafka-metricas

Endpoints estilo Node para pruebas Kafka:

- GET /test-kafka
- GET /metrics

## Flujo de autenticacion

1. POST /auth/login con username y password
2. Obtener access_token
3. Enviar Authorization: Bearer <token> en todas las rutas protegidas
4. El middleware valida token y roles

## Roles y permisos

- admin: acceso total al sistema.
- recepcionista: registrar y actualizar clientes y vehiculos.
- mecanico: gestionar ordenes de trabajo e historial.
- almacen: gestionar inventario y movimientos de stock.
- cajero: registrar y consultar pagos.
- gerencia: acceso a reportes y resumenes del negocio.

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