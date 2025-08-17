# routers/rules.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import crud, models, schemas
from database import get_db

router = APIRouter(
    prefix="/rules",
    tags=["Rules"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=schemas.Rule)
def create_rule(rule: schemas.RuleCreate, db: Session = Depends(get_db)):
    db_rule = crud.get_rule(db, rule_id=rule.rule_id)
    if db_rule:
        raise HTTPException(status_code=400, detail="Rule ID already registered")
    return crud.create_rule(db=db, rule=rule)

@router.get("/", response_model=List[schemas.Rule])
def read_rules(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    rules = crud.get_rules(db, skip=skip, limit=limit)
    return rules

@router.get("/{rule_id}", response_model=schemas.Rule)
def read_rule(rule_id: str, db: Session = Depends(get_db)):
    db_rule = crud.get_rule(db, rule_id=rule_id)
    if db_rule is None:
        raise HTTPException(status_code=404, detail="Rule not found")
    return db_rule