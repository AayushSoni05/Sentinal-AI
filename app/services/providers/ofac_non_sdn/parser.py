# ============================================================
# OFAC CONSOLIDATED NON-SDN XML PARSER
# ============================================================

import xml.etree.ElementTree as ET


OFAC_XML_NAMESPACE = (
    "https://sanctionslistservice.ofac.treas.gov/"
    "api/PublicationPreview/exports/XML"
)

NS = {
    "ofac": OFAC_XML_NAMESPACE
}


def _text(element, path: str):
    node = element.find(path, NS)

    if node is None or node.text is None:
        return None

    return node.text.strip()


def parse_non_sdn_list(xml_data: bytes):
    root = ET.fromstring(xml_data)

    records = []

    for entry in root.findall(
        ".//ofac:sdnEntry",
        NS
    ):
        uid = _text(
            entry,
            "ofac:uid"
        )

        first_name = _text(
            entry,
            "ofac:firstName"
        )

        last_name = _text(
            entry,
            "ofac:lastName"
        )

        sdn_type = _text(
            entry,
            "ofac:sdnType"
        )

        names = []

        if first_name:
            names.append(first_name)

        if last_name:
            names.append(last_name)

        primary_name = " ".join(names).strip()

        aliases = []

        for alias in entry.findall(
            ".//ofac:aka",
            NS
        ):
            alias_parts = []

            alias_first = _text(
                alias,
                "ofac:firstName"
            )

            alias_last = _text(
                alias,
                "ofac:lastName"
            )

            if alias_first:
                alias_parts.append(
                    alias_first
                )

            if alias_last:
                alias_parts.append(
                    alias_last
                )

            alias_name = (
                " ".join(alias_parts).strip()
            )

            if alias_name:
                aliases.append(
                    alias_name
                )

        records.append({
            "uid": uid,
            "original_name": primary_name,
            "aliases": aliases,
            "sdn_type": sdn_type,
        })

    return records