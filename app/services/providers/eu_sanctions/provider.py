# ============================================================
# EU CONSOLIDATED FINANCIAL SANCTIONS LIST PROVIDER
# ============================================================

from app.services.providers.eu_sanctions.downloader import (
    download_eu_sanctions_list
)

from app.services.providers.eu_sanctions.parser import (
    parse_eu_sanctions_list
)

from app.services.providers.eu_sanctions.normalizer import (
    normalize_eu_record
)

from app.services.providers.eu_sanctions.matcher import (
    match_subject_against_eu
)


class EUSanctionsProvider:

    def screen(
        self,
        name: str,
        screening_type: str,
        subject_type: str,
        subject_id: str,
        relationship_role: str,
        subject_country: str | None = None,
        subject_identifiers: dict | None = None
    ):

        if screening_type != "SANCTIONS":
            raise ValueError(
                "EUSanctionsProvider "
                "only supports SANCTIONS"
            )

        xml_data = download_eu_sanctions_list()

        raw_records = parse_eu_sanctions_list(
            xml_data
        )

        normalized_records = [
            normalize_eu_record(record)
            for record in raw_records
        ]

        match = match_subject_against_eu(
            subject_name=name,
            eu_records=normalized_records
        )

        matched_record = match.get(
            "matched_record"
        )

        return {
            "provider": "EU",
            "screening_type": "SANCTIONS",
            "result": match["result"],
            "matched_name": (
                matched_record.get(
                    "original_name"
                )
                if matched_record
                else None
            ),
            "match_confidence":
                match["match_confidence"],
            "evidence": matched_record,
            "source_uid": (
                matched_record.get("uid")
                if matched_record
                else None
            ),
            "subject_type": subject_type,
            "subject_id": subject_id,
            "relationship_role": relationship_role,
            "country_match": None,
            "identifier_match": None,
            "match_strength":
                match["match_strength"],
            "evidence_strength":
                match["evidence_strength"]
        }