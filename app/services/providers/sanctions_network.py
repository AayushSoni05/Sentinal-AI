# ============================================================
# SANCTIONS.NETWORK PROVIDER
# ============================================================

from urllib.parse import quote

import requests


class SanctionsNetworkProvider:

    BASE_URL = "https://sanctions.network/api"

    def screen(
        self,
        name: str,
        screening_type: str,
        subject_type: str,
        subject_id: str,
        relationship_role: str
    ):
        if screening_type != "SANCTIONS":
            raise ValueError(
                "SanctionsNetworkProvider only supports SANCTIONS"
            )

        encoded_name = quote(name)

        url = (
            f"{self.BASE_URL}"
            f"/rpc/search_sanctions"
            f"?name={encoded_name}"
        )

        response = requests.get(
            url,
            timeout=15
        )

        response.raise_for_status()

        data = response.json()

        return {
            "provider": "SANCTIONS_NETWORK",
            "screening_type": "SANCTIONS",
            "result": "POSSIBLE_MATCH" if data else "CLEAR",
            "matched_name": (
                data[0].get("names", [None])[0]
                if data
                else None
            ),
            "match_confidence": None,
            "evidence": data,
            "subject_type": subject_type,
            "subject_id": subject_id,
            "relationship_role": relationship_role
        }