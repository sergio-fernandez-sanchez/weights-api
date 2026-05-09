from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime, timedelta
from passlib.context import CryptContext
from dotenv import load_dotenv
import os
import jwt

load_dotenv()
security = HTTPBearer()

SECRET_KEY = os.getenv("JWT_SECRET")
ALGORITHM  = os.getenv("JWT_ALGORITHM")
EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """
    Convierte una contraseña en texto plano a un hash seguro con bcrypt.
    """
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    """
    Compara una contraseña en texto plano con su hash.
    Devuelve True si coinciden, False si no.
    """
    return pwd_context.verify(plain, hashed)


def create_token(user_id: int) -> str:
    """
    Recibe un user_id y genera un token JWT firmado con la clave secreta.
    El token incluye el user_id y una fecha de expiración.
    """
    payload = {
        "user_id": user_id,
        "exp": datetime.now() + timedelta(minutes=EXPIRE_MINUTES)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> int:
    """
    Recibe un token JWT y devuelve el user_id que contiene.
    Lanza jwt.InvalidTokenError si el token es inválido o ha expirado.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload["user_id"]
    except jwt.InvalidTokenError:
        raise


def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> int:
    """
    Extrae el token del header Authorization, verifica su firma y expiración
    con decode_token(), y devuelve el user_id si es válido.
    """
    try:
        return decode_token(credentials.credentials)
    except:
        raise HTTPException(status_code=401, detail="Invalid or expired token")