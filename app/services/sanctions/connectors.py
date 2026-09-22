from abc import ABC, abstractmethod

from app.services.sanctions.sources import (
    SanctionsSourceDefinition,
    SourceScreeningStatus,
)
from app.services.sanctions.screening import (
    SanctionsCandidate,
    SourceRetrievalResult,
    SourceScreeningResult,
)
import requests
from urllib.parse import urljoin
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup

# ============================================================
# CONNECTOR INTERFACE
# ============================================================

def resolve_data_source_url(
    data_source_url: str | None,
    timeout: tuple[int, int] = (3, 5),
) -> str | None:
    if not data_source_url:
        return None

    try:
        response = requests.get(
            data_source_url,
            timeout=timeout,
        )
        response.raise_for_status()

        content_type = (
            response.headers.get("content-type", "")
            .lower()
        )

        if "text/csv" in content_type:
            return data_source_url

        if "text/html" not in content_type:
            return data_source_url

        soup = BeautifulSoup(
            response.text,
            "html.parser",
        )

        for link in soup.find_all("a", href=True):
            href = link["href"]

            if ".csv" in href.lower():
                return urljoin(
                    data_source_url,
                    href,
                )

        return data_source_url

    except requests.RequestException:
        return data_source_url
    except Exception:
        return data_source_url
