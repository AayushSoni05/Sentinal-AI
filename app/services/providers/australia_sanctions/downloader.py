# ============================================================
# AUSTRALIA SANCTIONS CONSOLIDATED LIST DOWNLOADER
# ============================================================

import requests


AUSTRALIA_SANCTIONS_XLSX_URL = (
    "https://www.dfat.gov.au/sites/default/files/"
    "Australian_Sanctions_Consolidated_List.xlsx"
)


def download_australia_sanctions_list():

    response = requests.get(
        AUSTRALIA_SANCTIONS_XLSX_URL,
        headers={
            "User-Agent": "Mozilla/5.0"
        },
        timeout=(15, 180)
    )

    response.raise_for_status()

    return response.content