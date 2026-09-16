from app.services.providers.unsc.downloader import download_unsc_list
from app.services.providers.unsc.parser import parse_unsc_list

from .candidate import SanctionsCandidate
from .candidate_adapter import unsc_record_to_candidate


class UNSCGlobalSanctionsProvider:
    """
    Higher-level Sprint 5 adapter for the existing UNSC official source.

    The existing provider remains untouched. This adapter exposes
    normalized SanctionsCandidate records to the common sanctions engine.
    """

    source_name = "UNSC"
    issuing_country = "GLOBAL"

    def get_candidates(self) -> list[SanctionsCandidate]:
        xml_data = download_unsc_list()

        records = parse_unsc_list(xml_data)

        return [
            unsc_record_to_candidate(record)
            for record in records
            if record.get("name")
        ]