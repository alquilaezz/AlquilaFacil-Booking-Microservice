from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas
from ..deps import get_db, get_current_user, CurrentUser

router = APIRouter(prefix="/api/v1/reservation", tags=["Reservation"])

# --- Helpers ---

def _check_reservation_access(reservation: models.Reservation, current_user: CurrentUser):
    if reservation.user_id != current_user.id and current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Not enough permissions")

# --- POST /api/v1/reservation ---

@router.post("", response_model=schemas.ReservationOut, status_code=status.HTTP_201_CREATED)
def create_reservation(
    payload: schemas.ReservationCreate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    if payload.end_date <= payload.start_date:
        raise HTTPException(status_code=400, detail="end_date must be after start_date")

    reservation = models.Reservation(
        start_date=payload.start_date,
        end_date=payload.end_date,
        local_id=payload.local_id,
        price=payload.price,
        voucher_image_url=payload.voucher_image_url,
        user_id=current_user.id,
    )
    db.add(reservation)
    db.commit()
    db.refresh(reservation)
    return reservation

# --- PUT /api/v1/reservation/{id} ---

@router.put("/{reservation_id}", response_model=schemas.ReservationOut)
def update_reservation(
    reservation_id: int,
    payload: schemas.ReservationUpdate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    reservation = db.query(models.Reservation).filter(models.Reservation.id == reservation_id).first()
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")

    _check_reservation_access(reservation, current_user)

    data = payload.dict(exclude_unset=True)
    for field, value in data.items():
        setattr(reservation, field, value)

    if reservation.end_date <= reservation.start_date:
        raise HTTPException(status_code=400, detail="end_date must be after start_date")

    db.add(reservation)
    db.commit()
    db.refresh(reservation)
    return reservation

# --- DELETE /api/v1/reservation/{id} ---

@router.delete("/{reservation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_reservation(
    reservation_id: int,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    reservation = db.query(models.Reservation).filter(models.Reservation.id == reservation_id).first()
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")

    _check_reservation_access(reservation, current_user)

    db.delete(reservation)
    db.commit()
    return

# --- GET /api/v1/reservation/by-user-id/{userId} ---

@router.get("/by-user-id/{user_id}", response_model=List[schemas.ReservationOut])
def get_reservations_by_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    if current_user.id != user_id and current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Not enough permissions")

    reservations = (
        db.query(models.Reservation)
        .filter(models.Reservation.user_id == user_id)
        .order_by(models.Reservation.start_date.desc())
        .all()
    )
    return reservations

# --- GET /api/v1/reservation/reservation-user-details/{userId} ---

@router.get("/reservation-user-details/{user_id}", response_model=List[schemas.ReservationOut])
def get_reservation_user_details(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    Por ahora lo dejamos igual que by-user-id.
    Más adelante puedes enriquecer con datos del local llamando al microservicio de locals.
    """
    return get_reservations_by_user(user_id=user_id, db=db, current_user=current_user)

# --- GET /api/v1/reservation/by-start-date/{startDate} ---

@router.get("/by-start-date/{start_date}", response_model=List[schemas.ReservationOut])
def get_reservations_by_start_date(
    start_date: datetime,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    start_date en formato ISO, por ejemplo: 2024-01-01T00:00:00
    Devuelve reservas del usuario actual con start_date >= start_date.
    """
    reservations = (
        db.query(models.Reservation)
        .filter(
            models.Reservation.user_id == current_user.id,
            models.Reservation.start_date >= start_date,
        )
        .order_by(models.Reservation.start_date.asc())
        .all()
    )
    return reservations

# --- GET /api/v1/reservation/by-end-date/{endDate} ---

@router.get("/by-end-date/{end_date}", response_model=List[schemas.ReservationOut])
def get_reservations_by_end_date(
    end_date: datetime,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    end_date en formato ISO, por ejemplo: 2024-01-31T23:59:59
    Devuelve reservas del usuario actual con end_date <= end_date.
    """
    reservations = (
        db.query(models.Reservation)
        .filter(
            models.Reservation.user_id == current_user.id,
            models.Reservation.end_date <= end_date,
        )
        .order_by(models.Reservation.end_date.asc())
        .all()
    )
    return reservations
