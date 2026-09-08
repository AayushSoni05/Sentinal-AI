from pydantic import BaseModel
class CustomerRequest(BaseModel):

    name: str
    customer_type: str
    country: str
    pan: str | None = None
    gst_cin: str | None = None

class CustomerUpdate(BaseModel):

    name: str | None = None
    customer_type: str | None = None
    country: str | None = None
    pan: str | None = None
    gst_cin: str | None = None

class PersonRequest(BaseModel):

    full_name: str
    date_of_birth: str | None = None
    nationality: str | None = None
    country_of_residence: str | None = None
    identity_type: str | None = None
    identity_number: str | None = None

class LegalEntityRequest(BaseModel):
    legal_name: str
    trading_name: str | None = None
    entity_type: str
    registration_number: str | None = None
    incorporation_date: str | None = None
    country_of_incorporation: str | None = None
    registered_address: str | None = None
    principal_business_address: str | None = None
    business_activity: str | None = None
    industry: str | None = None