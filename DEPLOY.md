# Despliegue en la nube

La app se empaqueta como **un solo servicio**: FastAPI sirve la API y también el
frontend de React ya compilado. Eso significa un contenedor + una base de datos,
sin CORS ni proxy de nginx.

```
┌─────────────────────────────┐      ┌──────────────┐
│  Servicio web (Dockerfile)  │─────▶│  PostgreSQL  │
│  FastAPI + React compilado  │      │  (gestionado)│
└─────────────────────────────┘      └──────────────┘
```

## Desplegar en Railway

1. Entrar a [railway.app](https://railway.app) e iniciar sesión con GitHub.
2. **New Project → Deploy from GitHub repo** → elegir `Javvit/plantas-medicinales`.
3. En el proyecto: **+ New → Database → Add PostgreSQL**.
4. Abrir el servicio web → pestaña **Variables** → agregar:

   | Variable | Valor |
   |---|---|
   | `DATABASE_URL` | `${{Postgres.DATABASE_URL}}` (referencia a la base creada) |
   | `SECRET_KEY` | una cadena larga y aleatoria — **no** dejar la de por defecto |
   | `ACCESS_TOKEN_EXPIRE_MINUTES` | `480` |
   | `CORS_ORIGINS` | `*` |

   Para generar el `SECRET_KEY`:

   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(48))"
   ```

5. Pestaña **Settings → Networking → Generate Domain**. Railway entrega una URL
   pública tipo `https://algo.up.railway.app`.
6. El primer despliegue aplica las migraciones de Alembic y ejecuta los seeds
   automáticamente (ambos son idempotentes: si ya corrieron, no duplican datos).

Listo — el cliente entra por esa URL desde cualquier navegador, sin Docker ni
instalación.

## Alternativa: Render

Mismo Dockerfile. **New → Web Service → Docker**, y crear aparte un
**PostgreSQL**; luego copiar su *Internal Database URL* a la variable
`DATABASE_URL`. Render inyecta `PORT` automáticamente y el Dockerfile ya lo
respeta.

## Verificar que quedó bien

- `https://TU-URL/health` → debe responder `{"status":"ok"}`
- `https://TU-URL/docs` → documentación interactiva de la API
- `https://TU-URL/` → pantalla de login

## Desarrollo local

Sigue igual que siempre, con los tres contenedores:

```bash
docker-compose up -d --build
```

Frontend en `http://localhost:3000`, API en `http://localhost:8000`.

El `Dockerfile` de la raíz es **solo para producción**; `docker-compose.yml` usa
`backend/Dockerfile` y `frontend/Dockerfile`, que no cambiaron.

## Respaldos

Con la base gestionada en la nube, los respaldos los hace el proveedor. Para una
copia manual:

```bash
pg_dump "$DATABASE_URL" > respaldo_$(date +%Y%m%d).sql
```
