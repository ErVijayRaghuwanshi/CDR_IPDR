# models.py
from sqlalchemy import (Column, String, Table, Text, TIMESTAMP, ForeignKey,
                        Integer, create_engine)
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from sqlalchemy.orm import relationship, sessionmaker
from database import Base
from sqlalchemy import Enum
import enum

class StatusEnum(enum.Enum):
    active = "active"
    inactive = "inactive"

# Association table for Target Groups and Targets (many-to-many)
target_group_targets_association = Table('target_group_targets', Base.metadata,
    Column('group_id', String(20), ForeignKey('target_groups.group_id', ondelete="CASCADE"), primary_key=True),
    Column('target_id', String(20), ForeignKey('targets.target_id', ondelete="CASCADE"), primary_key=True)
)

class Target(Base):
    __tablename__ = 'targets'
    target_id = Column(String(20), primary_key=True, index=True)
    target_type = Column(String(50), nullable=False)
    identifier = Column(String(100), nullable=False)
    associated_imsi = Column(String(20))
    associated_imei = Column(String(20))
    created_at = Column(TIMESTAMP(timezone=True), server_default='CURRENT_TIMESTAMP')
    status = Column(Enum(StatusEnum), nullable=False, default=StatusEnum.active)  # Default to 'active'
    associated_bts = Column(String(50))
    description = Column(Text)

    groups = relationship(
        "TargetGroup",
        secondary=target_group_targets_association,
        back_populates="targets"
    )

class Rule(Base):
    __tablename__ = 'rules'
    rule_id = Column(String(20), primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), server_default='CURRENT_TIMESTAMP')
    modified_at = Column(TIMESTAMP(timezone=True), server_default='CURRENT_TIMESTAMP')
    version = Column(String(20))
    rule_type = Column(String(50))
    data_source = Column(String(50))
    required_fields = Column(ARRAY(Text), nullable=False)
    default_params = Column(JSONB)
    tags = Column(ARRAY(Text))
    sql_template = Column(Text)

class TargetGroup(Base):
    __tablename__ = 'target_groups'
    group_id = Column(String(20), primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), server_default='CURRENT_TIMESTAMP')
    created_by = Column(String(100))
    status = Column(String(20), nullable=False)

    targets = relationship(
        "Target",
        secondary=target_group_targets_association,
        back_populates="groups",
        cascade="all, delete"
    )
    
    rules = relationship("TargetGroupRule", back_populates="group", cascade="all, delete-orphan")


class TargetGroupRule(Base):
    __tablename__ = 'target_group_rules'
    group_rule_id = Column(Integer, primary_key=True, autoincrement=True)
    group_id = Column(String(20), ForeignKey('target_groups.group_id', ondelete="CASCADE"), nullable=False)
    rule_id = Column(String(20), ForeignKey('rules.rule_id', ondelete="CASCADE"), nullable=False)
    custom_params = Column(JSONB)
    added_at = Column(TIMESTAMP(timezone=True), server_default='CURRENT_TIMESTAMP')
    
    group = relationship("TargetGroup", back_populates="rules")
    rule_details = relationship("Rule") # To fetch rule details easily