class SanctionsSourceConnector(ABC):
    @abstractmethod
    def retrieve(
        self,
        source: SanctionsSourceDefinition,
    ) -> SourceRetrievalResult:
        ...

    @abstractmethod
    def load_candidates(
        self,
        source: SanctionsSourceDefinition,
    ) -> list[SanctionsCandidate]:
        ...
    
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
    ) -> tuple[bytes | None, str | None]:
        source_url = source.data_source_url or source.official_source_url

        if source.data_source_url:
            source_url = resolve_data_source_url(
                source.data_source_url,
            )

        if not source_url:
            return None, "Source URL is not configured"

        try:
            response = requests.get(
                source_url,
                timeout=timeout,
            )
            response.raise_for_status()

            content = response.content

            ET.fromstring(content)

            return content, None

        except requests.RequestException as exc:
            return None, str(exc)

        except ET.ParseError as exc:
            return None, f"Invalid XML source: {exc}"

        except Exception as exc:
            return None, str(exc)

    def parse_candidates(
        self,
        source: SanctionsSourceDefinition,
        xml_text: str,
    ) -> list[SanctionsCandidate]:
        root = ET.fromstring(xml_text)

        config = source.parser_config

        if not config:
            raise ValueError(
                f"No parser configuration defined for source: {source.source_id}"
            )

        namespace = source.xml_namespace

        if namespace:
            namespaces = {"src": namespace}
        else:
            namespaces = {}

        def qualified_path(path: str) -> str:
            if not namespace:
                return path

            if path.startswith(".//"):
                parts = path[3:].split("/")
                return ".//" + "/".join(
                    f"src:{part}" for part in parts
                )

            parts = path.split("/")

            return "/".join(
                f"src:{part}" for part in parts
            )

        def find_text(element, path: str) -> str | None:
            return element.findtext(
                qualified_path(path),
                default=None,
                namespaces=namespaces,
            )

        def find_element(element, path: str):
            return element.find(
                qualified_path(path),
                namespaces=namespaces,
            )

        def find_elements(element, path: str):
            return element.findall(
                qualified_path(path),
                namespaces=namespaces,
            )

        def build_name(
            element,
            fields: list[str],
        ) -> str:
            parts = []

            for field in fields:
                value = find_text(element, field)

                if value and value.strip():
                    parts.append(value.strip())

            return " ".join(parts).strip()

        def extract_aliases(
            element,
            alias_config: dict | None,
        ) -> tuple[str, ...]:
            if not alias_config:
                return ()

            alias_record_path = alias_config.get("record_path")
            alias_name_fields = alias_config.get("name_fields", [])

            if not alias_record_path:
                return ()

            aliases = []

            for alias_record in find_elements(
                element,
                alias_record_path,
            ):
                alias_name = build_name(
                    alias_record,
                    alias_name_fields,
                )

                if alias_name:
                    aliases.append(alias_name)

            return tuple(aliases)

        def extract_first_text(
            element,
            path: str | None,
        ) -> str | None:
            if not path:
                return None

            values = find_elements(
                element,
                path,
            )

            for value_element in values:
                if value_element.text and value_element.text.strip():
                    return value_element.text.strip()

            value_element = find_element(
                element,
                path,
            )

            if value_element is not None and value_element.text:
                return value_element.text.strip()

            return None

        def extract_identifiers(
            element,
            identifier_config,
        ) -> tuple[str, ...]:
            if not identifier_config:
                return ()

            if isinstance(identifier_config, str):
                identifiers = []

                for identifier_element in find_elements(
                    element,
                    identifier_config,
                ):
                    if (
                        identifier_element.text
                        and identifier_element.text.strip()
                    ):
                        identifiers.append(
                            identifier_element.text.strip()
                        )

                return tuple(identifiers)

            record_path = identifier_config.get("record_path")
            type_path = identifier_config.get("type_path")
            value_path = identifier_config.get("value_path")

            allowed_types = set(
                identifier_config.get("allowed_types", [])
            )

            if not record_path or not value_path:
                return ()

            identifiers = []

            for record in find_elements(
                element,
                record_path,
            ):
                identifier_type = (
                    find_text(record, type_path)
                    if type_path
                    else None
                )

                if (
                    allowed_types
                    and identifier_type not in allowed_types
                ):
                    continue

                value = find_text(
                    record,
                    value_path,
                )

                if value and value.strip():
                    identifiers.append(value.strip())

            return tuple(identifiers)

        candidates: list[SanctionsCandidate] = []

        # ========================================================
        # UNIFIED RECORD SOURCES
        # Example: OFAC sdnEntry + sdnType
        # ========================================================

        record_config = config.get("records")

        if record_config:
            record_path = record_config["path"]
            type_path = record_config["type_path"]

            record_type_mapping = record_config.get(
                "record_type_mapping",
                {},
            )

            for record in find_elements(
                root,
                record_path,
            ):
                record_type = find_text(
                    record,
                    type_path,
                )

                if record_type not in record_type_mapping:
                    continue

                entity_type = record_type_mapping[record_type]

                subject_config = config.get(
                    entity_type.lower()
                )

                if not subject_config:
                    continue

                data_id = find_text(
                    record,
                    subject_config["id"],
                )

                name = build_name(
                    record,
                    subject_config.get(
                        "name_fields",
                        [],
                    ),
                )

                if not name:
                    continue

                aliases = extract_aliases(
                    record,
                    subject_config.get("alias"),
                )

                date_of_birth = extract_first_text(
                    record,
                    subject_config.get(
                        "date_of_birth_path"
                    ),
                )

                identifier_config = subject_config.get(
                    "identifier",
                    subject_config.get(
                        "identifier_path"
                    ),
                )

                identifiers = extract_identifiers(
                    record,
                    identifier_config,
                )

                country = extract_first_text(
                    record,
                    subject_config.get(
                        "country_path"
                    ),
                )

                candidates.append(
                    SanctionsCandidate(
                        source_id=source.source_id,
                        source_uid=(
                            data_id
                            or f"{source.source_id}-{len(candidates)}"
                        ),
                        name=name,
                        aliases=aliases,
                        entity_type=entity_type,
                        date_of_birth=date_of_birth,
                        country=country,
                        identifiers=identifiers,
                        raw_data={
                            "record_type": record_type,
                        },
                    )
                )

            return candidates

        # ========================================================
        # SEPARATE PERSON / ENTITY RECORD SOURCES
        # Example: UNSC
        # ========================================================

        person_config = config.get("person")
        person_path = config.get(
            "record_paths",
            {},
        ).get("person")

        if person_config and person_path:
            for individual in find_elements(
                root,
                person_path,
            ):
                data_id = find_text(
                    individual,
                    person_config["id"],
                )

                name = build_name(
                    individual,
                    person_config.get("name_fields", []),
                )

                if not name:
                    continue

                aliases = extract_aliases(
                    individual,
                    person_config.get("alias"),
                )

                if not aliases:
                    old_alias_path = person_config.get(
                        "alias_path"
                    )

                    if old_alias_path:
                        aliases = tuple(
                            alias.text.strip()
                            for alias in find_elements(
                                individual,
                                old_alias_path,
                            )
                            if alias.text
                            and alias.text.strip()
                        )

                nationality = extract_first_text(
                    individual,
                    person_config.get(
                        "nationality_path"
                    ),
                )

                date_of_birth = extract_first_text(
                    individual,
                    person_config.get(
                        "date_of_birth_path"
                    ),
                )

                identifiers = extract_identifiers(
                    individual,
                    person_config.get(
                        "identifier_path"
                    ),
                )

                candidates.append(
                    SanctionsCandidate(
                        source_id=source.source_id,
                        source_uid=(
                            data_id
                            or f"{source.source_id}-{len(candidates)}"
                        ),
                        name=name,
                        aliases=aliases,
                        entity_type="PERSON",
                        date_of_birth=date_of_birth,
                        nationality=nationality,
                        identifiers=identifiers,
                        raw_data={
                            "record_type": "INDIVIDUAL",
                        },
                    )
                )

        entity_config = config.get("entity")
        entity_path = config.get(
            "record_paths",
            {},
        ).get("entity")

        if entity_config and entity_path:
            for entity in find_elements(
                root,
                entity_path,
            ):
                data_id = find_text(
                    entity,
                    entity_config["id"],
                )

                name = build_name(
                    entity,
                    entity_config.get("name_fields", []),
                )

                if not name:
                    continue

                aliases = extract_aliases(
                    entity,
                    entity_config.get("alias"),
                )

                if not aliases:
                    old_alias_path = entity_config.get(
                        "alias_path"
                    )

                    if old_alias_path:
                        aliases = tuple(
                            alias.text.strip()
                            for alias in find_elements(
                                entity,
                                old_alias_path,
                            )
                            if alias.text
                            and alias.text.strip()
                        )

                country = extract_first_text(
                    entity,
                    entity_config.get(
                        "country_path"
                    ),
                )

                candidates.append(
                    SanctionsCandidate(
                        source_id=source.source_id,
                        source_uid=(
                            data_id
                            or f"{source.source_id}-{len(candidates)}"
                        ),
                        name=name,
                        aliases=aliases,
                        entity_type="ENTITY",
                        country=country,
                        raw_data={
                            "record_type": "ENTITY",
                        },
                    )
                )

        return candidates

    def retrieve(
        self,
        source: SanctionsSourceDefinition,
    ) -> SourceRetrievalResult:
        from datetime import datetime, timezone

        success, _, error = self.fetch_source(source)

        return SourceRetrievalResult(
            source_id=source.source_id,
            source_name=source.source_name,
            available=success,
            checked_at=datetime.now(timezone.utc),
            message=error,
        )

    def load_candidates(
        self,
        source: SanctionsSourceDefinition,
    ) -> list[SanctionsCandidate]:
        success, xml_text, error = self.fetch_source(source)

        if not success:
            raise RuntimeError(
                error or f"Unable to retrieve source: {source.source_id}"
            )

        if xml_text is None:
            raise RuntimeError(
                f"Source returned no XML data: {source.source_id}"
            )

        return self.parse_candidates(
            source=source,
            xml_text=xml_text,
        )
    
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
            screening_completed=False,
            message="Source retrieved successfully; matching not implemented yet.",
        )

