# ============================================================
# UN SECURITY COUNCIL CONSOLIDATED LIST DOWNLOADER
# ============================================================

import requests


UNSC_XML_URL = (
    "https://scsanctions.un.org/"
    "resources/xml/en/name/consolidated.xml"
)


def download_unsc_list() -> bytes:
    """
    Download the current United Nations Security Council
    Consolidated Sanctions List.

    Returns:
        Raw XML bytes.
    """

    response = requests.get(
        UNSC_XML_URL,
        headers={
            "User-Agent": "Sentinel-AI/1.0"
        },
        timeout=30
    )

    response.raise_for_status()

    if not response.content:
        raise ValueError(
            "UNSC sanctions list returned empty content"
        )

    return response.content