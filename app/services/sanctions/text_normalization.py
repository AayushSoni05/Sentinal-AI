import re
import unicodedata


def normalize_text(value: str | None) -> str:
    """
    Normalize text for deterministic sanctions matching.

    Removes diacritics, punctuation, repeated whitespace,
    and normalizes casing.
    """

    if not value:
        return ""

    value = unicodedata.normalize("NFKD", value)

    value = "".join(
        character
        for character in value
        if not unicodedata.combining(character)
    )

    value = value.upper()

    value = re.sub(r"[^A-Z0-9\s]", " ", value)

    value = re.sub(r"\s+", " ", value)

    return value.strip()