import xml.etree.ElementTree as ET

from app.services.providers.ofac.downloader import download_sdn_list


xml_data = download_sdn_list()
root = ET.fromstring(xml_data)

ns = "https://sanctionslistservice.ofac.treas.gov/api/PublicationPreview/exports/XML"

found = 0

for entry in root.iter(
    f"{{{ns}}}sdnEntry"
):

    id_list = entry.find(
        f"{{{ns}}}idList"
    )

    if id_list is None:
        continue

    print(
        "NAME:",
        entry.findtext(
            f"{{{ns}}}lastName"
        )
    )

    print(
        ET.tostring(
            id_list,
            encoding="unicode"
        )[:2000]
    )

    print("---")

    found += 1

    if found >= 3:
        break

print("FOUND:", found)