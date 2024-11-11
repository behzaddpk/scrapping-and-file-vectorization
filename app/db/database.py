from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
# from app.config.settings import DATABASE_URL
from sqlalchemy.ext.declarative import declarative_base
import logging

Base = declarative_base()

DATABASE_URL="mysql+pymysql://root:@localhost:3306/legalmaster"

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


try:
    def create_table():
        Base.metadata.create_all(bind=engine)
        logging.info('tables Created')
except:
    logging.info('tables Created')


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()