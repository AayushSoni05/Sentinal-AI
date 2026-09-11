from .name_similarity import name_similarity
from .phonetic import phonetic_agreement
from .text_normalization import normalize_text


def find_best_name_match(
    target_name: str,
    canonical_name: str,
    aliases: list[str] | None = None,
) -> dict:
    """
    Compare the target against the canonical name and all available aliases.

    Returns the strongest name match while preserving whether the match
    came from the canonical name or an alias.
    """

    target_name = normalize_text(target_name)
    canonical_name = normalize_text(canonical_name)
    aliases = [
        normalize_text(alias)
        for alias in (aliases or [])
        if alias
    ]

    aliases = aliases or []

    candidates = [
        {
            "name": canonical_name,
            "is_alias": False,
        }
    ]

    candidates.extend(
        {
            "name": alias,
            "is_alias": True,
        }
        for alias in aliases
        if alias
    )

    best_match = None

    for candidate in candidates:
        similarity = name_similarity(
            target_name,
            candidate["name"],
        )

        match = {
            "matched_name": candidate["name"],
            "matched_alias_used": (
                candidate["name"]
                if candidate["is_alias"]
                else None
            ),
            "jaro_winkler": similarity["jaro_winkler"],
            "levenshtein": similarity["levenshtein"],
            "name_combined": similarity["combined"],
            "phonetic_agreement": phonetic_agreement(
                target_name,
                candidate["name"],
            ),
        }

        if (
            best_match is None
            or match["name_combined"] > best_match["name_combined"]
        ):
            best_match = match

    return best_match