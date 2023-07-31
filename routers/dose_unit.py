import sys

sys.path.append("..")

from typing import Optional
from fastapi import Depends, HTTPException, APIRouter
import models
from database import engine, SessionLocal, select
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field


router = APIRouter(
    prefix="/dose_unit",
    tags=["DoseUnit"],
    responses={404: {"description": "Not found"}}
)


# models.Base.metadata.create_all(bind=engine)

class DoseUnit(BaseModel):
    description: str
    category: str
    code: str

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@router.get("/")
async def read_all(db: Session = Depends(get_db)):
    return db.query(models.DoseUnit).all()


@router.get("/{dose_unit_id}")
async def read_dose_unit(dose_unit_id: int,
                                db: Session = Depends(get_db)):
    dose_unit_model = db.query(models.DoseUnit) \
        .filter(models.DoseUnit.id == dose_unit_id) \
        .first()

    if dose_unit_model is None:
        raise http_exception()

    return dose_unit_id


@router.post("/")
async def create_dose_unit(dose_unit: DoseUnit,
                                  db: Session = Depends(get_db)):
    dose_unit_model = models.DoseUnit()
    dose_unit_model.description = dose_unit.description
    dose_unit_model.code = dose_unit.code
    dose_unit_model.category = dose_unit.category
    db.add(dose_unit_model)
    db.commit()

    return successful_response(201)


@router.put("/{dose_unit_id}")
async def update_dose_unit(dose_unit_id: int,
                                  dose_unit: DoseUnit,
                                  db: Session = Depends(get_db)):
    dose_unit_model = db.query(models.DoseUnit) \
        .filter(models.DoseUnit.id == dose_unit_id) \
        .first()

    if dose_unit_model is None:
        raise http_exception()

    dose_unit_model.description = dose_unit_model.description if validate_field(
        dose_unit.description) else dose_unit.description
    dose_unit_model.code = dose_unit_model.code if validate_field(
        dose_unit.code) else dose_unit.code
    dose_unit_model.category = dose_unit_model.category if validate_field(
        dose_unit.category) else dose_unit.category

    db.add(dose_unit_model)
    db.commit()

    return successful_response(200)


@router.delete("/{dose_unit_id}")
async def delete_dose_unit(dose_unit_id: int,
                                  db: Session = Depends(get_db)):
    dose_unit_model = db.query(models.DoseUnit) \
        .filter(models.DoseUnit.id == dose_unit_id) \
        .first()

    if dose_unit_model is None:
        raise http_exception()

    db.query(models.DoseUnit) \
        .filter(models.DoseUnit.id == dose_unit_id) \
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
