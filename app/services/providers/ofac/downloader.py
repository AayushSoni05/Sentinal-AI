# ============================================================
# OFAC SANCTIONS LIST DOWNLOADER
# ============================================================

import requests


OFAC_SDN_XML_URL = (
    "https://sanctionslistservice.ofac.treas.gov/"
    "api/PublicationPreview/exports/sdn.xml"
)


def download_sdn_list():
    response = requests.get(
        OFAC_SDN_XML_URL,
        headers={
            "User-Agent": "Sentinel-AI/1.0"
        },
        timeout=30
    )

    response.raise_for_status()

    return response.content