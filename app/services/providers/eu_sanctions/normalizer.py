# ============================================================
# EU CONSOLIDATED FINANCIAL SANCTIONS RECORD NORMALIZER
# ============================================================

import re


def normalize_name(
    name: str | None
):
    if not name:
        return ""

    normalized = name.upper()

    normalized = re.sub(
        r"[^A-Z0-9\s]",
        " ",
        normalized
    )

    normalized = re.sub(
        r"\s+",
        " ",
        normalized
    )

    return normalized.strip()


def normalize_eu_record(
    record: dict
):
    original_name = record.get(
        "name"
    )

    aliases = [
        alias
        for alias in record.get(
            "aliases",
            []
        )
        if alias
    ]

    normalized_aliases = [
        normalize_name(alias)
        for alias in aliases
    ]

    return {
        "uid": record.get(
            "uid"
        ),
        "original_name": original_name,
        "normalized_name": normalize_name(
            original_name
        ),
        "original_aliases": aliases,
        "normalized_aliases": normalized_aliases,
        "subject_type": record.get(
            "subject_type"
        ),
        "designation_date": record.get(
            "designation_date"
        ),
        "programme": record.get(
            "programme"
        )
    }