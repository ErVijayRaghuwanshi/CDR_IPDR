# routers/target_groups.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import crud, models, schemas
from database import get_db

router = APIRouter(
    prefix="/target-groups",
    tags=["Target Groups"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=schemas.TargetGroup, status_code=status.HTTP_201_CREATED)
def create_target_group(group: schemas.TargetGroupCreate, db: Session = Depends(get_db)):
    db_group = crud.get_target_group(db, group_id=group.group_id)
    if db_group:
        raise HTTPException(status_code=400, detail="Group ID already exists")
    return crud.create_target_group(db=db, group=group)

@router.get("/", response_model=List[schemas.TargetGroupBase]) # Use Base schema for list view
def read_target_groups(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    groups = crud.get_target_groups(db, skip=skip, limit=limit)
    return groups

@router.get("/{group_id}", response_model=schemas.TargetGroup)
def read_target_group(group_id: str, db: Session = Depends(get_db)):
    db_group = crud.get_target_group(db, group_id=group_id)
    if db_group is None:
        raise HTTPException(status_code=404, detail="Target group not found")
    return db_group

# --- Relationships ---

@router.post("/{group_id}/targets/{target_id}", response_model=schemas.TargetGroup)
def add_target_to_group(group_id: str, target_id: str, db: Session = Depends(get_db)):
    updated_group = crud.add_target_to_group(db, group_id, target_id)
    if updated_group is None:
        raise HTTPException(status_code=404, detail="Group or Target not found")
    return read_target_group(group_id, db) # Re-fetch to get updated nested objects

@router.delete("/{group_id}/targets/{target_id}", response_model=schemas.TargetGroup)
def remove_target_from_group(group_id: str, target_id: str, db: Session = Depends(get_db)):
    updated_group = crud.remove_target_from_group(db, group_id, target_id)
    if updated_group is None:
        raise HTTPException(status_code=404, detail="Group or Target not found, or Target not in Group")
    return read_target_group(group_id, db)

@router.post("/{group_id}/rules", response_model=schemas.TargetGroupRuleResponse, status_code=status.HTTP_201_CREATED)
def add_rule_to_group(group_id: str, rule_data: schemas.RuleToGroupCreate, db: Session = Depends(get_db)):
    new_group_rule = crud.add_rule_to_group(db, group_id, rule_data)
    if new_group_rule is None:
        raise HTTPException(status_code=404, detail="Group or Rule not found")
    # Manually load the relationship for the response
    db.refresh(new_group_rule, attribute_names=['rule_details'])
    return new_group_rule

@router.delete("/rules/{group_rule_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_rule_from_group(group_rule_id: int, db: Session = Depends(get_db)):
    success = crud.remove_rule_from_group(db, group_rule_id)
    if not success:
        raise HTTPException(status_code=404, detail="Group-Rule link not found")
    return