from datetime import datetime
from sqlalchemy import Column, Integer, Float, Text, DateTime
from .database import Base

class Reservation(Base):
    __tablename__ = "reservations"

    id = Column(Integer, primary_key=True, index=True)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    user_id = Column(Integer, nullable=False, index=True)  # id de users (IAM)
    local_id = Column(Integer, nullable=False, index=True) # id de locals (otro ms)
    price = Column(Float, nullable=False)
    voucher_image_url = Column(Text, nullable=True)

class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    local_id = Column(Integer, nullable=False, index=True)
    title = Column(Text, nullable=False)
    user_id = Column(Integer, nullable=False, index=True)
    description = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
