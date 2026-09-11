def birth_year(value: str | None) -> str | None:
    """
    Extract the YYYY component from a date value.
    """

    if not value:
        return None

    value = value.strip()

    if len(value) >= 4 and value[:4].isdigit():
        return value[:4]

    return None


def birth_year_agreement(
    target_dob: str | None,
    candidate_dobs: list[str],
) -> bool:
    """
    Return True when the target and candidate share the same birth year.
    """

    target_year = birth_year(target_dob)

    if not target_year:
        return False

    candidate_years = {
        birth_year(value)
        for value in candidate_dobs
        if birth_year(value)
    }

    return target_year in candidate_years


def country_agreement(
    target_country: str | None,
    candidate_countries: list[str],
) -> bool:
    """
    Return True when the target country matches one of the candidate countries.
    """

    if not target_country:
        return False

    target = target_country.strip().upper()

    return target in {
        country.strip().upper()
        for country in candidate_countries
        if country
    }


def identifier_agreement(
    target_identifiers: dict,
    candidate_identifiers: dict,
) -> bool:
    """
    Return True when any shared identifier type has the same non-empty value.
    """

    if not target_identifiers or not candidate_identifiers:
        return False

    for identifier_name, target_value in target_identifiers.items():
        if not target_value:
            continue

        candidate_value = candidate_identifiers.get(identifier_name)

        if not candidate_value:
            continue

        if str(target_value).strip().upper() == str(candidate_value).strip().upper():
            return True

    return False