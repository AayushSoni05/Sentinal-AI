from .candidate import SanctionsCandidate


def unsc_record_to_candidate(
    record: dict,
) -> SanctionsCandidate:
    """
    Convert one normalized UNSC parser record into the
    common Sprint 5 sanctions candidate model.
    """

    identifiers = {}

    for identifier in record.get("identifiers", []):
        id_type = identifier.get("id_type")
        id_number = identifier.get("id_number")

        if id_type and id_number:
            identifiers[id_type] = id_number

    countries = []

    nationality = record.get("nationality")

    if nationality:
        countries.append(nationality)

    dates_of_birth = []

    dob = record.get("dob")

    if dob:
        dates_of_birth.append(dob)

    return SanctionsCandidate(
        source_name="UNSC",
        source_uid=record.get("reference_number"),
        canonical_name=record.get("name", ""),
        aliases=record.get("aliases", []),
        issuing_country="GLOBAL",
        countries=countries,
        dates_of_birth=dates_of_birth,
        entity_type=record.get("subject_type"),
        identifiers=identifiers,
        raw_data=record,
    )