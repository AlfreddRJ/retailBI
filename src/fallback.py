import os
import pickle
from cryptography.fernet import Fernet

FALLBACK_DIR = os.path.join(os.path.dirname(__file__), "fallback_storage")
KEY_FILE = os.path.join(FALLBACK_DIR, ".fernet.key")
DUMP_FILE = os.path.join(FALLBACK_DIR, "pending_payload.enc")

def _obtener_cipher():
    os.makedirs(FALLBACK_DIR, exist_ok=True)
    if not os.path.exists(KEY_FILE):
        with open(KEY_FILE, "wb") as f:
            f.write(Fernet.generate_key())
    with open(KEY_FILE, "rb") as f:
        return Fernet(f.read())

def guardar_respaldo_encriptado(payload: dict):
    cipher = _obtener_cipher()
    datos_serializados = pickle.dumps(payload)
    datos_encriptados = cipher.encrypt(datos_serializados)
    with open(DUMP_FILE, "wb") as f:
        f.write(datos_encriptados)
    print(f"Alerta de red: Respaldo temporal encriptado guardado en {DUMP_FILE}")

def recuperar_respaldo_encriptado():
    if not os.path.exists(DUMP_FILE):
        return None
    cipher = _obtener_cipher()
    with open(DUMP_FILE, "rb") as f:
        datos_encriptados = f.read()
    os.remove(DUMP_FILE)
    return pickle.loads(cipher.decrypt(datos_encriptados))