import sys

sys.path.append("..")

from typing import Optional
from fastapi import Depends, HTTPException, APIRouter
import models
from database import engine, SessionLocal, select
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field


router = APIRouter(
    prefix="/route_of_administration",
    tags=["Route Of Administration"],
    responses={404: {"description": "Not found"}}
)


# models.Base.metadata.create_all(bind=engine)

class RouteOfAdministration(BaseModel):
    description: str
    sub_category: str
    category: str
    sub_category: str

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@router.get("/")
async def read_all(db: Session = Depends(get_db)):
    return db.query(models.RouteOfAdministration).all()


@router.get("/{route_of_administration_id}")
async def read_route_of_administration(route_of_administration_id: int,
                                db: Session = Depends(get_db)):
    route_of_administration_model = db.query(models.RouteOfAdministration) \
        .filter(models.RouteOfAdministration.id== route_of_administration_id) \
        .first()

    if route_of_administration_model is None:
        raise http_exception()

    return route_of_administration_model


@router.post("/")
async def create_route_of_administration(route_of_administration: RouteOfAdministration,
                                  db: Session = Depends(get_db)):
    route_of_administration_model = models.RouteOfAdministration()
    route_of_administration_model.description = route_of_administration.description
    route_of_administration_model.sub_category = route_of_administration.sub_category
    route_of_administration_model.category = route_of_administration.category
    db.add(route_of_administration_model)
    db.commit()

    return successful_response(201)


@router.put("/{route_of_administration_id}")
async def update_route_of_administration(route_of_administration_id: int,
                                  route_of_administration: RouteOfAdministration,
                                  db: Session = Depends(get_db)):
    route_of_administration_model = db.query(models.RouteOfAdministration) \
        .filter(models.RouteOfAdministration.id == route_of_administration_id) \
        .first()

    if route_of_administration_model is None:
        raise http_exception()

    route_of_administration_model.description = route_of_administration_model.description if validate_field(
        route_of_administration.description) else route_of_administration.description
    route_of_administration_model.sub_category = route_of_administration_model.sub_category if validate_field(
        route_of_administration.sub_category) else route_of_administration.sub_category
    route_of_administration_model.category = route_of_administration_model.category if validate_field(
        route_of_administration.category) else route_of_administration.category

    db.add(route_of_administration_model)
    db.commit()

    return successful_response(200)


@router.delete("/{route_of_administration_id}")
async def delete_route_of_administration(route_of_administration_id: int,
                                  db: Session = Depends(get_db)):
    route_of_administration_model = db.query(models.RouteOfAdministration) \
        .filter(models.RouteOfAdministration.id == route_of_administration_id) \
        .first()

    if route_of_administration_model is None:
        raise http_exception()

    db.query(models.RouteOfAdministration) \
        .filter(models.RouteOfAdministration.id == route_of_administration_id) \
        .delete()

    db.commit()

    return successful_response(200)


def validate_field(field):
    if field is None:
        return True
    else:
        return False


# Exceptions
def successful_response(status_sub_category: int):
    return {
        'status': status_sub_category,
        'transaction': 'Successful'
    }


def http_exception():    return HTTPException(status_sub_category=404, detail="Industry not found")
