# ============================================================
# UK SANCTIONS LIST DOWNLOADER
# ============================================================

import requests


UK_SANCTIONS_XML_URL = (
    "https://sanctionslist.fcdo.gov.uk/docs/"
    "UK-Sanctions-List.xml"
)


def download_uk_sanctions_list():
    response = requests.get(
        UK_SANCTIONS_XML_URL,
        headers={
            "User-Agent": "Sentinel-AI/1.0"
        },
        timeout=30
    )

    response.raise_for_status()

    return response.content