import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    """
    Crea y devuelve una conexión a PostgreSQL usando las variables del .env.
    """
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT", 5432)
    )