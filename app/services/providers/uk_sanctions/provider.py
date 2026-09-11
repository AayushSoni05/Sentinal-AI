# ============================================================
# UK SANCTIONS LIST PROVIDER
# ============================================================

from app.services.providers.uk_sanctions.downloader import (
    download_uk_sanctions_list
)

from app.services.providers.uk_sanctions.parser import (
    parse_uk_sanctions_list
)

from app.services.providers.uk_sanctions.normalizer import (
    normalize_uk_record
)

from app.services.providers.uk_sanctions.matcher import (
    match_subject_against_uk
)


class UKSanctionsProvider:

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
                "UKSanctionsProvider "
                "only supports SANCTIONS"
            )

        xml_data = download_uk_sanctions_list()

        raw_records = parse_uk_sanctions_list(
            xml_data
        )

        normalized_records = [
            normalize_uk_record(record)
            for record in raw_records
        ]

        match = match_subject_against_uk(
            subject_name=name,
            uk_records=normalized_records
        )

        matched_record = match.get(
            "matched_record"
        )

        return {
            "provider": "UK",
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