class CSVConnector(SanctionsSourceConnector):
    """Generic connector for CSV-based sanctions sources."""

    def fetch_source(
        self,
        source: SanctionsSourceDefinition,
        timeout: int = 30,
    ) -> tuple[str | None, str | None]:
        source_url = source.data_source_url or source.official_source_url

        if source.data_source_url:
            resolved_url = resolve_data_source_url(
                source.data_source_url,
            )

            if resolved_url:
                source_url = resolved_url

        if not source_url:
            return None, "Source URL is not configured"

        try:
            response = requests.get(
                source_url,
                timeout=timeout,
            )
            response.raise_for_status()

            return response.content.decode("utf-8-sig"), None

        except requests.RequestException as exc:
            return None, str(exc)

        except Exception as exc:
            return None, str(exc)

    def retrieve(
        self,
        source: SanctionsSourceDefinition,
    ) -> SourceRetrievalResult:
        from datetime import datetime, timezone

        success, _, error = self.fetch_source(source)

        return SourceRetrievalResult(
            source_id=source.source_id,
            source_name=source.source_name,
            available=success is not None,
            checked_at=datetime.now(timezone.utc),
            message=error,
        )

    def load_candidates(
        self,
        source: SanctionsSourceDefinition,
    ) -> list[SanctionsCandidate]:
        raise NotImplementedError(
            "CSV candidate parsing is not implemented yet."
        )

    def screen(
        self,
        subject_id: str,
        subject_type: str,
        source: SanctionsSourceDefinition,
    ) -> SourceScreeningResult:
        from datetime import datetime, timezone

        success, _, error = self.fetch_source(source)

        if success is None:
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
            screening_completed=False,
            message="Source retrieved successfully; matching not implemented yet.",
        )

xml_connector = XMLConnector()

register_connector("XML", XMLConnector())
register_connector("CSV", CSVConnector())