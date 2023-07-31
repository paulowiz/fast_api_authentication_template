import sys

sys.path.append("..")

from typing import Optional
from fastapi import Depends, HTTPException, APIRouter
import models
from database import engine, SessionLocal, select
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

router = APIRouter(
    prefix="/drug",
    tags=["Drug"],
    responses={404: {"description": "Not found"}}
)


# models.Base.metadata.create_all(bind=engine)

class Drug(BaseModel):
    description: str
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
    data = db.query(models.Drug)
    data_length = db.query(models.Drug).count()
    response = {
        "total": data_length,
        "page_size": page_size,
        "total_pages": round(data_length / page_size),
        "current_page": page_num,
        "data": data[start:end],
    }
    return response


@router.get("/{text}")
async def read_all_by_text(text: str = 'A', page_num: int = 1, page_size: int = 10, db: Session = Depends(get_db)):
    search_text = text + '%'
    start = (page_num - 1) * page_size
    end = start + page_size
    data = db.query(models.Drug) \
           .filter(models.Drug.description.like(search_text)).all()
    data_length = db.query(models.Drug).count()
    response = {
        "total": data_length,
        "page_size": page_size,
        "total_pages": round(data_length / page_size),
        "current_page": page_num,
        "data": data[start:end],
    }
    return response


@router.get("/{drug_id}")
async def read_drug(drug_id: int,
                    db: Session = Depends(get_db)):
    drug_model = db.query(models.Drug) \
        .filter(models.Drug.id == drug_id) \
        .first()

    if drug_model is None:
        raise http_exception()

    return drug_model


@router.post("/")
async def create_drug(drug: Drug,
                      db: Session = Depends(get_db)):
    drug_model = models.Drug()
    drug_model.description = drug.description
    drug_model.creator_id = drug.creator_id

    db.add(drug_model)
    db.commit()

    return successful_response(201)


@router.put("/{drug_id}")
async def update_drug(drug_id: int,
                      drug: Drug,
                      db: Session = Depends(get_db)):
    drug_model = db.query(models.Drug) \
        .filter(models.Drug.id == drug_id) \
        .first()

    if drug_model is None:
        raise http_exception()

    drug_model.description = drug_model.description if validate_field(
        drug.description) else drug.description
    drug_model.creator_id = drug_model.creator_id if validate_field(
        drug.creator_id) else drug.creator_id

    db.add(drug_model)
    db.commit()

    return successful_response(200)


@router.delete("/{drug_id}")
async def delete_drug(drug_id: int,
                      db: Session = Depends(get_db)):
    drug_model = db.query(models.Drug) \
        .filter(models.Drug.id == drug_id) \
        .first()

    if drug_model is None:
        raise http_exception()

    db.query(models.Drug) \
        .filter(models.Drug.id == drug_id) \
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
