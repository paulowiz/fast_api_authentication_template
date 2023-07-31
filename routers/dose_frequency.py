import sys

sys.path.append("..")

from typing import Optional
from fastapi import Depends, HTTPException, APIRouter
import models
from database import engine, SessionLocal, select
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field


router = APIRouter(
    prefix="/dose_frequency",
    tags=["DoseFrequency"],
    responses={404: {"description": "Not found"}}
)


# models.Base.metadata.create_all(bind=engine)

class DoseFrequency(BaseModel):
    description: str
    code: str

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@router.get("/")
async def read_all(db: Session = Depends(get_db)):
    return db.query(models.DoseFrequency).all()


@router.get("/{dose_frequency_id}")
async def read_dose_frequency(dose_frequency_id: int,
                                db: Session = Depends(get_db)):
    dose_frequency_model = db.query(models.DoseFrequency) \
        .filter(models.DoseFrequency.id == dose_frequency_id) \
        .first()

    if dose_frequency_model is None:
        raise http_exception()

    return dose_frequency_id


@router.post("/")
async def create_dose_frequency(dose_frequency: DoseFrequency,
                                  db: Session = Depends(get_db)):
    dose_frequency_model = models.DoseFrequency()
    dose_frequency_model.description = dose_frequency.description
    dose_frequency_model.code = dose_frequency.code

    db.add(dose_frequency_model)
    db.commit()

    return successful_response(201)


@router.put("/{dose_frequency_id}")
async def update_dose_frequency(dose_frequency_id: int,
                                  dose_frequency: DoseFrequency,
                                  db: Session = Depends(get_db)):
    dose_frequency_model = db.query(models.DoseFrequency) \
        .filter(models.DoseFrequency.id == dose_frequency_id) \
        .first()

    if dose_frequency_model is None:
        raise http_exception()

    dose_frequency_model.description = dose_frequency_model.description if validate_field(
        dose_frequency.description) else dose_frequency.description
    dose_frequency_model.code = dose_frequency_model.code if validate_field(
        dose_frequency.code) else dose_frequency.code

    db.add(dose_frequency_model)
    db.commit()

    return successful_response(200)


@router.delete("/{dose_frequency_id}")
async def delete_dose_frequency(dose_frequency_id: int,
                                  db: Session = Depends(get_db)):
    dose_frequency_model = db.query(models.DoseFrequency) \
        .filter(models.DoseFrequency.id == dose_frequency_id) \
        .first()

    if dose_frequency_model is None:
        raise http_exception()

    db.query(models.DoseFrequency) \
        .filter(models.DoseFrequency.id == dose_frequency_id) \
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
