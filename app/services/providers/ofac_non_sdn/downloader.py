# ============================================================
# OFAC CONSOLIDATED NON-SDN LIST DOWNLOADER
# ============================================================

import requests


OFAC_NON_SDN_XML_URL = (
    "https://sanctionslistservice.ofac.treas.gov/"
    "api/PublicationPreview/exports/consolidated.xml"
)


def download_non_sdn_list():
    response = requests.get(
        OFAC_NON_SDN_XML_URL,
        headers={
            "User-Agent": "Sentinel-AI/1.0"
        },
        timeout=30
    )

    response.raise_for_status()

    return response.content