import os
from sqlalchemy import create_engine
from google.cloud import bigquery
from config import (
    POS_DB_USER, POS_DB_PASSWORD, POS_DB_HOST, POS_DB_PORT, POS_DB_NAME,
    GCP_PROJECT_ID
)

WATERMARK_FILE = os.path.join(os.path.dirname(__file__), ".last_sync.txt")

def get_pos_engine():
    url = f"postgresql+psycopg2://{POS_DB_USER}:{POS_DB_PASSWORD}@{POS_DB_HOST}:{POS_DB_PORT}/{POS_DB_NAME}"
    return create_engine(url)

def get_bq_client():
    return bigquery.Client(project=GCP_PROJECT_ID)

def leer_ultima_sincronizacion() -> str:
    if os.path.exists(WATERMARK_FILE):
        with open(WATERMARK_FILE, "r", encoding="utf-8") as f:
            return f.read().strip()
    return "1970-01-01 00:00:00"

def guardar_ultima_sincronizacion(timestamp_str: str):
    with open(WATERMARK_FILE, "w", encoding="utf-8") as f:
        f.write(timestamp_str)