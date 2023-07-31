import sys

sys.path.append("..")

from typing import Optional
from fastapi import Depends, HTTPException, APIRouter
import models
from database import engine, SessionLocal, select
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

router = APIRouter(
    prefix="/learning_session",
    tags=["Learning Session"],
    responses={404: {"description": "Not found"}}
)


# models.Base.metadata.create_all(bind=engine)

class LearningSession(BaseModel):
    code: str
    supervisor_id: int


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@router.get("/")
async def read_all(db: Session = Depends(get_db)):
    return db.query(models.LearningSession).all()


@router.get("/{learning_session_id}")
async def read_learning_session(learning_session_id: int,
                                db: Session = Depends(get_db)):
    learning_session_model = db.query(models.LearningSession) \
        .filter(models.LearningSession.id == learning_session_id) \
        .first()

    if learning_session_model is None:
        raise http_exception()

    return learning_session_model


@router.post("/")
async def create_learning_session(learningSession: LearningSession,
                                  db: Session = Depends(get_db)):
    learning_session_model = models.LearningSession()
    learning_session_model.code = learningSession.code
    learning_session_model.supervisor_id = learningSession.supervisor_id

    db.add(learning_session_model)
    db.commit()

    return successful_response(201)


@router.put("/{learning_session_id}")
async def update_learning_session(learning_session_id: int,
                                  learning_session: LearningSession,
                                  db: Session = Depends(get_db)):
    learning_session_model = db.query(models.LearningSession) \
        .filter(models.LearningSession.id == learning_session_id) \
        .first()

    if learning_session_model is None:
        raise http_exception()

    learning_session_model.name = learning_session_model.code if validate_field(
        learning_session.code) else learning_session.code
    learning_session_model.supervisor_id = learning_session_model.supervisor_id if validate_field(
        learning_session.supervisor_id) else learning_session.supervisor_id

    db.add(learning_session_model)
    db.commit()

    return successful_response(200)


@router.delete("/{learning_session_id}")
async def delete_learning_session(learning_session_id: int,
                                  db: Session = Depends(get_db)):
    industry_model = db.query(models.LearningSession) \
        .filter(models.LearningSession.id == learning_session_id) \
        .first()

    if industry_model is None:
        raise http_exception()

    db.query(models.LearningSession) \
        .filter(models.LearningSession.id == learning_session_id) \
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
