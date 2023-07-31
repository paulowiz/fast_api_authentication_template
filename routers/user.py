import sys

sys.path.append("../..")

from typing import Optional
from fastapi import Depends, HTTPException, APIRouter, File, UploadFile, status
import models
from database import engine, SessionLocal, select
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from .auth import get_current_user, get_user_exception

router = APIRouter(
    prefix="/user",
    tags=["User"],
    responses={404: {"description": "Not found"}}
)

# models.Base.metadata.create_all(bind=engine)


class User(BaseModel):
    first_name: str
    last_name: Optional[str]


class Password(BaseModel):
    current_password: str
    new_password: str


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@router.get("")
async def read_current_user(db: Session = Depends(get_db),
                            user: dict = Depends(get_current_user)):
    if user is None:
        raise get_user_exception()

    return db.query(models.User.email,
                    models.User.first_name,
                    models.User.last_name,
                    models.User.is_active,
                    models.User.is_confirmed,
                    models.User.img_path
                    ) \
        .filter(models.User.id == user['id']) \
        .first()


@router.put("")
async def update_current_user_profile(
        user_data: User,
        user: dict = Depends(get_current_user),
        db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()

    user_model = db.query(models.User) \
        .filter(models.User.id == user['id']) \
        .first()

    user_model.first_name = user_model.first_name if validate_field(user_data.first_name) else user_data.first_name
    user_model.last_name = user_model.last_name if validate_field(user_data.last_name) else user_data.last_name

    db.add(user_model)
    db.commit()

    return successful_response(200)


@router.delete("")
async def delete_account(
        user: dict = Depends(get_current_user),
        db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()

    user_model = db.query(models.User) \
        .filter(models.User.id == user['id']) \
        .first()

    user_model.is_active = False

    db.add(user_model)

    db.commit()

    return successful_response(200)


def validate_field(field):
    if field is None:
        return True
    else:
        return False


def successful_response(status_code: int):
    return {
        'status': status_code,
        'transaction': 'Successful'
    }


def wrong_format():
    wrong_format_exception_response = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Only jpg,png,gif and jpeg are supported!",
        headers={"WWW-Authenticate": "Bearer"},
    )
    return wrong_format_exception_response


def http_exception():    return HTTPException(status_code=404, detail="Industry not found")
