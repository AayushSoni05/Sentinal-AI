from .name_similarity import name_similarity
from .phonetic import phonetic_agreement


def calculate_name_signals(
    target_name: str,
    candidate_name: str,
) -> dict:
    """
    Calculate the deterministic name-matching signals for one
    target/candidate pair.
    """

    similarity = name_similarity(
        target_name,
        candidate_name,
    )

    return {
        "jaro_winkler": similarity["jaro_winkler"],
        "levenshtein": similarity["levenshtein"],
        "name_combined": similarity["combined"],
        "phonetic_agreement": phonetic_agreement(
            target_name,
            candidate_name,
        ),
    }