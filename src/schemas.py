# schemas.py
import enum
from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime


class StatusEnum(enum.Enum):
    active = "active"
    inactive = "inactive"

class TargetTypeEnum(enum.Enum):
    MOBILE_NUMBER = "MOBILE_NUMBER"
    IMEI = "IMEI"
    IP_ADDRESS = "IP_ADDRESS"

# ====================================
# Target Schemas
# ====================================
class TargetBase(BaseModel):
    target_id: str
    target_type: TargetTypeEnum = TargetTypeEnum.MOBILE_NUMBER
    identifier: str
    status: StatusEnum = StatusEnum.active
    associated_imsi: Optional[str] = None
    associated_imei: Optional[str] = None
    associated_bts: Optional[str] = None
    description: Optional[str] = None

class TargetCreate(BaseModel):
    target_type: TargetTypeEnum = TargetTypeEnum.MOBILE_NUMBER
    identifier: str
    status: StatusEnum = StatusEnum.active
    associated_imsi: Optional[str] = ''
    associated_imei: Optional[str] = ''
    associated_bts: Optional[str] = ''
    description: Optional[str] = ''


class Target(TargetBase):
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

# ====================================
# Rule Schemas
# ====================================
class RuleBase(BaseModel):
    rule_id: str
    name: str
    required_fields: List[str]
    description: Optional[str] = None
    version: Optional[str] = None
    rule_type: Optional[str] = None
    data_source: Optional[str] = None
    default_params: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    sql_template: Optional[str] = None

class RuleCreate(RuleBase):
    pass

class Rule(RuleBase):
    created_at: datetime
    modified_at: datetime
    model_config = ConfigDict(from_attributes=True)

# ====================================
# Target Group Schemas
# ====================================
class TargetGroupBase(BaseModel):
    group_id: str
    name: str
    status: str
    description: Optional[str] = None
    created_by: Optional[str] = None

class TargetGroupCreate(TargetGroupBase):
    pass

# Schemas for response models to show nested relationships
class TargetGroupRuleResponse(BaseModel):
    group_rule_id: int
    rule_id: str
    custom_params: Optional[Dict[str, Any]] = None
    added_at: datetime
    rule_details: Rule  # Nested rule details
    model_config = ConfigDict(from_attributes=True)

class TargetGroup(TargetGroupBase):
    created_at: datetime
    targets: List[Target] = []
    rules: List[TargetGroupRuleResponse] = []
    model_config = ConfigDict(from_attributes=True)

# Schema for adding a rule to a group
class RuleToGroupCreate(BaseModel):
    rule_id: str
    custom_params: Optional[Dict[str, Any]] = None