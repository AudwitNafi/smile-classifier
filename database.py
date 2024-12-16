from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# SQLALCHEMY_DATABASE_URL = 'sqlite:///./history.db'
SQLALCHEMY_DATABASE_URL = 'mysql+pymysql://root:1234@mysql_container:3306/history'

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit =  False, autoflush=False, bind=engine)

Base = declarative_base()