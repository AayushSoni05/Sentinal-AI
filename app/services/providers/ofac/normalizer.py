# ============================================================
# OFAC RECORD NORMALIZER
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


def normalize_sdn_record(
    record: dict
):
    original_name = record.get("name")

    aliases = record.get(
        "aliases",
        []
    )

    normalized_aliases = [
        normalize_name(alias)
        for alias in aliases
        if alias
    ]

    identifiers = []

    for identifier in record.get(
        "identifiers",
        []
    ):
        identifiers.append({
            "uid": identifier.get("uid"),
            "id_type": identifier.get("id_type"),
            "id_number": identifier.get("id_number"),
            "id_country": identifier.get("id_country")
        })

    return {
        "uid": record.get("uid"),
        "original_name": original_name,
        "normalized_name": normalize_name(
            original_name
        ),
        "original_aliases": aliases,
        "normalized_aliases": normalized_aliases,
        "sdn_type": record.get("sdn_type"),
        "programs": record.get(
            "programs",
            []
        ),
        "addresses": record.get(
            "addresses",
            []
        ),
        "identifiers": identifiers
    }