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