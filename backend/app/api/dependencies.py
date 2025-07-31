from fastapi import Depends, HTTPException, status
import datetime # Keep this import
from datetime import timedelta, datetime, timezone 
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from ..database import get_db
from ..crud import user as crud_user
from jose import JWTError, jwt
from ..schemas.user import TokenData
from ..core.config import settings

# Make sure this tokenUrl matches your actual login endpoint.
# Based on your previous examples, if your login endpoint is /auth/login,
# then this should be tokenUrl="/auth/login" or adjust it as needed.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login") # <--- Potentially update this to /auth/login

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

        user_id_str: str = payload.get("sub")
        if user_id_str is None:
            raise credentials_exception
        user_id: int = int(user_id_str)
        token_data = TokenData(user_id=user_id)

    except JWTError as e:
        raise credentials_exception
    except ValueError as e:
        raise credentials_exception

    user = crud_user.get_user_by_id(db, user_id=token_data.user_id)
    if user is None:
        raise credentials_exception

    print(f"--- DEBUG: User validated successfully: {user.email}")
    return user

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt