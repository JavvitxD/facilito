# ---------------------------------------------------------------
# Imagen de PRODUCCION: un solo servicio que sirve la API y el frontend.
# El frontend se compila con VITE_API_URL vacio, asi que llama al mismo
# origen y no hace falta CORS ni proxy de nginx.
#
# Para desarrollo local se sigue usando docker-compose.yml (3 servicios).
# ---------------------------------------------------------------

# --- Etapa 1: compilar el frontend ---
FROM node:20-alpine AS frontend
WORKDIR /build
COPY frontend/package*.json ./
RUN npm ci || npm install
COPY frontend/ ./
ENV VITE_API_URL=""
RUN npm run build

# --- Etapa 2: backend + frontend compilado ---
FROM python:3.12-slim
WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./
COPY --from=frontend /build/dist ./static

ENV STATIC_DIR=/app/static
ENV PORT=8000
EXPOSE 8000

# Aplica migraciones y siembra datos (ambos seeds son idempotentes) antes de arrancar.
CMD sh -c "alembic upgrade head && python seed.py && python seed_mf.py && python seed_demo.py && uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"
