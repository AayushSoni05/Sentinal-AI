# ============================================================
# CUSTOMER TYPES
# ============================================================

ALLOWED_CUSTOMER_TYPES = {
    "Individual",
    "Sole Proprietorship",
    "Company",
    "Partnership",
    "Other Legal Arrangement"
}


# ============================================================
# REQUIRED SECTIONS BY CUSTOMER TYPE
# ============================================================

CUSTOMER_TYPE_SECTIONS = {
    "Individual": {
        "identity",
        "address",
        "relationship",
        "financial"
    },

    "Sole Proprietorship": {
        "proprietor_identity",
        "business",
        "relationship",
        "financial"
    },

    "Company": {
        "entity",
        "business",
        "authorized_persons",
        "ownership_control",
        "relationship",
        "financial"
    },

    "Partnership": {
        "entity",
        "partners",
        "business",
        "ownership_control",
        "relationship",
        "financial"
    },

    "Other Legal Arrangement": {
        "arrangement",
        "parties",
        "control",
        "relationship",
        "financial"
    }
}

# ============================================================
# CUSTOMER TYPE FIELD MAP
# ============================================================

CUSTOMER_TYPE_FIELDS = {

    "Individual": {

        "identity": [
            "full_name",
            "date_of_birth",
            "nationality",
            "country_of_residence",
            "identity_type",
            "identity_number"
        ],

        "address": [
            "residential_address",
            "contact_details"
        ],

        "relationship": [
            "purpose_of_relationship",
            "requested_products",
            "expected_activity"
        ],

        "financial": [
            "occupation",
            "source_of_funds",
            "source_of_wealth",
            "expected_turnover"
        ]
    },

    "Sole Proprietorship": {

        "proprietor": [
            "full_name",
            "date_of_birth",
            "nationality",
            "country_of_residence",
            "identity_type",
            "identity_number"
        ],

        "business": [
            "business_name",
            "business_type",
            "registration_number",
            "business_address",
            "country_of_operation",
            "business_activity"
        ],

        "relationship": [
            "purpose_of_relationship",
            "requested_products",
            "expected_activity"
        ],

        "financial": [
            "source_of_funds",
            "source_of_wealth",
            "expected_turnover"
        ]
    },

    "Company": {

        "entity": [
            "legal_name",
            "trading_name",
            "entity_type",
            "registration_number",
            "incorporation_date",
            "country_of_incorporation",
            "registered_address",
            "principal_business_address"
        ],

        "business": [
            "business_activity",
            "industry",
            "operating_countries",
            "expected_activity"
        ],

        "authorized_persons": [
            "authorized_representatives",
            "authorized_signatories"
        ],

        "ownership_control": [
            "shareholders",
            "directors",
            "controllers",
            "ubos"
        ],

        "relationship": [
            "purpose_of_relationship",
            "requested_products"
        ],

        "financial": [
            "source_of_funds",
            "source_of_wealth",
            "expected_turnover"
        ]
    },

    "Partnership": {

        "entity": [
            "legal_name",
            "partnership_type",
            "registration_number",
            "formation_date",
            "address"
        ],

        "partners": [
            "partners"
        ],

        "business": [
            "business_activity",
            "industry",
            "expected_activity"
        ],

        "ownership_control": [
            "control_relationships"
        ],

        "relationship": [
            "purpose_of_relationship",
            "requested_products"
        ],

        "financial": [
            "source_of_funds",
            "source_of_wealth",
            "expected_turnover"
        ]
    },

    "Other Legal Arrangement": {

        "arrangement": [
            "arrangement_type",
            "legal_name",
            "formation_date",
            "jurisdiction",
            "purpose"
        ],

        "parties": [
            "settlor",
            "trustee",
            "beneficiaries",
            "other_relevant_parties"
        ],

        "control": [
            "controllers"
        ],

        "relationship": [
            "purpose_of_relationship",
            "requested_products"
        ],

        "financial": [
            "source_of_funds",
            "source_of_wealth",
            "expected_activity"
        ]
    }
}

# ============================================================
# GET ONBOARDING REQUIREMENTS
# ============================================================

def get_onboarding_requirements(
    customer_type: str
):
    if customer_type not in ALLOWED_CUSTOMER_TYPES:
        return None, "Invalid customer type"

    return {
        "customer_type": customer_type,
        "required_sections": sorted(
            CUSTOMER_TYPE_SECTIONS[customer_type]
        ),
        "fields": CUSTOMER_TYPE_FIELDS[customer_type]
    }, None