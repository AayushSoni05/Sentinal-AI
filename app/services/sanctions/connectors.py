from abc import ABC, abstractmethod

from app.services.sanctions.sources import (
    SanctionsSourceDefinition,
    SourceScreeningStatus,
)
from app.services.sanctions.screening import (
    SanctionsCandidate,
    SourceScreeningResult,
)
import requests
import xml.etree.ElementTree as ET

# ============================================================
# CONNECTOR INTERFACE
# ============================================================

class SanctionsSourceConnector(ABC):

    @abstractmethod
    def screen(
        self,
        subject_id: str,
        subject_type: str,
        source: SanctionsSourceDefinition,
    ) -> SourceScreeningResult:
        ...


# ============================================================
# CONNECTOR REGISTRY
# ============================================================

_CONNECTORS: dict[str, SanctionsSourceConnector] = {}


def register_connector(
    connector_type: str,
    connector: SanctionsSourceConnector,
) -> None:
    _CONNECTORS[connector_type] = connector


def get_connector(
    connector_type: str,
) -> SanctionsSourceConnector | None:
    return _CONNECTORS.get(connector_type)

class XMLConnector(SanctionsSourceConnector):
    """Generic connector for XML-based official sanctions sources."""

    def fetch_source(
        self,
        source: SanctionsSourceDefinition,
        timeout: int = 30,
    ) -> tuple[bool, str | None, str | None]:
        try:
            response = requests.get(
                source.official_source_url,
                timeout=timeout,
            )

            response.raise_for_status()

            # Validate that the response is actually XML.
            ET.fromstring(response.content)

            return True, response.text, None

        except requests.RequestException as exc:
            return False, None, f"HTTP/connection error: {exc}"

        except ET.ParseError as exc:
            return False, None, f"Invalid XML response: {exc}"

        except Exception as exc:
            return False, None, f"Unexpected connector error: {exc}"

    def parse_candidates(
        self,
        source: SanctionsSourceDefinition,
        xml_text: str,
    ) -> list[SanctionsCandidate]:
        root = ET.fromstring(xml_text)
        namespace = source.xml_namespace
        if namespace:
            ns = {"src": namespace}
        else:
            ns = {}
        config = source.parser_config

        if not config:
            raise ValueError(
                f"No parser configuration defined for source: {source.source_id}"
            )

        candidates: list[SanctionsCandidate] = []

        # ========================================================
        # PERSON RECORDS
        # ========================================================

        person_config = config.get("person")
        person_path = config.get("record_paths", {}).get("person")

        if person_config and person_path:
            for individual in root.findall(
                person_path if not namespace else person_path.replace(
                    ".//",
                    ".//src:",
                    1,
                ),
                ns,
            ):
                data_id = individual.findtext(person_config["id"])

                name_parts = []

                for tag in person_config.get("name_fields", []):
                    value = individual.findtext(tag)

                    if value and value.strip():
                        name_parts.append(value.strip())

                name = " ".join(name_parts).strip()

                if not name:
                    continue

                aliases = []

                alias_path = person_config.get("alias_path")

                if alias_path:
                    for alias_element in individual.findall(alias_path):
                        if alias_element.text and alias_element.text.strip():
                            aliases.append(alias_element.text.strip())

                nationality = None

                nationality_path = person_config.get("nationality_path")

                if nationality_path:
                    nationality_element = individual.find(nationality_path)

                    if (
                        nationality_element is not None
                        and nationality_element.text
                    ):
                        nationality = nationality_element.text.strip()

                date_of_birth = None

                dob_path = person_config.get("date_of_birth_path")

                if dob_path:
                    dob_element = individual.find(dob_path)

                    if dob_element is not None and dob_element.text:
                        date_of_birth = dob_element.text.strip()

                identifiers = []

                identifier_path = person_config.get("identifier_path")

                if identifier_path:
                    for identifier_element in individual.findall(
                        identifier_path
                    ):
                        if (
                            identifier_element.text
                            and identifier_element.text.strip()
                        ):
                            identifiers.append(
                                identifier_element.text.strip()
                            )

                candidates.append(
                    SanctionsCandidate(
                        source_id=source.source_id,
                        source_uid=(
                            data_id
                            or f"{source.source_id}-{len(candidates)}"
                        ),
                        name=name,
                        aliases=tuple(aliases),
                        entity_type="PERSON",
                        date_of_birth=date_of_birth,
                        nationality=nationality,
                        identifiers=tuple(identifiers),
                        raw_data={
                            "record_type": "INDIVIDUAL",
                        },
                    )
                )

        # ========================================================
        # ENTITY RECORDS
        # ========================================================

        entity_config = config.get("entity")
        entity_path = config.get("record_paths", {}).get("entity")

        if entity_config and entity_path:
            for entity in root.findall(entity_path):
                data_id = entity.findtext(entity_config["id"])

                name = entity.findtext(
                    entity_config["name_fields"][0]
                )

                if not name or not name.strip():
                    continue

                aliases = []

                alias_path = entity_config.get("alias_path")

                if alias_path:
                    for alias_element in entity.findall(alias_path):
                        if alias_element.text and alias_element.text.strip():
                            aliases.append(alias_element.text.strip())

                country = None

                country_path = entity_config.get("country_path")

                if country_path:
                    country_element = entity.find(country_path)

                    if (
                        country_element is not None
                        and country_element.text
                    ):
                        country = country_element.text.strip()

                candidates.append(
                    SanctionsCandidate(
                        source_id=source.source_id,
                        source_uid=(
                            data_id
                            or f"{source.source_id}-{len(candidates)}"
                        ),
                        name=name.strip(),
                        aliases=tuple(aliases),
                        entity_type="ENTITY",
                        country=country,
                        raw_data={
                            "record_type": "ENTITY",
                        },
                    )
                )

        return candidates
    def screen(
        self,
        subject_id: str,
        subject_type: str,
        source: SanctionsSourceDefinition,
    ) -> SourceScreeningResult:
        from datetime import datetime, timezone

        success, data, error = self.fetch_source(source)

        if not success:
            return SourceScreeningResult(
                source_id=source.source_id,
                source_name=source.source_name,
                status=SourceScreeningStatus.UNAVAILABLE,
                checked_at=datetime.now(timezone.utc),
                message=error,
            )

        return SourceScreeningResult(
            source_id=source.source_id,
            source_name=source.source_name,
            status=SourceScreeningStatus.NO_MATCH,
            checked_at=datetime.now(timezone.utc),
            message="Source retrieved successfully; matching not implemented yet.",
        )


xml_connector = XMLConnector()

register_connector("XML", xml_connector)