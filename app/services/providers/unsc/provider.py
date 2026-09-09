from app.services.providers.unsc.downloader import (
    download_unsc_list
)

from app.services.providers.unsc.parser import (
    parse_unsc_list
)

from app.services.providers.unsc.matcher import (
    match_subject_against_unsc
)


class UNSCSanctionsProvider:

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
                "UNSC provider only supports SANCTIONS screening"
            )

        xml_data = download_unsc_list()

        raw_records = parse_unsc_list(
            xml_data
        )

        match = match_subject_against_unsc(
            name=name,
            records=raw_records,
            subject_identifiers=subject_identifiers
        )

        matched_record = match.get(
            "matched_record"
        )

        return {
            "provider": "UNSC",
            "screening_type": "SANCTIONS",

            "result": match["result"],

            "matched_name": (
                matched_record.get("name")
                if matched_record
                else None
            ),

            "match_confidence": match[
                "match_confidence"
            ],

            "evidence": matched_record,

            "subject_type": subject_type,
            "subject_id": subject_id,
            "relationship_role": relationship_role,

            "country_match": match[
                "country_match"
            ],

            "identifier_match": match[
                "identifier_match"
            ],

            "match_strength": match[
                "match_strength"
            ],

            "evidence_strength": match[
                "evidence_strength"
            ],

            "source_uid": (
                matched_record.get(
                    "reference_number"
                )
                if matched_record
                else None
            ),

            "match_type": match.get(
                "match_type"
            ),

            "recommendation": match.get(
                "recommendation"
            ),

            "similarity_score": match.get(
                "similarity_score"
            ),
        }