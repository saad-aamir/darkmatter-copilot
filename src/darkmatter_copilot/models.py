"""Pydantic models for Dark Matter Co-Pilot domain objects."""

from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, EmailStr, field_serializer


def _to_isoformat_utc(value: datetime | None) -> str | None:
    """Serialize datetime as ISO 8601 with UTC timezone (RFC 3339 compliant)."""
    if value is None:
        return None
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.isoformat()


# ===== Enums =====


class LeadSource(str, Enum):
    referral = "referral"
    cold_outbound = "cold_outbound"
    inbound_form = "inbound_form"
    linkedin = "linkedin"
    other = "other"


class LeadStatus(str, Enum):
    new = "new"
    contacted = "contacted"
    in_conversation = "in_conversation"
    proposal_sent = "proposal_sent"
    won = "won"
    lost = "lost"
    on_hold = "on_hold"


class ProjectType(str, Enum):
    landing_page = "landing_page"
    saas_marketing = "saas_marketing"
    portfolio = "portfolio"
    ecommerce = "ecommerce"
    redesign = "redesign"
    corporate_site = "corporate_site"
    other = "other"


class ProjectStatus(str, Enum):
    planning = "planning"
    in_progress = "in_progress"
    delivered = "delivered"
    completed = "completed"
    on_hold = "on_hold"
    cancelled = "cancelled"


class ProposalStatus(str, Enum):
    pending = "pending"
    accepted = "accepted"
    rejected = "rejected"


# ===== Lead models =====


class LeadBase(BaseModel):
    """Shared fields for a lead."""

    company: str
    contact_name: str | None = None
    contact_email: EmailStr | None = None
    contact_phone: str | None = None
    website_url: str | None = None
    source: LeadSource
    source_detail: str | None = None
    existing_client_id: int | None = None
    status: LeadStatus = LeadStatus.new
    business_type: str | None = None
    notes: str | None = None


class LeadCreate(LeadBase):
    """Input shape for creating a new lead."""

    pass


class LeadRead(LeadBase):
    """A lead as returned from the database."""

    id: int
    created_at: datetime
    last_contact_at: datetime | None = None

    @field_serializer("created_at", "last_contact_at", when_used="json")
    def serialize_datetimes(self, value: datetime | None) -> str | None:
        return _to_isoformat_utc(value)


# ===== Client models =====


class ClientBase(BaseModel):
    """Shared fields for a client."""

    name: str
    contact_name: str | None = None
    contact_email: EmailStr | None = None
    contact_phone: str | None = None
    converted_from_lead_id: int | None = None
    notes: str | None = None


class ClientCreate(ClientBase):
    """Input shape for creating a new client."""

    pass


class ClientRead(ClientBase):
    """A client as returned from the database."""

    id: int
    became_client_at: datetime
    project_count: int = 0

    @field_serializer("became_client_at", when_used="json")
    def serialize_datetimes(self, value: datetime | None) -> str | None:
        return _to_isoformat_utc(value)


# ===== Project models =====


class ProjectBase(BaseModel):
    """Shared fields for a project."""

    client_id: int
    name: str
    project_type: ProjectType
    scope: str | None = None
    price: int | None = None
    paid_at: datetime | None = None
    started_at: datetime | None = None
    deadline: datetime | None = None
    completed_at: datetime | None = None
    status: ProjectStatus = ProjectStatus.planning
    deployment_url: str | None = None
    notes: str | None = None
    converted_from_lead_id: int | None = None


class ProjectCreate(ProjectBase):
    """Input shape for creating a new project."""

    pass


class ProjectRead(ProjectBase):
    """A project as returned from the database."""

    id: int
    created_at: datetime
    client_name: str | None = None

    @field_serializer(
        "created_at",
        "paid_at",
        "started_at",
        "deadline",
        "completed_at",
        when_used="json",
    )
    def serialize_datetimes(self, value: datetime | None) -> str | None:
        return _to_isoformat_utc(value)


# ===== Case study models =====


class CaseStudyBase(BaseModel):
    """Shared fields for a case study."""

    project_id: int
    problem: str
    approach: str
    result: str
    tech_stack: list[str] = []
    is_published: bool = False
    published_at: datetime | None = None


class CaseStudyCreate(CaseStudyBase):
    """Input shape for creating a new case study."""

    pass


class CaseStudyRead(CaseStudyBase):
    """A case study as returned from the database."""

    id: int
    created_at: datetime

    @field_serializer("created_at", "published_at", when_used="json")
    def serialize_datetimes(self, value: datetime | None) -> str | None:
        return _to_isoformat_utc(value)


# ===== Proposal models =====


class ProposalBase(BaseModel):
    """Shared fields for a proposal."""

    lead_id: int
    title: str
    body: str
    quoted_price: int | None = None
    status: ProposalStatus = ProposalStatus.pending
    notes: str | None = None


class ProposalCreate(ProposalBase):
    """Input shape for creating a new proposal."""

    pass


class ProposalRead(ProposalBase):
    """A proposal as returned from the database."""

    id: int
    sent_at: datetime
    responded_at: datetime | None = None

    @field_serializer("sent_at", "responded_at", when_used="json")
    def serialize_datetimes(self, value: datetime | None) -> str | None:
        return _to_isoformat_utc(value)
