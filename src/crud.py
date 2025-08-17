# crud.py
from sqlalchemy.orm import Session, joinedload
import models, schemas
from typing import List, Optional, Dict, Any

# ====================================
# Target CRUD
# ====================================
def get_target(db: Session, target_id: str):
    return db.query(models.Target).filter(models.Target.target_id == target_id).first()

def get_targets(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Target).offset(skip).limit(limit).all()

def create_target(db: Session, target: schemas.TargetCreate):
    db_target = models.Target(**target.dict())
    db.add(db_target)
    db.commit()
    db.refresh(db_target)
    return db_target

# ====================================
# Rule CRUD
# ====================================
def get_rule(db: Session, rule_id: str):
    return db.query(models.Rule).filter(models.Rule.rule_id == rule_id).first()

def get_rules(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Rule).offset(skip).limit(limit).all()

def create_rule(db: Session, rule: schemas.RuleCreate):
    db_rule = models.Rule(**rule.dict())
    db.add(db_rule)
    db.commit()
    db.refresh(db_rule)
    return db_rule

# ====================================
# Target Group CRUD
# ====================================
def get_target_group(db: Session, group_id: str):
    return db.query(models.TargetGroup).options(
        joinedload(models.TargetGroup.targets),
        joinedload(models.TargetGroup.rules).joinedload(models.TargetGroupRule.rule_details)
    ).filter(models.TargetGroup.group_id == group_id).first()

def get_target_groups(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.TargetGroup).offset(skip).limit(limit).all()

def create_target_group(db: Session, group: schemas.TargetGroupCreate):
    db_group = models.TargetGroup(**group.dict())
    db.add(db_group)
    db.commit()
    db.refresh(db_group)
    return db_group

# ====================================
# Target Group Relationship Management
# ====================================
def add_target_to_group(db: Session, group_id: str, target_id: str):
    group = db.query(models.TargetGroup).filter(models.TargetGroup.group_id == group_id).first()
    target = db.query(models.Target).filter(models.Target.target_id == target_id).first()
    if group and target:
        group.targets.append(target)
        db.commit()
        db.refresh(group)
    return group

def remove_target_from_group(db: Session, group_id: str, target_id: str):
    group = db.query(models.TargetGroup).options(joinedload(models.TargetGroup.targets)).filter(models.TargetGroup.group_id == group_id).first()
    target = db.query(models.Target).filter(models.Target.target_id == target_id).first()
    if group and target and target in group.targets:
        group.targets.remove(target)
        db.commit()
        db.refresh(group)
    return group
    
def add_rule_to_group(db: Session, group_id: str, rule_data: schemas.RuleToGroupCreate):
    group = db.query(models.TargetGroup).filter(models.TargetGroup.group_id == group_id).first()
    rule = db.query(models.Rule).filter(models.Rule.rule_id == rule_data.rule_id).first()
    if not group or not rule:
        return None # Or raise an exception
    
    db_group_rule = models.TargetGroupRule(
        group_id=group_id,
        rule_id=rule_data.rule_id,
        custom_params=rule_data.custom_params
    )
    db.add(db_group_rule)
    db.commit()
    db.refresh(db_group_rule)
    return db_group_rule

def remove_rule_from_group(db: Session, group_rule_id: int):
    db_group_rule = db.query(models.TargetGroupRule).filter(models.TargetGroupRule.group_rule_id == group_rule_id).first()
    if db_group_rule:
        db.delete(db_group_rule)
        db.commit()
        return True
    return False