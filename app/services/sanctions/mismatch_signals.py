def gender_mismatch(
    target_gender: str | None,
    candidate_gender: str | None,
) -> bool:
    """
    Return True when both genders are present and clearly different.
    """

    if not target_gender or not candidate_gender:
        return False

    return (
        target_gender.strip().upper()
        != candidate_gender.strip().upper()
    )


def date_of_birth_mismatch(
    target_dob: str | None,
    candidate_dobs: list[str],
) -> bool:
    """
    Return True when both sides provide DOB information but there
    is no exact DOB or birth-year agreement.
    """

    if not target_dob or not candidate_dobs:
        return False

    target_dob = target_dob.strip()

    if target_dob in {
        value.strip()
        for value in candidate_dobs
        if value
    }:
        return False

    target_year = target_dob[:4]

    if target_year.isdigit():
        for value in candidate_dobs:
            if value and value[:4] == target_year:
                return False

    return True


def entity_type_mismatch(
    target_type: str | None,
    candidate_type: str | None,
) -> bool:
    """
    Return True when both entity types are present and clearly different.
    """

    if not target_type or not candidate_type:
        return False

    return (
        target_type.strip().upper()
        != candidate_type.strip().upper()
    )