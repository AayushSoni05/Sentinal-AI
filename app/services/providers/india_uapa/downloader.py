# ============================================================
# INDIA UAPA / MHA LIST DOWNLOADER
# ============================================================

import requests


MHA_TERRORIST_ORGANISATIONS_URL = (
    "https://www.mha.gov.in/en/commoncontent/"
    "list-of-organisations-designated-"
    "‘terrorist-organizations’-under-section-35-of"
)

MHA_INDIVIDUAL_TERRORISTS_URL = (
    "https://xn--i1b5bzbybhfo5c8b4bxh.xn--11b7cb3a6a."
    "xn--h2brj9c/en/commoncontent/"
    "individuals-terrorists-listed-fourth-schedule-"
    "of-unlawful-activities-prevention-act"
)


def _download_page(
    url: str
):
    response = requests.get(
        url,
        headers={
            "User-Agent": "Sentinel-AI/1.0"
        },
        timeout=30
    )

    response.raise_for_status()

    return response.content


def download_india_uapa_lists():
    return {
        "terrorist_organisations":
            _download_page(
                MHA_TERRORIST_ORGANISATIONS_URL
            ),
        "individual_terrorists":
            _download_page(
                MHA_INDIVIDUAL_TERRORISTS_URL
            )
    }