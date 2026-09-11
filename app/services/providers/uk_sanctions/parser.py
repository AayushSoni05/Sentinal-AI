# ============================================================
# UK SANCTIONS LIST XML PARSER
# ============================================================

import xml.etree.ElementTree as ET


def _local_name(tag: str) -> str:
    if "}" in tag:
        return tag.split("}", 1)[1]

    return tag


def _text(element):
    if element is None or element.text is None:
        return None

    value = element.text.strip()

    return value if value else None


def _child_text(element, field_name: str):
    for child in element.iter():
        if _local_name(child.tag) == field_name:
            return _text(child)

    return None


def _child_values(element, field_name: str):
    values = []

    for child in element.iter():
        if _local_name(child.tag) == field_name:
            value = _text(child)

            if value:
                values.append(value)

    return values


def parse_uk_sanctions_list(xml_data: bytes):
    root = ET.fromstring(xml_data)

    records = []

    for element in root.iter():

        if _local_name(element.tag) not in {
            "Designation",
            "FinancialSanctionsTarget"
        }:
            continue

        unique_id = _child_text(
            element,
            "UniqueID"
        )

        if not unique_id:
            continue

        name_parts = []

        for field in [
            "Name1",
            "Name2",
            "Name3",
            "Name4",
            "Name5",
            "Name6"
        ]:
            value = _child_text(
                element,
                field
            )

            if value:
                name_parts.append(value)

        records.append({
            "unique_id": unique_id,
            "name": " ".join(name_parts).strip(),
            "name_type": _child_text(
                element,
                "NameType"
            ),
            "aliases": _child_values(
                element,
                "Name"
            ),
            "regime_name": _child_text(
                element,
                "RegimeName"
            ),
            "subject_type": _child_text(
                element,
                "GroupTypeDescription"
            ),
        })

    return records