from .source_models import SanctionsSourceDefinition


SANCTIONS_SOURCE_CATALOG = [
    SanctionsSourceDefinition(
        source_name="UNSC",
        issuing_country="GLOBAL",
        source_list_name="UN Security Council Consolidated Sanctions List",
        issuing_authority="United Nations Security Council",
        official_source_url="https://scsanctions.un.org/resources/xml/en/name/consolidated.xml",
        global_scope=True,
        provider_name="UNSC",
        provider_implemented=True,
    ),

    SanctionsSourceDefinition(
        source_name="OFAC",
        issuing_country="UNITED_STATES",
        source_list_name="OFAC Specially Designated Nationals (SDN) List",
        issuing_authority="U.S. Department of the Treasury",
        official_source_url="https://sanctionslistservice.ofac.treas.gov/api/PublicationPreview/exports/sdn.xml",
        provider_name="OFAC",
        provider_implemented=False
    ),

    SanctionsSourceDefinition(
        source_name="OFAC_NON_SDN",
        issuing_country="UNITED_STATES",
        source_list_name="OFAC Consolidated Non-SDN Lists",
        issuing_authority="U.S. Department of the Treasury",
        official_source_url="https://sanctionslistservice.ofac.treas.gov/api/PublicationPreview/exports/consolidated.xml",
        provider_name="OFAC_NON_SDN",
        provider_implemented=False
    ),

    SanctionsSourceDefinition(
        source_name="UK",
        issuing_country="UNITED_KINGDOM",
        source_list_name="UK Sanctions List",
        issuing_authority="UK Foreign, Commonwealth & Development Office",
        official_source_url="https://sanctionslist.fcdo.gov.uk/docs/UK-Sanctions-List.xml",
        provider_name="UK",
        provider_implemented=False
    ),

    SanctionsSourceDefinition(
        source_name="EU",
        issuing_country="EU",
        source_list_name="EU Consolidated Financial Sanctions List",
        issuing_authority="European Union",
        official_source_url="https://webgate.ec.europa.eu/fsd/fsf/public/files/xmlFullSanctionsList_1_1/content",
        provider_name="EU",
        provider_implemented=False
    ),

    SanctionsSourceDefinition(
        source_name="INDIA_UAPA",
        issuing_country="INDIA",
        source_list_name="India UAPA / MHA Designated Terrorists Lists",
        issuing_authority="Ministry of Home Affairs, Government of India",
        official_source_url="https://www.mha.gov.in/",
        provider_name="INDIA_UAPA",
        provider_implemented=False
    ),

    SanctionsSourceDefinition(
        source_name="SINGAPORE_TSOFA",
        issuing_country="SINGAPORE",
        source_list_name="First Schedule of the Terrorism (Suppression of Financing) Act 2002",
        issuing_authority="Inter-Ministry Committee on Terrorist Designation, Singapore",
        official_source_url="https://sso.agc.gov.sg/Act/TSFA2002",
        provider_name="SINGAPORE_TSOFA",
        provider_implemented=False,
    ),
]


def get_enabled_sanctions_sources() -> list[SanctionsSourceDefinition]:
    return [
        source
        for source in SANCTIONS_SOURCE_CATALOG
        if source.enabled
    ]