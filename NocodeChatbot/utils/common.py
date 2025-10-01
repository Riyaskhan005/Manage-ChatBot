import datetime
from cryptography.fernet import Fernet



crypto_key = "y7nyMfwrCnTMiS06REnDjRKRRTx_DQ_ztZE358J4Cc0="

def get_utc_now():
    now = datetime.datetime.utcnow()
    utc_time_str = now.strftime("%Y-%m-%d %H:%M:%S")
    return utc_time_str

def encrypt_data(data: str) -> bytes:
    f = Fernet(crypto_key)
    return f.encrypt(data.encode())

def decrypt_data(token: bytes) -> str:
    f = Fernet(crypto_key)
    return f.decrypt(token).decode()