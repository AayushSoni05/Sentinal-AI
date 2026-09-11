def exact_identifier_match(
    target_identifiers: dict,
    candidate_identifiers: dict,
) -> bool:
    """
    Return True when any shared identifier has an exact match.
    """

    if not target_identifiers or not candidate_identifiers:
        return False

    for identifier_name, target_value in target_identifiers.items():
        if not target_value:
            continue

        candidate_value = candidate_identifiers.get(identifier_name)

        if not candidate_value:
            continue

        if (
            str(target_value).strip().upper()
            == str(candidate_value).strip().upper()
        ):
            return True

    return False