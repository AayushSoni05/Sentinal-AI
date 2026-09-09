# ============================================================
# UN SECURITY COUNCIL CONSOLIDATED LIST PARSER
# ============================================================

import xml.etree.ElementTree as ET


def _local_name(tag: str) -> str:
    """
    Remove XML namespace from a tag.

    Example:
        {http://example.com}FIRST_NAME
        becomes:
        FIRST_NAME
    """

    if "}" in tag:
        return tag.split("}", 1)[1]

    return tag


def _clean_text(value):
    """
    Normalize XML text.
    """

    if value is None:
        return None

    value = value.strip()

    return value if value else None


def _direct_child_text(
    element,
    tag_name: str
):
    """
    Find a direct child using the local XML tag name.
    """

    wanted = tag_name.upper()

    for child in list(element):

        if _local_name(child.tag).upper() == wanted:
            return _clean_text(child.text)

    return None


def _first_descendant_text(
    element,
    tag_names: list[str]
):
    """
    Find the first matching descendant from a list
    of possible tag names.
    """

    wanted = {
        name.upper()
        for name in tag_names
    }

    for child in element.iter():

        if _local_name(child.tag).upper() in wanted:

            value = _clean_text(child.text)

            if value:
                return value

    return None


def _all_descendant_text(
    element,
    tag_names: list[str]
):
    """
    Return all matching descendant text values.
    """

    wanted = {
        name.upper()
        for name in tag_names
    }

    values = []

    for child in element.iter():

        if _local_name(child.tag).upper() in wanted:

            value = _clean_text(child.text)

            if value and value not in values:
                values.append(value)

    return values


def _build_individual_name(element):
    """
    Build the primary individual name from the UNSC
    four-name structure.
    """

    name_parts = []

    for field in [
        "FIRST_NAME",
        "SECOND_NAME",
        "THIRD_NAME",
        "FOURTH_NAME"
    ]:

        value = _direct_child_text(
            element,
            field
        )

        if value:
            name_parts.append(value)

    return " ".join(name_parts)


def _build_entity_name(element):
    """
    Extract the primary entity name.
    """

    for field in [
        "FIRST_NAME",
        "NAME"
    ]:

        value = _direct_child_text(
            element,
            field
        )

        if value:
            return value

    return ""


def _extract_aliases(
    element
):
    """
    Extract aliases from the UNSC record.

    We deliberately collect alias-name fields rather than
    assuming one exact XML nesting structure.
    """

    aliases = []

    for tag_name in [
        "ALIAS_NAME",
        "AKA",
        "ALIAS",
        "LOW_QUALITY_AKA",
        "GOOD_QUALITY_AKA"
    ]:

        for value in _all_descendant_text(
            element,
            [tag_name]
        ):

            if value not in aliases:
                aliases.append(value)

    return aliases


def _extract_identifiers(
    element
):
    """
    Extract passport and national identification data.
    """

    identifiers = []

    passport_numbers = _all_descendant_text(
        element,
        [
            "PASSPORT_NUMBER",
            "PASSPORT_NO"
        ]
    )

    for value in passport_numbers:

        identifiers.append({
            "id_type": "PASSPORT",
            "id_number": value
        })

    national_ids = _all_descendant_text(
        element,
        [
            "NATIONAL_IDENTIFICATION_NUMBER",
            "NATIONAL_ID_NUMBER",
            "NATIONAL_ID_NO"
        ]
    )

    for value in national_ids:

        identifiers.append({
            "id_type": "NATIONAL_ID",
            "id_number": value
        })

    return identifiers


def _extract_common_fields(
    element
):
    """
    Extract common identifying information.
    """

    reference_number = _first_descendant_text(
        element,
        [
            "DATAID",
            "REFERENCE_NUMBER",
            "PERMANENT_REFERENCE_NUMBER"
        ]
    )

    dob = _first_descendant_text(
        element,
        [
            "DATE_OF_BIRTH",
            "DOB"
        ]
    )

    nationality = _first_descendant_text(
        element,
        [
            "NATIONALITY"
        ]
    )

    address = _first_descendant_text(
        element,
        [
            "ADDRESS"
        ]
    )

    listed_on = _first_descendant_text(
        element,
        [
            "LISTED_ON"
        ]
    )

    other_information = _first_descendant_text(
        element,
        [
            "OTHER_INFORMATION"
        ]
    )

    return {
        "reference_number": reference_number,
        "dob": dob,
        "nationality": nationality,
        "address": address,
        "listed_on": listed_on,
        "other_information": other_information
    }


def parse_unsc_list(
    xml_data: bytes
):
    """
    Parse the complete UNSC consolidated XML list.

    Returns:
        List of normalized raw records.
    """

    root = ET.fromstring(xml_data)

    records = []

    for element in root.iter():

        local_name = _local_name(
            element.tag
        ).upper()

        if local_name not in {
            "INDIVIDUAL",
            "ENTITY"
        }:
            continue

        common_fields = _extract_common_fields(
            element
        )

        aliases = _extract_aliases(
            element
        )

        identifiers = _extract_identifiers(
            element
        )

        if local_name == "INDIVIDUAL":

            name = _build_individual_name(
                element
            )

            subject_type = "Individual"

        else:

            name = _build_entity_name(
                element
            )

            subject_type = "LegalEntity"

        if not name:
            continue

        record = {
            "reference_number":
                common_fields["reference_number"],

            "subject_type":
                subject_type,

            "name":
                name,

            "aliases":
                aliases,

            "dob":
                common_fields["dob"],

            "nationality":
                common_fields["nationality"],

            "address":
                common_fields["address"],

            "identifiers":
                identifiers,

            "listed_on":
                common_fields["listed_on"],

            "other_information":
                common_fields["other_information"]
        }

        records.append(record)

    return records