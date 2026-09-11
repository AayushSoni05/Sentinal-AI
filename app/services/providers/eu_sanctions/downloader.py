# ============================================================
# EU CONSOLIDATED FINANCIAL SANCTIONS LIST DOWNLOADER
# ============================================================

import requests


EU_SANCTIONS_XML_URL = (
    "https://webgate.ec.europa.eu/"
    "fsd/fsf/public/files/"
    "xmlFullSanctionsList_1_1/content"
    "?token=dG9rZW4tMjAxNw"
)


def download_eu_sanctions_list():
    response = requests.get(
        EU_SANCTIONS_XML_URL,
        headers={
            "User-Agent": "Sentinel-AI/1.0"
        },
        timeout=30
    )

    response.raise_for_status()

    return response.content