from metaphone import doublemetaphone
from .text_normalization import normalize_text


def phonetic_codes(value: str) -> tuple[str, str]:
    """
    Return the Double Metaphone primary and alternate codes
    after text normalization.
    """

    value = normalize_text(value)

    primary, alternate = doublemetaphone(value)

    return primary or "", alternate or ""

def phonetic_agreement(first: str, second: str) -> bool:
    """
    Return True when the names share a Double Metaphone code.
    """

    first_codes = {
        code
        for code in phonetic_codes(first)
        if code
    }

    second_codes = {
        code
        for code in phonetic_codes(second)
        if code
    }

    return bool(first_codes & second_codes)