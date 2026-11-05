import os
from dotenv import load_dotenv

load_dotenv()

POS_DB_USER = os.getenv("POS_DB_USER", "postgres")
POS_DB_PASSWORD = os.getenv("POS_DB_PASSWORD", "admin_pos_123")
POS_DB_HOST = os.getenv("POS_DB_HOST", "localhost")
POS_DB_PORT = os.getenv("POS_DB_PORT", "5433")
POS_DB_NAME = os.getenv("POS_DB_NAME", "pos_alfredos")

GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID", "retailbi-509402")
BQ_DATASET_NAME = os.getenv("BQ_DATASET_NAME", "retailbi_dwh")
GOOGLE_APPLICATION_CREDENTIALS = os.getenv(
    "GOOGLE_APPLICATION_CREDENTIALS",
    "./credentials/gcp_service_account.json"
)

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_APPLICATION_CREDENTIALS

PREFECT_API_URL = os.getenv("PREFECT_API_URL", "http://localhost:4200/api")
os.environ["PREFECT_API_URL"] = PREFECT_API_URL