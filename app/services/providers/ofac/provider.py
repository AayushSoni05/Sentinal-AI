# ============================================================
# OFAC SANCTIONS PROVIDER
# ============================================================

from app.services.providers.ofac.downloader import (
    download_sdn_list
)

from app.services.providers.ofac.parser import (
    parse_sdn_list
)

from app.services.providers.ofac.normalizer import (
    normalize_sdn_record
)

from app.services.providers.ofac.matcher import (
    match_subject_against_sdn
)


class OFACSanctionsProvider:

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
                "OFACSanctionsProvider only supports SANCTIONS"
            )

        xml_data = download_sdn_list()

        raw_records = parse_sdn_list(
            xml_data
        )

        normalized_records = [
            normalize_sdn_record(record)
            for record in raw_records
        ]

        match = match_subject_against_sdn(
            subject_name=name,
            sdn_records=normalized_records,
            subject_country=subject_country,
            subject_identifiers=subject_identifiers
        )

        matched_record = match.get(
            "matched_record"
        )

        return {
            "provider": "OFAC",
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
            "subject_type": subject_type,
            "subject_id": subject_id,
            "relationship_role": relationship_role,
            "country_match":
                match["country_match"],
            "match_strength":
                match["match_strength"],
            "identifier_match":
                match["identifier_match"],
            "evidence_strength":
                match["evidence_strength"]
        }