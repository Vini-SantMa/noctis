from datetime import datetime, timedelta
import jwt
from passlib.context import CryptContext

SECRET_KEY = "chave_super_secreta_do_noctis" 
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 360

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str):
    # Trunca a senha para 72 bytes antes de enviar para o bcrypt
    return pwd_context.hash(password[:72])

def verify_password(plain_password, hashed_password):
    # Trunca a senha de entrada para garantir compatibilidade
    return pwd_context.verify(plain_password[:72], hashed_password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt