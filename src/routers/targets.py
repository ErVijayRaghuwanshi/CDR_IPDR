# routers/targets.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import crud, models, schemas
from database import get_db

router = APIRouter(
    prefix="/targets",
    tags=["Targets"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=schemas.Target)
def create_target(target: schemas.TargetCreate, db: Session = Depends(get_db)):
    db_target = crud.get_target(db, target_id=target.target_id)
    if db_target:
        raise HTTPException(status_code=400, detail="Target ID already registered")
    return crud.create_target(db=db, target=target)

@router.get("/", response_model=List[schemas.Target])
def read_targets(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    targets = crud.get_targets(db, skip=skip, limit=limit)
    return targets

@router.get("/{target_id}", response_model=schemas.Target)
def read_target(target_id: str, db: Session = Depends(get_db)):
    db_target = crud.get_target(db, target_id=target_id)
    if db_target is None:
        raise HTTPException(status_code=404, detail="Target not found")
    return db_target