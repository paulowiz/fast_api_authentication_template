from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime, timedelta


class User(Base):
    __tablename__ = "user"
    __table_args__ = {"extend_existing": True}
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    user_role_id = Column(Integer, default=2)
    first_name = Column(String)
    last_name = Column(String)
    hashed_password = Column(String)
    reset_password_expires_at = Column(DateTime)
    reset_password_hash = Column(String)
    is_active = Column(Boolean, default=True)
    is_confirmed = Column(Boolean, default=False)
    img_path = Column(String)
    updated_at = Column(DateTime, default=datetime.now)


class UserCode(Base):
    __tablename__ = "user_code"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String)
    code = Column(Integer)
    expires_at = Column(DateTime)