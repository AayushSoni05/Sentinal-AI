from datetime import datetime

from sqlalchemy import Column, String, DateTime, ForeignKey,Boolean
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

    person_id = Column(
        String,
        ForeignKey("persons.id"),
        nullable=True,
        unique=True,
        index=True
    )

    legal_entity_id = Column(
        String,
        ForeignKey("legal_entities.id"),
        nullable=True,
        unique=True,
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

    person = relationship(
        "Person",
        back_populates="customer",
        uselist=False
    )

    legal_entity = relationship(
        "LegalEntity",
        back_populates="customer",
        uselist=False
    )

    kyc_profile = relationship(
        "KYCProfile",
        back_populates="customer",
        uselist=False,
        cascade="all, delete-orphan"
    )

# ============================================================
# PERSON
# ============================================================

class Person(Base):

    __tablename__ = "persons"

    id = Column(
        String,
        primary_key=True,
        index=True
    )

    full_name = Column(
        String,
        nullable=False
    )

    date_of_birth = Column(
        DateTime,
        nullable=True
    )

    nationality = Column(
        String,
        nullable=True
    )

    country_of_residence = Column(
        String,
        nullable=True
    )

    identity_type = Column(
        String,
        nullable=True
    )

    identity_number = Column(
        String,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    customer = relationship(
        "Customer",
        back_populates="person",
        uselist=False
    )

    entity_relationships = relationship(
        "EntityRelationship",
        foreign_keys="EntityRelationship.from_person_id",
        back_populates="from_person"
    )

# ============================================================
# LEGAL ENTITY
# ============================================================

class LegalEntity(Base):

    __tablename__ = "legal_entities"

    id = Column(
        String,
        primary_key=True,
        index=True
    )

    legal_name = Column(
        String,
        nullable=False
    )

    trading_name = Column(
        String,
        nullable=True
    )

    entity_type = Column(
        String,
        nullable=False
    )

    registration_number = Column(
        String,
        nullable=True
    )

    incorporation_date = Column(
        DateTime,
        nullable=True
    )

    country_of_incorporation = Column(
        String,
        nullable=True
    )

    registered_address = Column(
        String,
        nullable=True
    )

    principal_business_address = Column(
        String,
        nullable=True
    )

    business_activity = Column(
        String,
        nullable=True
    )

    industry = Column(
        String,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    customer = relationship(
        "Customer",
        back_populates="legal_entity",
        uselist=False
    )

    entity_relationships_from = relationship(
        "EntityRelationship",
        foreign_keys="EntityRelationship.from_legal_entity_id",
        back_populates="from_legal_entity"
    )

    entity_relationships_to = relationship(
        "EntityRelationship",
        foreign_keys="EntityRelationship.to_legal_entity_id",
        back_populates="to_legal_entity"
    )

# ============================================================
# ENTITY RELATIONSHIP
# ============================================================

class EntityRelationship(Base):

    __tablename__ = "entity_relationships"

    id = Column(
        String,
        primary_key=True,
        index=True
    )

    relationship_type = Column(
        String,
        nullable=False
    )

    from_person_id = Column(
        String,
        ForeignKey("persons.id"),
        nullable=True,
        index=True
    )

    from_legal_entity_id = Column(
        String,
        ForeignKey("legal_entities.id"),
        nullable=True,
        index=True
    )

    to_legal_entity_id = Column(
        String,
        ForeignKey("legal_entities.id"),
        nullable=False,
        index=True
    )

    from_person = relationship(
        "Person",
        foreign_keys=[from_person_id],
        back_populates="entity_relationships"
    )

    from_legal_entity = relationship(
        "LegalEntity",
        foreign_keys=[from_legal_entity_id],
        back_populates="entity_relationships_from"
    )

    to_legal_entity = relationship(
        "LegalEntity",
        foreign_keys=[to_legal_entity_id],
        back_populates="entity_relationships_to"
    )

    
    ownership_percentage = Column(
        String,
        nullable=True
    )

    voting_percentage = Column(
        String,
        nullable=True
    )

    is_control = Column(
        String,
        nullable=True
    )

    effective_from = Column(
        DateTime,
        nullable=True
    )

    effective_to = Column(
        DateTime,
        nullable=True
    )

    evidence_reference = Column(
        String,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

# ============================================================
# EVIDENCE / DOCUMENT
# ============================================================

class Evidence(Base):

    __tablename__ = "evidence"

    id = Column(
        String,
        primary_key=True,
        index=True
    )

    subject_type = Column(
        String,
        nullable=False
    )

    subject_id = Column(
        String,
        nullable=False,
        index=True
    )

    document_type = Column(
        String,
        nullable=False
    )

    document_number = Column(
        String,
        nullable=True
    )

    issuing_authority = Column(
        String,
        nullable=True
    )

    issuing_country = Column(
        String,
        nullable=True
    )

    issue_date = Column(
        DateTime,
        nullable=True
    )

    expiry_date = Column(
        DateTime,
        nullable=True
    )

    verification_status = Column(
        String,
        nullable=False,
        default="Not Provided"
    )

    verification_method = Column(
        String,
        nullable=True
    )

    verified_by = Column(
        String,
        nullable=True
    )

    verified_at = Column(
        DateTime,
        nullable=True
    )

    storage_reference = Column(
        String,
        nullable=True
    )

    metadata_text = Column(
        String,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

# ============================================================
# KYC PROFILE
# ============================================================

class KYCProfile(Base):

    __tablename__ = "kyc_profiles"

    id = Column(
        String,
        primary_key=True,
        index=True
    )

    customer_id = Column(
        String,
        ForeignKey("customers.id"),
        nullable=False,
        unique=True,
        index=True
    )

    # Identity / KYC
    identity_type = Column(
        String,
        nullable=True
    )

    identity_number = Column(
        String,
        nullable=True
    )

    aadhaar_number = Column(
        String,
        nullable=True
    )

    pan_number = Column(
        String,
        nullable=True
    )

    # Onboarding
    onboarding_channel = Column(
        String,
        nullable=True
    )

    customer_country = Column(
        String,
        nullable=True
    )

    # Business / financial information
    occupation = Column(
        String,
        nullable=True
    )

    source_of_funds_type = Column(
        String,
        nullable=True
    )

    funds_documentation = Column(
        String,
        nullable=True
    )

    monthly_turnover = Column(
        String,
        nullable=True
    )

    actual_monthly_turnover = Column(
        String,
        nullable=True
    )

    product_category = Column(
        String,
        nullable=True
    )

    # Timestamps
    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    customer = relationship(
        "Customer",
        back_populates="kyc_profile"
    )

    screening_results = relationship(
        "ScreeningResult",
        back_populates="kyc_profile",
        cascade="all, delete-orphan"
    )

# ============================================================
# SCREENING RESULT
# ============================================================

class ScreeningResult(Base):

    __tablename__ = "screening_results"

    id = Column(
        String,
        primary_key=True,
        index=True
    )

    kyc_profile_id = Column(
        String,
        ForeignKey("kyc_profiles.id"),
        nullable=False,
        index=True
    )

    subject_type = Column(
        String,
        nullable=False
    )

    subject_id = Column(
        String,
        nullable=False,
        index=True
    )

    relationship_role = Column(
        String,
        nullable=False
    )

    source_uid = Column(
        String,
        nullable=True,
        index=True
    )

    country_match = Column(
        Boolean,
        nullable=True
    )

    identifier_match = Column(
        Boolean,
        nullable=True
    )

    match_strength = Column(
        String,
        nullable=True
    )

    evidence_strength = Column(
        String,
        nullable=True
    )

    screening_type = Column(
        String,
        nullable=False
    )

    provider = Column(
        String,
        nullable=False
    )

    result = Column(
        String,
        nullable=False
    )

    matched_name = Column(
        String,
        nullable=True
    )

    match_confidence = Column(
        String,
        nullable=True
    )

    evidence = Column(
        String,
        nullable=True
    )

    checked_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    kyc_profile = relationship(
        "KYCProfile",
        back_populates="screening_results"
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

    risk_assessment = relationship(
        "RiskAssessment",
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

# ============================================================
# RISK ASSESSMENT
# ============================================================

class RiskAssessment(Base):

    __tablename__ = "risk_assessments"

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

    risk_score = Column(
        String,
        nullable=True
    )

    risk_tier = Column(
        String,
        nullable=True
    )

    assessment_status = Column(
        String,
        nullable=False,
        default="Pending"
    )

    assessment_reason = Column(
        String,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    investigation = relationship(
        "Investigation",
        back_populates="risk_assessment"
    )

# ============================================================
# RISK RULE
# ============================================================

class RiskRule(Base):

    __tablename__ = "risk_rules"

    id = Column(
        String,
        primary_key=True,
        index=True
    )

    rule_name = Column(
        String,
        nullable=False,
        unique=True
    )

    factor = Column(
        String,
        nullable=False,
        index=True
    )

    min_score = Column(
        String,
        nullable=False
    )

    max_score = Column(
        String,
        nullable=False
    )

    risk_tier = Column(
        String,
        nullable=False
    )

    action = Column(
        String,
        nullable=False
    )

    is_active = Column(
        Boolean,
        nullable=False,
        default=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )