from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# ---------- Reservation ----------

class ReservationBase(BaseModel):
    start_date: datetime
    end_date: datetime
    local_id: int
    price: float
    voucher_image_url: Optional[str] = None

class ReservationCreate(ReservationBase):
    pass   # user_id viene del token

class ReservationUpdate(BaseModel):
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    local_id: Optional[int] = None
    price: Optional[float] = None
    voucher_image_url: Optional[str] = None

class ReservationOut(ReservationBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True

# ---------- Report ----------

class ReportCreate(BaseModel):
    local_id: int
    title: str
    description: str

class ReportOut(BaseModel):
    id: int
    local_id: int
    title: str
    user_id: int
    description: str
    created_at: datetime

    class Config:
        orm_mode = True
