from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import select, func, select, column, case, literal_column
from secret import get_secret


def create_mysql_connection_string(user, password, host, database):
    port = 3306  # Change this if your MySQL server is running on a different port

    connection_string = f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"
    return connection_string


JSON_SECRET = get_secret()

SQLALCHEMY_DATABASE_URL = create_mysql_connection_string(JSON_SECRET['mysql']['user'],
                                                         JSON_SECRET['mysql']['password'],
                                                         JSON_SECRET['mysql']['host'],
                                                         JSON_SECRET['mysql']['database'])

engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
