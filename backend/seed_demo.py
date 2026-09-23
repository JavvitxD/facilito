"""
Siembra el ambiente de demostracion. Idempotente: si ya existe, no hace nada.
La logica vive en app/demo.py para que la API pueda reutilizarla al restaurar.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from app.database import SessionLocal
from app.demo import crear_si_no_existe, EMAIL_DEMO, PASSWORD_DEMO

db = SessionLocal()
try:
    if crear_si_no_existe(db):
        print(f"Ambiente de demostracion listo: {EMAIL_DEMO} / {PASSWORD_DEMO}")
    else:
        print("Seed demo ya ejecutado, omitiendo.")
finally:
    db.close()
