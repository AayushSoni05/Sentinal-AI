from pydantic import BaseModel


class KYCRequest(BaseModel):

    identity_type: str | None = None
    identity_number: str | None = None
    aadhaar_number: str | None = None
    pan_number: str | None = None

    onboarding_channel: str | None = None
    customer_country: str | None = None

    occupation: str | None = None
    source_of_funds_type: str | None = None
    funds_documentation: str | None = None

    monthly_turnover: str | None = None
    actual_monthly_turnover: str | None = None

    product_category: str | None = None


class KYCUpdate(BaseModel):

    identity_type: str | None = None
    identity_number: str | None = None
    aadhaar_number: str | None = None
    pan_number: str | None = None

    onboarding_channel: str | None = None
    customer_country: str | None = None

    occupation: str | None = None
    source_of_funds_type: str | None = None
    funds_documentation: str | None = None

    monthly_turnover: str | None = None
    actual_monthly_turnover: str | None = None

    product_category: str | None = None