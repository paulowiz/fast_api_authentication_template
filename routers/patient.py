import sys

sys.path.append("..")

from typing import Optional
from fastapi import Depends, HTTPException, APIRouter
import models
from database import engine, SessionLocal, select, func, extract
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

router = APIRouter(
    prefix="/patient",
    tags=["Patient"],
    responses={404: {"description": "Not found"}}
)

# models.Base.metadata.create_all(bind=engine)

class Patient(BaseModel):
    first_name: str
    last_name: str
    gender: str
    patient_number: str
    birth_date: str
    creator_id: int


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@router.get("/")
async def read_all(page_num: int = 1, page_size: int = 10, db: Session = Depends(get_db)):
    start = (page_num - 1) * page_size
    end = start + page_size
    data = db.query(models.Patient)
    data_length = db.query(models.Patient).count()
    response = {
        "total": data_length,
        "page_size": page_size,
        "total_pages": round(data_length / page_size),
        "current_page": page_num,
        "data": data[start:end],
    }
    return response


@router.get("/{patient_id}")
async def read_patient(patient_id: int,
                       db: Session = Depends(get_db)):
    from datetime import datetime
    patient_model = db.query(models.Patient,
                             (func.round((func.datediff(datetime.now(), models.Patient.birth_date) / 365), 0)).label(
                                 "age")) \
        .filter(models.Patient.id == patient_id) \
        .first()

    if patient_model is None:
        raise http_exception()

    return patient_model


@router.post("/")
async def create_patient(patient: Patient,
                         db: Session = Depends(get_db)):
    patient_model = models.Patient()
    patient_model.first_name = patient.first_name
    patient_model.last_name = patient.last_name
    patient_model.patient_number = patient.patient_number
    patient_model.gender = patient.gender
    patient_model.birth_date = patient.birth_date
    patient_model.creator_id = patient.creator_id

    db.add(patient_model)
    db.commit()

    return successful_response(201)


@router.put("/{patient_id}")
async def update_patient(patient_id: int,
                         patient: Patient,
                         db: Session = Depends(get_db)):
    patient_model = db.query(models.Patient) \
        .filter(models.Patient.id == patient_id) \
        .first()

    if patient_model is None:
        raise http_exception()

    patient_model.first_name = patient_model.first_name if validate_field(
        patient.first_name) else patient.first_name
    patient_model.last_name = patient_model.last_name if validate_field(
        patient.last_name) else patient.last_name
    patient_model.gender = patient_model.gender if validate_field(
        patient.gender) else patient.gender
    patient_model.patient_number = patient_model.patient_number if validate_field(
        patient.patient_number) else patient.patient_number
    patient_model.birth_date = patient_model.birth_date if validate_field(
        patient.birth_date) else patient.birth_date
    patient_model.creator_id = patient_model.creator_id if validate_field(
        patient.creator_id) else patient.creator_id

    db.add(patient_model)
    db.commit()

    return successful_response(200)


@router.delete("/{patient_id}")
async def delete_patient(patient_id: int,
                         db: Session = Depends(get_db)):
    patient_model = db.query(models.Patient) \
        .filter(models.Patient.id == patient_id) \
        .first()

    if patient_model is None:
        raise http_exception()

    db.query(models.Patient) \
        .filter(models.Patient.id == patient_id) \
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
