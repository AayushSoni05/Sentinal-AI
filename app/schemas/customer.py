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