# ============================================================
# INDIA UAPA / MHA SANCTIONS PROVIDER
# ============================================================

from app.services.providers.india_uapa.downloader import (
    download_india_uapa_lists
)

from app.services.providers.india_uapa.parser import (
    parse_india_uapa_lists
)

from app.services.providers.india_uapa.normalizer import (
    normalize_india_uapa_record
)

from app.services.providers.india_uapa.matcher import (
    match_subject_against_india_uapa
)


class IndiaUAPASanctionsProvider:

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
                "IndiaUAPASanctionsProvider "
                "only supports SANCTIONS"
            )

        html_data = download_india_uapa_lists()

        raw_records = parse_india_uapa_lists(
            html_data
        )

        normalized_records = [
            normalize_india_uapa_record(record)
            for record in raw_records
        ]

        match = match_subject_against_india_uapa(
            subject_name=name,
            india_records=normalized_records
        )

        matched_record = match.get(
            "matched_record"
        )

        return {
            "provider": "INDIA_UAPA",
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