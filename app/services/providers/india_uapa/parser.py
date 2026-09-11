# ============================================================
# INDIA UAPA / MHA LIST PARSER
# ============================================================

from bs4 import BeautifulSoup


def parse_mha_page(
    html_data: bytes,
    subject_type: str
):
    soup = BeautifulSoup(
        html_data,
        "html.parser"
    )

    records = []

    for row in soup.find_all("tr"):

        cells = row.find_all("td")

        if len(cells) < 2:
            continue

        serial_number = cells[0].get_text(
            " ",
            strip=True
        )

        name = cells[1].get_text(
            " ",
            strip=True
        )

        if not serial_number.isdigit():
            continue

        if not name:
            continue

        records.append({
            "uid": f"INDIA-UAPA-{subject_type.upper()}-{serial_number}",
            "name": name,
            "aliases": [],
            "subject_type": subject_type,
            "serial_number": serial_number
        })

    return records


def parse_india_uapa_lists(
    html_data: dict
):
    organisation_records = parse_mha_page(
        html_data[
            "terrorist_organisations"
        ],
        "TERRORIST_ORGANISATION"
    )

    individual_records = parse_mha_page(
        html_data[
            "individual_terrorists"
        ],
        "INDIVIDUAL_TERRORIST"
    )

    return (
        organisation_records
        + individual_records
    )