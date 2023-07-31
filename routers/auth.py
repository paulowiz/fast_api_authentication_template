import sys

sys.path.append("../..")

from fastapi import Depends, HTTPException, status, APIRouter
from pydantic import BaseModel
from typing import Optional, Annotated
import models
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer, HTTPBearer
from datetime import datetime, timedelta
from jose import jwt, JWTError
import random
from send_grid import send_email
from secret import get_secret

JSON_SECRET = get_secret()
SENDER_EMAIL = JSON_SECRET['sendgrid']['sender_email']
SECRET_KEY = "KlgH6AzYDeZeGwD288to79I3vTHT8wp7"
ALGORITHM = "HS256"


class CreateUser(BaseModel):
    email: Optional[str]
    first_name: str
    last_name: str
    password: str


class UserCode(BaseModel):
    email: str
    code: int
    password: str


class ResetPasswordUserCode(BaseModel):
    email: str
    code: int


class ResetPassword(BaseModel):
    email: str
    token: str
    new_password: str


class SendCode(BaseModel):
    email: str


bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

models.Base.metadata.create_all(bind=engine)

oauth2_bearer = OAuth2PasswordBearer(tokenUrl="/auth/token")

router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
    responses={401: {"user": "Not authorized"}}
)


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


def send_verification_code(email_to) -> int:
    code = random.randint(111111, 999999)
    if send_email(email_from=SENDER_EMAIL,
                  email_to=email_to,
                  subject='Use the code ' + str(code),
                  html_content='<p>Use the code <strong>' + str(code) + '</strong> for your account verification.'):
        return code
    return False


def get_password_hash(password):
    return bcrypt_context.hash(password)


def verify_password(plain_password, hashed_password):
    return bcrypt_context.verify(plain_password, hashed_password)


def authenticate_user(username: str, password: str, db):
    user = db.query(models.User) \
        .filter(models.User.username == username) \
        .first()

    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(username: str, user_id: int,
                        expires_delta: Optional[timedelta] = None):
    encode = {"sub": username, "id": user_id}
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=60)
    encode.update({"exp": expire})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        if username is None or username is None:
            raise get_user_exception()
        return {"username": username, "id": user_id}
    except JWTError:
        raise get_user_exception()


@router.post("/reset/password/validate/code")
async def validate_email_code_reset_password(user_code: ResetPasswordUserCode, db: Session = Depends(get_db)):
    user_code_model = models.UserCode()
    user_code_model.email = user_code.email
    user_code_model.code = user_code.code

    validation1 = db.query(models.UserCode) \
        .filter(models.UserCode.email == user_code.email) \
        .filter(models.UserCode.code == user_code.code) \
        .filter(models.UserCode.expires_at > datetime.now()) \
        .first()

    if validation1 is not None:
        user_model = db.query(models.User) \
            .filter(models.User.email == user_code.email) \
            .first()

        user_model.is_confirmed = True

        token_expires = timedelta(minutes=15)
        token = create_access_token(user_code.email,
                                    user_code.code,
                                    expires_delta=token_expires)

        user_model.reset_password_hash = token
        user_model.reset_password_expires_at = datetime.now() + timedelta(minutes=15)

        db.add(user_model)
        db.commit()

        return {"token": token}
    else:
        raise code_invalid_or_expired()


@router.post("/reset/password")
async def reset_password(user_reset_password: ResetPassword, db: Session = Depends(get_db)):
    user_model = db.query(models.User) \
        .filter(models.User.username == user_reset_password.email) \
        .filter(models.User.reset_password_hash == user_reset_password.token) \
        .filter(models.User.reset_password_expires_at > datetime.now()) \
        .first()

    if user_model is not None:

        hash_password = get_password_hash(user_reset_password.new_password)

        user_model.hashed_password = hash_password

        db.add(user_model)
        db.commit()

        raise reset_password_success()
    else:
        raise code_invalid_or_expired()


