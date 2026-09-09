from app.services.providers.unsc.downloader import download_unsc_list
from app.services.providers.unsc.parser import parse_unsc_list


xml_data = download_unsc_list()

records = parse_unsc_list(xml_data)

entity_records = [
    record
    for record in records
    if record.get("subject_type") == "LegalEntity"
]

print("TOTAL LEGAL ENTITIES:", len(entity_records))

for record in entity_records[:20]:
    print(
        "NAME:", record.get("name")
    )
    print(
        "ALIASES:", record.get("aliases")
    )
    print(
        "REFERENCE:", record.get("reference_number")
    )
    print(
        "IDENTIFIERS:", record.get("identifiers")
    )
    print("-" * 60)