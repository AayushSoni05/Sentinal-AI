# ============================================================
# EU CONSOLIDATED FINANCIAL SANCTIONS XML PARSER
# ============================================================

import xml.etree.ElementTree as ET


def parse_eu_sanctions_list(xml_data: bytes):
    root = ET.fromstring(xml_data)

    records = []

    for entity in root.iter():

        if entity.tag.split("}")[-1] != "sanctionEntity":
            continue

        unique_id = entity.get(
            "euReferenceNumber"
        )

        logical_id = entity.get(
            "logicalId"
        )

        if not unique_id:
            unique_id = logical_id

        if not unique_id:
            continue

        subject_type = None

        for child in entity:

            if child.tag.split("}")[-1] == "subjectType":
                subject_type = child.get(
                    "code"
                )

                break

        names = []
        aliases = []

        for child in entity:

            if child.tag.split("}")[-1] != "nameAlias":
                continue

            whole_name = (
                child.get("wholeName")
                or ""
            ).strip()

            first_name = (
                child.get("firstName")
                or ""
            ).strip()

            middle_name = (
                child.get("middleName")
                or ""
            ).strip()

            last_name = (
                child.get("lastName")
                or ""
            ).strip()

            if whole_name:
                name = whole_name

            else:
                name = " ".join(
                    part
                    for part in [
                        first_name,
                        middle_name,
                        last_name
                    ]
                    if part
                ).strip()

            if not name:
                continue

            if not names:
                names.append(name)

            else:
                aliases.append(name)

        if not names:
            continue

        programme = None

        for child in entity:

            if child.tag.split("}")[-1] != "regulation":
                continue

            programme = child.get(
                "programme"
            )

            if programme:
                break

        designation_date = None

        for child in entity:

            if child.tag.split("}")[-1] == "regulation":
                designation_date = child.get(
                    "publicationDate"
                )

                if designation_date:
                    break

        records.append({
            "uid": unique_id,
            "logical_id": logical_id,
            "name": names[0],
            "aliases": aliases,
            "subject_type": subject_type,
            "designation_date": designation_date,
            "programme": programme
        })

    return records