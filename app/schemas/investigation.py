from pydantic import BaseModel


class InvestigationRequest(BaseModel):
    customer_number: str
    company_name: str


class InvestigationUpdate(BaseModel):
    company_name: str | None = None
    status: str | None = None