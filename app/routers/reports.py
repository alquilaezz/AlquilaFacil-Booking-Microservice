from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas
from ..deps import get_db, get_current_user, CurrentUser

router = APIRouter(prefix="/api/v1/report", tags=["Report"])

# --- Helpers ---

def _check_report_access(report: models.Report, current_user: CurrentUser):
    if report.user_id != current_user.id and current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Not enough permissions")

# --- POST /api/v1/report ---

@router.post("", response_model=schemas.ReportOut, status_code=status.HTTP_201_CREATED)
def create_report(
    payload: schemas.ReportCreate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    report = models.Report(
        local_id=payload.local_id,
        title=payload.title,
        description=payload.description,
        user_id=current_user.id,
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report

# --- GET /api/v1/report/get-by-user-id/{userId} ---

@router.get("/get-by-user-id/{user_id}", response_model=List[schemas.ReportOut])
def get_reports_by_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    if current_user.id != user_id and current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Not enough permissions")

    reports = (
        db.query(models.Report)
        .filter(models.Report.user_id == user_id)
        .order_by(models.Report.created_at.desc())
        .all()
    )
    return reports

# --- GET /api/v1/report/get-by-local-id/{localId} ---

@router.get("/get-by-local-id/{local_id}", response_model=List[schemas.ReportOut])
def get_reports_by_local(
    local_id: int,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    # cualquier usuario autenticado puede ver reports de un local;
    # si quieres restringir, aquí sería el lugar
    reports = (
        db.query(models.Report)
        .filter(models.Report.local_id == local_id)
        .order_by(models.Report.created_at.desc())
        .all()
    )
    return reports

# --- DELETE /api/v1/report/{reportId} ---

@router.delete("/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    report = db.query(models.Report).filter(models.Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    _check_report_access(report, current_user)

    db.delete(report)
    db.commit()
    return