@router.post("/validate/code")
async def validate_email_code(user_code: UserCode, db: Session = Depends(get_db)):
    user_code_model = models.UserCode()
    user_code_model.email = user_code.email
    user_code_model.code = user_code.code

    validation1 = db.query(models.UserCode) \
        .filter(models.UserCode.email == user_code.email) \
        .filter(models.UserCode.code == user_code.code) \
        .filter(models.UserCode.expires_at > datetime.now()) \
        .first()

    if validation1 is not None:
        user_model = db.query(models.User) \
            .filter(models.User.email == user_code.email) \
            .first()

        user_model.is_confirmed = True
        user_model.is_active = True

        db.add(user_model)
        db.commit()

        user = authenticate_user(user_code.email, user_code.password, db)

        if not user:
            raise token_exception()

        token_expires = timedelta(minutes=60)
        token = create_access_token(user.username,
                                    user.id,
                                    expires_delta=token_expires)
        return {"access_token": token}
    else:
        raise code_invalid_or_expired()


@router.post("/send_email/code")
async def send_email_code(send_code: SendCode, db: Session = Depends(get_db)):
    db.query(models.UserCode) \
        .filter(models.UserCode.email == send_code.email) \
        .delete()
    db.commit()

    user_code_model = models.UserCode()
    user_code_model.email = send_code.email
    code_tmp = send_verification_code(send_code.email)
    if not code_tmp:
        raise error_provider()
    user_code_model.code = code_tmp
    user_code_model.email = send_code.email
    user_code_model.expires_at = datetime.now() + timedelta(minutes=15)

    db.add(user_code_model)
    db.commit()

    raise user_code_sent()


@router.post("/create/user")
async def create_new_user(create_user: CreateUser, db: Session = Depends(get_db)):
    create_user_model = models.User()
    create_user_model.email = create_user.email
    create_user_model.username = create_user.email
    create_user_model.first_name = create_user.first_name
    create_user_model.last_name = create_user.last_name
    hash_password = get_password_hash(create_user.password)

    create_user_model.hashed_password = hash_password
    create_user_model.is_active = True

    validation1 = db.query(models.User) \
        .filter(models.User.username == create_user.email).first()

    if validation1 is not None:
        raise user_exists()

    db.add(create_user_model)
    db.commit()

    raise user_created()


@router.post("/token")
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                                 db: Session = Depends(get_db)):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise token_exception()

    if not user.is_confirmed:
        raise user_not_confirmed()

    if not user.is_active:
        raise user_not_active()

    token_expires = timedelta(minutes=60)
    token = create_access_token(user.username,
                                user.id,
                                expires_delta=token_expires)
    return {"access_token": token, "token_type": "bearer"}


# Exceptions

def user_created():
    credentials_exception = HTTPException(
        status_code=status.HTTP_200_OK,
        detail="User created successfully"
    )
    return credentials_exception


def user_is_not_active():
    credentials_exception = HTTPException(
        status_code=status.HTTP_200_OK,
        detail="Verification code sent successfully to your email!"
    )
    return credentials_exception


def user_confirmed_email():
    credentials_exception = HTTPException(
        status_code=status.HTTP_200_OK,
        detail="User confirmed email successfully"
    )
    return credentials_exception


def user_code_sent():
    credentials_exception = HTTPException(
        status_code=status.HTTP_200_OK,
        detail="code sent to email successfully"
    )
    return credentials_exception


def reset_password_success():
    credentials_exception = HTTPException(
        status_code=status.HTTP_200_OK,
        detail="Password has updated successfully"
    )
    return credentials_exception


def get_user_exception():
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    return credentials_exception


def token_exception():
    token_exception_response = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Incorrect email or password",
        headers={"WWW-Authenticate": "Bearer"},
    )
    return token_exception_response


def user_exists():
    user_exists_exception_response = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="This email is already in use",
        headers={"WWW-Authenticate": "Bearer"},
    )
    return user_exists_exception_response


def user_not_confirmed():
    user_exists_exception_response = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="User is not confirmed",
        headers={"WWW-Authenticate": "Bearer"},
    )
    return user_exists_exception_response


def user_not_active():
    user_exists_exception_response = HTTPException(
        status_code=status.HTTP_406_NOT_ACCEPTABLE,
        detail="User is not active",
        headers={"WWW-Authenticate": "Bearer"},
    )
    return user_exists_exception_response


def code_invalid_or_expired():
    code_invalid_exception_response = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="This code is invalid or expired!"
    )
    return code_invalid_exception_response


def reset_password_session_expired():
    code_invalid_exception_response = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="The session to reset your password is expired!"
    )
    return code_invalid_exception_response


def error_provider():
    code_invalid_exception_response = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Email provider with error!"
    )
    return code_invalid_exception_response


def error_token():
    code_invalid_exception_response = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token Invalid!"
    )
    return code_invalid_exception_response
