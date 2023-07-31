import sys

sys.path.append("..")

from typing import Optional
from fastapi import Depends, HTTPException, APIRouter
import models
from database import engine, SessionLocal, select
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field


router = APIRouter(
    prefix="/grade",
    tags=["Grade"],
    responses={404: {"description": "Not found"}}
)


# models.Base.metadata.create_all(bind=engine)

class Grade(BaseModel):
    description: str

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@router.get("/")
async def read_all(db: Session = Depends(get_db)):
    return db.query(models.Grade).all()


@router.get("/{grade_id}")
async def read_grade(grade_id: int,
                                db: Session = Depends(get_db)):
    grade_model = db.query(models.Grade) \
        .filter(models.Grade.id == grade_id) \
        .first()

    if grade_model is None:
        raise http_exception()

    return grade_model


@router.post("/")
async def create_grade(grade: Grade,
                                  db: Session = Depends(get_db)):
    grade_model = models.Grade()
    grade_model.description = grade.description

    db.add(grade_model)
    db.commit()

    return successful_response(201)


@router.put("/{grade_id}")
async def update_grade(grade_id: int,
                                  grade: Grade,
                                  db: Session = Depends(get_db)):
    grade_model = db.query(models.Grade) \
        .filter(models.Grade.id == grade_id) \
        .first()

    if grade_model is None:
        raise http_exception()

    grade_model.description = grade_model.description if validate_field(
        grade.description) else grade.description

    db.add(grade_model)
    db.commit()

    return successful_response(200)


@router.delete("/{grade_id}")
async def delete_grade(grade_id: int,
                                  db: Session = Depends(get_db)):
    grade_model = db.query(models.Grade) \
        .filter(models.Grade.id == grade_id) \
        .first()

    if grade_model is None:
        raise http_exception()

    db.query(models.Grade) \
        .filter(models.Grade.id == grade_id) \
        .delete()

    db.commit()

    return successful_response(200)


def validate_field(field):
    if field is None:
        return True
    else:
        return False


# Exceptions
def successful_response(status_code: int):
    return {
        'status': status_code,
        'transaction': 'Successful'
    }


def http_exception():    return HTTPException(status_code=404, detail="Industry not found")
