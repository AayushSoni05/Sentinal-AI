from datetime import datetime

from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database.connection import Base


# ============================================================
# CUSTOMER
# ============================================================

class Customer(Base):

    __tablename__ = "customers"

    id = Column(
        String,
        primary_key=True,
        index=True
    )

    customer_number = Column(
        String,
        unique=True,
        index=True,
        nullable=False
    )

    name = Column(
        String,
        nullable=False
    )

    customer_type = Column(
        String,
        nullable=False
    )

    country = Column(
        String,
        nullable=False
    )

    pan = Column(
        String,
        unique=True,
        nullable=True
    )

    gst_cin = Column(
        String,
        unique=True,
        nullable=True
    )

    status = Column(
        String,
        nullable=False,
        default="Active"
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    investigations = relationship(
        "Investigation",
        back_populates="customer"
    )


# ============================================================
# INVESTIGATION
# ============================================================

class Investigation(Base):

    __tablename__ = "investigations"

    id = Column(
        String,
        primary_key=True,
        index=True
    )

    investigation_number = Column(
        String,
        unique=True,
        index=True,
        nullable=False
    )

    customer_id = Column(
        String,
        ForeignKey("customers.id"),
        nullable=True,
        index=True
    )

    customer = relationship(
        "Customer",
        back_populates="investigations"
    )

    decision = relationship(
        "InvestigationDecision",
        back_populates="investigation",
        uselist=False
    )

    company_name = Column(
        String,
        nullable=False
    )

    status = Column(
        String,
        nullable=False,
        default="Draft"
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )


# ============================================================
# INVESTIGATION DECISION
# ============================================================

class InvestigationDecision(Base):

    __tablename__ = "investigation_decisions"

    id = Column(
        String,
        primary_key=True,
        index=True
    )

    investigation_id = Column(
        String,
        ForeignKey("investigations.id"),
        nullable=False,
        unique=True,
        index=True
    )

    recommendation = Column(
        String,
        nullable=False
    )

    analyst_decision = Column(
        String,
        nullable=True
    )

    approval_status = Column(
        String,
        nullable=False,
        default="Pending"
    )

    approver_decision = Column(
        String,
        nullable=True
    )

    reason = Column(
        String,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    investigation = relationship(
        "Investigation",
        back_populates="decision"
    )


# ============================================================
# ROLE
# ============================================================

class Role(Base):

    __tablename__ = "roles"

    id = Column(
        String,
        primary_key=True,
        index=True
    )

    name = Column(
        String,
        unique=True,
        index=True,
        nullable=False
    )

    description = Column(
        String,
        nullable=True
    )

    users = relationship(
        "User",
        back_populates="role"
    )


# ============================================================
# USER
# ============================================================

class User(Base):

    __tablename__ = "users"

    id = Column(
        String,
        primary_key=True,
        index=True
    )

    username = Column(
        String,
        unique=True,
        index=True,
        nullable=False
    )

    email = Column(
        String,
        unique=True,
        index=True,
        nullable=False
    )

    password_hash = Column(
        String,
        nullable=False
    )

    role_id = Column(
        String,
        ForeignKey("roles.id"),
        nullable=False,
        index=True
    )

    status = Column(
        String,
        nullable=False,
        default="Active"
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    role = relationship(
        "Role",
        back_populates="users"
    )

# ============================================================
# AUDIT LOG
# ============================================================

class AuditLog(Base):

    __tablename__ = "audit_logs"

    id = Column(
        String,
        primary_key=True,
        index=True
    )

    user_id = Column(
        String,
        ForeignKey("users.id"),
        nullable=True,
        index=True
    )

    action = Column(
        String,
        nullable=False
    )

    entity_type = Column(
        String,
        nullable=False
    )

    entity_id = Column(
        String,
        nullable=True
    )

    old_value = Column(
        String,
        nullable=True
    )

    new_value = Column(
        String,
        nullable=True
    )

    reason = Column(
        String,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    user = relationship(
        "User"
    )