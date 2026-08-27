# ============================================================
# OFAC SDN XML PARSER
# ============================================================

import xml.etree.ElementTree as ET


OFAC_NAMESPACE = (
    "https://sanctionslistservice.ofac.treas.gov/"
    "api/PublicationPreview/exports/XML"
)


def _get_text(
    element,
    tag_name: str
):
    child = element.find(
        f"{{{OFAC_NAMESPACE}}}{tag_name}"
    )

    if child is None or child.text is None:
        return None

    return child.text.strip()


def parse_sdn_list(
    xml_data: bytes
):
    root = ET.fromstring(xml_data)

    records = []

    for entry in root.findall(
        f".//{{{OFAC_NAMESPACE}}}sdnEntry"
    ):
        uid = _get_text(entry, "uid")
        first_name = _get_text(entry, "firstName")
        last_name = _get_text(entry, "lastName")
        sdn_type = _get_text(entry, "sdnType")

        programs = []

        for program in entry.findall(
            f".//{{{OFAC_NAMESPACE}}}programList/"
            f"{{{OFAC_NAMESPACE}}}program"
        ):
            if program.text:
                programs.append(
                    program.text.strip()
                )

        aliases = []

        for aka in entry.findall(
            f".//{{{OFAC_NAMESPACE}}}akaList/"
            f"{{{OFAC_NAMESPACE}}}aka"
        ):
            aka_first_name = _get_text(
                aka,
                "firstName"
            )

            aka_last_name = _get_text(
                aka,
                "lastName"
            )

            aka_name = " ".join(
                part
                for part in [
                    aka_first_name,
                    aka_last_name
                ]
                if part
            )

            if aka_name:
                aliases.append(aka_name)

        full_name = " ".join(
            part
            for part in [
                first_name,
                last_name
            ]
            if part
        )

        addresses = []

        for address in entry.findall(
            f".//{{{OFAC_NAMESPACE}}}addressList/"
            f"{{{OFAC_NAMESPACE}}}address"
        ):
            address_data = {
                "address1": _get_text(
                    address,
                    "address1"
                ),
                "address2": _get_text(
                    address,
                    "address2"
                ),
                "address3": _get_text(
                    address,
                    "address3"
                ),
                "city": _get_text(
                    address,
                    "city"
                ),
                "state_or_province": _get_text(
                    address,
                    "stateOrProvince"
                ),
                "postal_code": _get_text(
                    address,
                    "postalCode"
                ),
                "country": _get_text(
                    address,
                    "country"
                )
            }

            addresses.append(address_data)

        identifiers = []

        for identifier in entry.findall(
            f".//{{{OFAC_NAMESPACE}}}idList/"
            f"{{{OFAC_NAMESPACE}}}id"
        ):
            identifiers.append({
                "uid": _get_text(
                    identifier,
                    "uid"
                ),
                "id_type": _get_text(
                    identifier,
                    "idType"
                ),
                "id_number": _get_text(
                    identifier,
                    "idNumber"
                )
            })

        records.append({
            "uid": uid,
            "name": full_name,
            "first_name": first_name,
            "last_name": last_name,
            "sdn_type": sdn_type,
            "programs": programs,
            "aliases": aliases,
            "addresses": addresses,
            "identifiers": identifiers,
        })

    return records