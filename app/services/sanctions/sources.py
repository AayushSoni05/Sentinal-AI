from dataclasses import dataclass
from enum import Enum


# ============================================================
# SOURCE MODEL
# ============================================================

@dataclass(frozen=True)
class SanctionsSourceDefinition:
    source_id: str
    source_name: str
    source_list_name: str
    issuing_authority: str
    issuing_country: str
    region: str
    source_scope: str
    source_type: str
    official_source_url: str
    catalogue_resource_url: str | None = None
    data_source_url: str | None = None
    enabled: bool = True
    connector_type: str = "UNKNOWN"
    implementation_status: str = "DISCOVERED"
    parser_config: dict | None = None
    xml_namespace: str | None = None


# ============================================================
# SOURCE STATUS
# ============================================================

class SourceScreeningStatus(str, Enum):
    MATCH = "MATCH"
    POSSIBLE_MATCH = "POSSIBLE_MATCH"
    NO_MATCH = "NO_MATCH"
    UNAVAILABLE = "UNAVAILABLE"
    ERROR = "ERROR"


# ============================================================
# GLOBAL SOURCE CATALOGUE
# ============================================================

SANCTIONS_SOURCE_CATALOG = [
    SanctionsSourceDefinition(
        source_id="UNSC",
        source_name="United Nations Security Council",
        source_list_name="UN Security Council Consolidated Sanctions List",
        issuing_authority="United Nations Security Council",
        issuing_country="GLOBAL",
        region="GLOBAL",
        source_scope="GLOBAL",
        source_type="SANCTIONS",
        official_source_url=(
            "https://scsanctions.un.org/resources/xml/en/name/consolidated.xml"
        ),
        connector_type="XML",
        implementation_status="IMPLEMENTED",
        parser_config={
            "record_paths": {
                "person": ".//INDIVIDUAL",
                "entity": ".//ENTITY",
            },
            "person": {
                "id": "DATAID",
                "name_fields": [
                    "FIRST_NAME",
                    "SECOND_NAME",
                    "THIRD_NAME",
                    "FOURTH_NAME",
                ],
                "alias_path": "INDIVIDUAL_ALIAS/ALIAS_NAME",
                "nationality_path": "NATIONALITY/VALUE",
                "date_of_birth_path": "INDIVIDUAL_DATE_OF_BIRTH/DATE",
                "identifier_path": "INDIVIDUAL_DOCUMENT/NUMBER",
            },
            "entity": {
                "id": "DATAID",
                "name_fields": [
                    "FIRST_NAME",
                ],
                "alias_path": "ENTITY_ALIAS/ALIAS_NAME",
                "country_path": "ENTITY_ADDRESS/COUNTRY",
            },
        },
    ),

    SanctionsSourceDefinition(
        source_id="OFAC_SDN",
        source_name="U.S. Department of the Treasury OFAC",
        source_list_name="Specially Designated Nationals (SDN) List",
        issuing_authority="U.S. Department of the Treasury",
        issuing_country="UNITED_STATES",
        region="NORTH_AMERICA",
        source_scope="GLOBAL",
        source_type="SANCTIONS",
        official_source_url=(
            "https://sanctionslistservice.ofac.treas.gov/"
            "api/PublicationPreview/exports/sdn.xml"
        ),
        connector_type="XML",
        implementation_status="IMPLEMENTED",
        xml_namespace=(
            "https://sanctionslistservice.ofac.treas.gov/"
            "api/PublicationPreview/exports/XML"
        ),
        parser_config={
            "records": {
                "path": ".//sdnEntry",
                "type_path": "sdnType",
                "record_type_mapping": {
                    "Individual": "PERSON",
                    "Entity": "ENTITY",
                    "Vessel": "VESSEL",
                    "Aircraft": "AIRCRAFT",
                },
            },
            "person": {
                "id": "uid",
                "name_fields": [
                    "firstName",
                    "lastName",
                ],
                "alias": {
                    "record_path": "akaList/aka",
                    "name_fields": [
                        "firstName",
                        "lastName",
                    ],
                },
                "date_of_birth_path": (
                    "dateOfBirthList/dateOfBirthItem/dateOfBirth"
                ),
                "identifier": {
                    "record_path": "idList/id",
                    "type_path": "idType",
                    "value_path": "idNumber",
                    "allowed_types": [
                        "Passport",
                        "National ID No.",
                        "Identification Number",
                    ],
                },
            },
            "entity": {
                "id": "uid",
                "name_fields": [
                    "firstName",
                    "lastName",
                ],
                "alias": {
                    "record_path": "akaList/aka",
                    "name_fields": [
                        "firstName",
                        "lastName",
                    ],
                },
                "identifier": {
                    "record_path": "idList/id",
                    "type_path": "idType",
                    "value_path": "idNumber",
                    "allowed_types": [
                        "Registration Number",
                        "Tax ID No.",
                        "Business Registration Number",
                        "Company Number",
                    ],
                },
                "country_path": "addressList/address/country",
            },
            "vessel": {
                "id": "uid",
                "name_fields": [
                    "lastName",
                ],
                "identifier": "vesselInfo/callSign",
                "country_path": "vesselInfo/vesselFlag",
            },

            "aircraft": {
                "id": "uid",
                "name_fields": [
                    "lastName",
                ],
                "identifier": {
                    "record_path": "idList/id",
                    "type_path": "idType",
                    "value_path": "idNumber",
                    "allowed_types": [
                        "Aircraft Construction Number (also called L/N or S/N or F/N)",
                        "Aircraft Manufacturer's Serial Number (MSN)",
                    ],
                },
            },
        },
    ),

    SanctionsSourceDefinition(
        source_id="OFAC_NON_SDN",
        source_name="U.S. Department of the Treasury OFAC",
        source_list_name="Consolidated Non-SDN Lists",
        issuing_authority="U.S. Department of the Treasury",
        issuing_country="UNITED_STATES",
        region="NORTH_AMERICA",
        source_scope="GLOBAL",
        source_type="SANCTIONS",
        official_source_url=(
            "https://sanctionslistservice.ofac.treas.gov/"
            "api/PublicationPreview/exports/consolidated.xml"
        ),
        connector_type="XML",
        implementation_status="DISCOVERED"
    ),

    SanctionsSourceDefinition(
        source_id="UK_SANCTIONS",
        source_name="UK Sanctions Authority",
        source_list_name="UK Sanctions List",
        issuing_authority="UK Government",
        issuing_country="UNITED_KINGDOM",
        region="EUROPE",
        source_scope="GLOBAL",
        source_type="SANCTIONS",
        official_source_url=(
            "https://sanctionslist.fcdo.gov.uk/docs/UK-Sanctions-List.xml"
        ),
        connector_type="XML",
        implementation_status="DISCOVERED"
    ),

    SanctionsSourceDefinition(
        source_id="EU_SANCTIONS",
        source_name="European Union",
        source_list_name="EU Consolidated Financial Sanctions List",
        issuing_authority="European Union",
        issuing_country="EU",
        region="EUROPE",
        source_scope="GLOBAL",
        source_type="SANCTIONS",
        official_source_url=(
            "https://webgate.ec.europa.eu/fsd/fsf/public/"
            "files/xmlFullSanctionsList_1_1/content"
        ),
        connector_type="XML",
        implementation_status="DISCOVERED"
    ),

    SanctionsSourceDefinition(
        source_id="INDIA_UAPA",
        source_name="Government of India",
        source_list_name="UAPA Designated Terrorists List",
        issuing_authority="Ministry of Home Affairs, Government of India",
        issuing_country="INDIA",
        region="ASIA",
        source_scope="GLOBAL",
        source_type="SANCTIONS",
        official_source_url="https://www.mha.gov.in/",
        connector_type="UNKNOWN",
        implementation_status="DISCOVERED"
    ),

    SanctionsSourceDefinition(
        source_id="SINGAPORE_TSOFA",
        source_name="Government of Singapore",
        source_list_name=(
            "First Schedule of the Terrorism "
            "(Suppression of Financing) Act 2002"
        ),
        issuing_authority="Government of Singapore",
        issuing_country="SINGAPORE",
        region="ASIA",
        source_scope="GLOBAL",
        source_type="SANCTIONS",
        official_source_url="https://sso.agc.gov.sg/Act/TSFA2002",
        connector_type="UNKNOWN",
        implementation_status="DISCOVERED"
    ),
]


# ============================================================
# SOURCE REGISTRY
# ============================================================

def get_all_sources() -> list[SanctionsSourceDefinition]:
    return list(SANCTIONS_SOURCE_CATALOG)


def get_enabled_sources() -> list[SanctionsSourceDefinition]:
    return [
        source
        for source in SANCTIONS_SOURCE_CATALOG
        if source.enabled
    ]


def get_source_by_id(
    source_id: str,
) -> SanctionsSourceDefinition | None:
    for source in SANCTIONS_SOURCE_CATALOG:
        if source.source_id == source_id:
            return source

    return None