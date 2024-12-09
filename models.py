from datetime import datetime
from database import Base
from sqlalchemy import Column, Integer, String, DateTime
class history(Base):
    __tablename__ = 'history'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    result = Column(String, nullable=False)
    date_time = Column(DateTime, default=datetime.now)